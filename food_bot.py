import streamlit as st
import requests

st.set_page_config(page_title="AI Food Analyzer", page_icon="🍎")

st.title("AI Food Analyzer 🍎")
st.write("Welcome to your intelligent food analyzer! Enter a packaged food name below to fetch its ingredients.")

food_query = st.text_input("Packaged Food Name", placeholder="e.g., Nutella, Oreo")

if st.button("Analyze Food"):
    if food_query:
        with st.spinner(f"Searching for **{food_query}** using Open Food Facts API..."):
            url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={food_query}&search_simple=1&action=process&json=1"
            response = requests.get(url, headers={'User-Agent': 'AIFoodAnalyzer/1.0'})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("products") and len(data["products"]) > 0:
                    top_product = data["products"][0]
                    
                    product_name = top_product.get("product_name", "Unknown Product")
                    ingredients = top_product.get("ingredients_text", "")
                    
                    st.success(f"Successfully found data for: **{product_name}**")
                    st.subheader("Ingredients:")
                    if ingredients and ingredients.strip() != "":
                        st.info(ingredients)
                    else:
                        st.warning("No specific ingredients list found for this product.")
                else:
                    st.error(f"Could not find any products matching '{food_query}' in the Open Food Facts database. Try a more specific known brand.")
            else:
                st.error("There was an error connecting to the Open Food Facts API. Please try again later.")
    else:
        st.error("Please enter a food name to analyze.")
