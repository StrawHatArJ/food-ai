import streamlit as st
import requests
import google.generativeai as genai

st.set_page_config(page_title="AI Food Analyzer", page_icon="🍎")

st.sidebar.header("⚙️ Settings")
api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Enter your free Google Gemini API key to enable WHO AI Analysis.")
if api_key:
    genai.configure(api_key=api_key)

usda_key_input = st.sidebar.text_input("USDA API Key (Optional)", type="password", help="USDA DEMO_KEY is rate limited to 30 requests/hour. Get a free one at fdc.nal.usda.gov to bypass this!")
active_usda_key = usda_key_input if usda_key_input else "DEMO_KEY"

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_usda_data(query, key):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={query}&dataType=Branded&pageSize=1&api_key=IuQdhlSX2AbpcVfXcv1Sj244jyTNDBqcq04TP7iW"
    response = requests.get(url, timeout=10)
    return response.status_code, response.json() if response.status_code == 200 else {}

@st.cache_data(ttl=3600, show_spinner=False)
def analyze_ingredients_with_ai(ingredients_text, _api_key):
    # Dynamically find an available model for the user's API key to prevent 404 errors
    model_name = "gemini-2.5-flash"
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if available:
            flash_models = [m for m in available if "flash" in m]
            model_name = flash_models[0] if flash_models else available[0]
            # Strip "models/" prefix if present, as GenerativeModel sometimes doubles it
            model_name = model_name.replace("models/", "")
    except Exception:
        pass
        
    model = genai.GenerativeModel(model_name)
    prompt = f"""
    You are an expert nutritionist and health AI. Analyze the following ingredients for a packaged food item against the World Health Organization (WHO) dietary guidelines.
    
    Ingredients: {ingredients_text}
    
    Please provide the output EXACTLY as a Markdown table with the following columns:
    | Ingredient | Purpose | WHO Guideline / Limit | Long-Term Side Effect |
    
    Only include ingredients that have notable guidelines (like sugars, sodium, specific preservatives, unhealthy fats), health impacts, or side effects. Consolidate benign ingredients or skip them.
    Ensure the output is ONLY the markdown table and no other conversational text.
    """
    response = model.generate_content(prompt)
    return response.text

st.title("AI Food Analyzer 🍎")
st.write("Welcome to your intelligent food analyzer! Enter a packaged food name below to fetch its ingredients.")

food_query = st.text_input("Packaged Food Name", placeholder="e.g., Nutella, Oreo")

if st.button("Analyze Food"):
    if food_query:
        with st.spinner(f"Searching for **{food_query}** using USDA FoodData Central..."):
            try:
                status_code, data = fetch_usda_data(food_query, active_usda_key)
                
                if status_code == 200:
                    foods = data.get("foods", [])
                    if foods and len(foods) > 0:
                        top_product = foods[0]
                        product_name = top_product.get("description", "Unknown Product")
                        ingredients = top_product.get("ingredients", "")
                        
                        st.success(f"Successfully found data for: **{product_name}**")
                        st.subheader("Ingredients:")
                        if ingredients and ingredients.strip() != "":
                            clean_ingredients = ingredients.replace(", ", " • ")
                            st.info(clean_ingredients)
                            
                            st.subheader("🏥 WHO Guideline Analysis")
                            if not api_key:
                                st.warning("Please enter your Gemini API Key in the sidebar to view the AI analysis table.")
                            else:
                                with st.spinner("Analyzing ingredients with Google Gemini AI..."):
                                    try:
                                        table_output = analyze_ingredients_with_ai(clean_ingredients, api_key)
                                        st.markdown(table_output)
                                    except Exception as e:
                                        st.error(f"Failed to generate AI analysis: {str(e)}")
                        else:
                            st.warning("No specific ingredients list found for this product.")
                    else:
                        st.error(f"Could not find any products matching '{food_query}' in the USDA database. Try a more specific known brand.")
                elif status_code == 429:
                    st.error("🚨 USDA API Rate Limit Exceeded. If using the default demo key, please enter your own API key in the sidebar.")
                else:
                    st.error(f"There was an error connecting to the USDA API (Status Code: {status_code}).")
            except Exception as e:
                st.error(f"Network error occurred: {str(e)}")
    else:
        st.error("Please enter a food name to analyze.")

