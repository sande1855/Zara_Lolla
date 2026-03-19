import streamlit as st
import pandas as pd
from serpapi import GoogleSearch

# 1. Page Config
st.set_page_config(page_title="Lisa Frank x Zara Larsson", layout="wide")

if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# 2. Lisa Frank Aesthetic Styling (Updated for better visibility)
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
        width: 100%;
    }
    img {
        border: 4px solid #FFD700;
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Smart Filters
st.sidebar.title("🌈 Style Wizard")

# Base Category (Always used)
category = st.sidebar.selectbox("Core Item", [
    "Ruffle Skirt", "Butterfly Top", "Mesh Dress", "Baby Tee", "Sequin Set"
])

# Optional Boosts (These only add to the search if selected)
use_color = st.sidebar.checkbox("Filter by Color?", value=False)
color_theme = st.sidebar.selectbox("Color Palette", ["Neon Pink", "Electric Blue", "Sunset Orange", "Silver"], disabled=not use_color)

use_brands = st.sidebar.checkbox("Filter by Brand?", value=False)
brand_list = st.sidebar.multiselect("Retailers", ["Revolve", "ASOS", "Urban Outfitters", "Nordstrom"], default=["Revolve"], disabled=not use_brands)

max_price = st.sidebar.slider("Max Price ($)", 10, 500, 200)

# 4. Search Logic (The "Anti-Limiting" Fix)
def fetch_style_results():
    # Start with a strong base aesthetic query
    query_parts = [category, "Zara Larsson tour style", "Y2K festival"]
    
    # Add optional filters only if checked
    if use_color:
        query_parts.append(color_theme)
    
    if use_brands and brand_list:
        brand_sites = " OR ".join([f"site:{b.lower().replace(' ', '')}.com" for b in brand_list])
        query_parts.append(f"({brand_sites})")
    
    full_query = " ".join(query_parts)
    
    params = {
        "engine": "google_shopping",
        "q": full_query,
        "location": "United States",
        "api_key": st.secrets["SERP_API_KEY"]
    }
    
    try:
        search = GoogleSearch(params)
        return search.get_dict().get("shopping_results", [])
    except Exception as e:
        st.error(f"Search failed: {e}")
        return []

# 5. Main Display
st.title("☀️ Midnight Sun Style")

if st.sidebar.button("GLITTER SEARCH"):
    items = fetch_style_results()
    
    if items:
        cols = st.columns(3)
        # Filter results by price manually to ensure the slider always works
        filtered_items = [i for i in items if float(i.get('price', '$1000').replace('$', '').replace(',', '')) <= max_price]
        
        if not filtered_items:
            st.warning("Found items, but they are all above your price limit! Try sliding the budget up.")
        
        for i, item in enumerate(filtered_items[:12]):
            with cols[i % 3]:
                st.image(item.get('thumbnail'), use_container_width=True)
                st.write(f"**{item.get('title')[:40]}**")
                st.write(f"{item.get('price')} at {item.get('source')}")
                if st.button("💖 Save", key=f"fav_{i}"):
                    st.session_state.favorites.append(item)
                    st.toast("Saved to collection!")
                st.link_button("Shop", item.get('link'))
    else:
        st.error("No results found. Try unchecking the Brand or Color filters to broaden the search!")

# 6. Favorites
if st.session_state.favorites:
    st.divider()
    st.header("🦄 Your Sticker Book")
    fav_cols = st.columns(6)
    for idx, fav in enumerate(st.session_state.favorites):
        with fav_cols[idx % 6]:
            st.image(fav.get('thumbnail'), width=100)
