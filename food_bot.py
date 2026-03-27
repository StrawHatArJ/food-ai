import streamlit as st
import requests

st.set_page_config(page_title="AI Food Analyzer", page_icon="🍎")

st.title("AI Food Analyzer 🍎")
st.write("Welcome to your intelligent food analyzer! Enter a packaged food name below to fetch its ingredients.")

food_query = st.text_input("Packaged Food Name", placeholder="e.g., Nutella, Oreo")

if st.button("Analyze Food"):
    if food_query:
        with st.spinner(f"Searching for **{food_query}** using USDA FoodData Central..."):
            try:
                # We migrated to USDA FoodData Central API because Open Food Facts was unstable globally
                url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_query}&dataType=Branded&pageSize=1&api_key=DEMO_KEY"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    foods = data.get("foods", [])
                    if foods and len(foods) > 0:
                        top_product = foods[0]
                        
                        # USDA JSON structure uses 'description' and 'ingredients'
                        product_name = top_product.get("description", "Unknown Product")
                        ingredients = top_product.get("ingredients", "")
                        
                        st.success(f"Successfully found data for: **{product_name}**")
                        st.subheader("Ingredients:")
                        if ingredients and ingredients.strip() != "":
                            # Clean up the string slightly for better readability
                            clean_ingredients = ingredients.replace(", ", " • ")
                            st.info(clean_ingredients)
                        else:
                            st.warning("No specific ingredients list found for this product.")
                    else:
                        st.error(f"Could not find any products matching '{food_query}' in the USDA database. Try a more specific known brand.")
                elif response.status_code == 429:
                    st.error("🚨 USDA API Demo Rate Limit Exceeded. Please try again soon.")
                else:
                    st.error(f"There was an error connecting to the USDA API (Status Code: {response.status_code}).")
            except Exception as e:
                st.error(f"Network error occurred: {str(e)}")
    else:
        st.error("Please enter a food name to analyze.")
