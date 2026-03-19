import streamlit as st
import pandas as pd
from serpapi import GoogleSearch

# 1. Page Config
st.set_page_config(page_title="Zara Larsson Midnight Sun Finder", layout="wide")

if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# 2. Lisa Frank / Midnight Sun Custom CSS
st.markdown("""
    <style>
    .main .block-container h1 {
        background: linear-gradient(to right, #FF00FF, #00FFFF, #FFD700, #FF69B4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        font-weight: 900;
        font-size: 3.5rem;
        text-align: center;
    }
    [data-testid="stSidebar"] {
        background-image: linear-gradient(#6EF7F7, #FFD700);
        border-right: 5px solid #FF00FF;
    }
    div.stButton > button:first-child {
        background-color: #FF00FF;
        color: white;
        border-radius: 50px;
        border: 4px solid #00FFFF;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Optional Filters
st.sidebar.title("🌈 Style Wizard")

# Multi-select to allow varied product types
product_types = st.sidebar.multiselect(
    "Include Categories", 
    ["Ruffle Skirt", "Mesh Dress", "Butterfly Top", "Airbrush Tee", "Sequin Set"],
    default=["Ruffle Skirt", "Mesh Dress"]
)

use_retailers = st.sidebar.checkbox("Filter by Retailer?", value=False)
retailer_list = []
if use_retailers:
    retailer_list = st.sidebar.multiselect("Stores", ["Revolve", "ASOS", "Urban Outfitters", "Nordstrom"])

max_price = st.sidebar.slider("Max Price ($)", 20, 500, 150)

# 4. Search Logic (The "Anti-Empty" Fix)
def fetch_style_results():
    # Use aesthetic keywords instead of just the artist's name
    aesthetic = "Cyber Y2K Scandinavian Barbie"
    category_query = " OR ".join(product_types) if product_types else "festival outfit"
    
    query = f"{category_query} {aesthetic} tropical neon"
    
    if use_retailers and retailer_list:
        brand_sites = " OR ".join([f"site:{r.lower().replace(' ', '')}.com" for r in retailer_list])
        query += f" ({brand_sites})"
    
    params = {
        "engine": "google_shopping",
        "q": query,
        "location": "United States",
        "api_key": st.secrets["SERP_API_KEY"]
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict().get("shopping_results", [])
        return results
    except Exception as e:
        st.error(f"Search failed: {e}")
        return []

# 5. Main Display
st.title("☀️ Midnight Sun Style")

if st.sidebar.button("GLITTER SEARCH"):
    items = fetch_style_results()
    
    if items:
        # Filter by price manually to ensure the slider always works
        filtered = []
        for item in items:
            p_str = item.get('price', '$1000').replace('$', '').replace(',', '')
            try:
                if float(p_str) <= max_price:
                    filtered.append(item)
            except:
                continue
        
        if not filtered:
            st.warning("Found items, but they exceed your budget! Try raising the slider.")
        else:
            cols = st.columns(3)
            for idx, item in enumerate(filtered[:15]):
                with cols[idx % 3]:
                    st.image(item.get('thumbnail'), use_container_width=True)
                    st.write(f"**{item.get('title')[:45]}...**")
                    st.write(f"{item.get('price')} @ {item.get('source')}")
                    
                    # Size details if the API provides them
                    if 'extensions' in item:
                        st.caption(f"Sizes/Info: {', '.join(item['extensions'])}")
                    
                    # Fix for the Link Error: Ensure link exists
                    shop_url = item.get('link')
                    if shop_url:
                        st.link_button("View on Site", shop_url)
                    else:
                        st.write("*(Direct link unavailable)*")
    else:
        st.error("Still no results! Try unchecking 'Filter by Retailer' for a broader search.")
