import streamlit as st
import pandas as pd
from serpapi import GoogleSearch

# 1. Page Config
st.set_page_config(page_title="Lisa Frank x Zara Larsson", layout="wide")

if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# 2. Lisa Frank Aesthetic Styling
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
    img {
        border: 4px solid #FFD700;
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Smart Filters
st.sidebar.title("🌈 Style Wizard")

category = st.sidebar.selectbox("Core Item", [
    "Ruffle Skirt", "Butterfly Top", "Mesh Dress", "Baby Tee", "Sequin Set"
])

# Toggle for filtering
use_filters = st.sidebar.checkbox("Apply Strict Filters?", value=False)

if use_filters:
    color_theme = st.sidebar.selectbox("Color Palette", ["Neon Pink", "Electric Blue", "Sunset Orange", "Silver"])
    brand_list = st.sidebar.multiselect("Retailers", ["Revolve", "ASOS", "Urban Outfitters", "Nordstrom"])
else:
    color_theme = ""
    brand_list = []

max_price = st.sidebar.slider("Max Price ($)", 10, 500, 250)

# 4. Search Logic
def fetch_style_results():
    # Base query for the Zara Larsson "Midnight Sun" vibe
    query = f"Zara Larsson tour style {category} {color_theme} Y2K festival"
    
    # Add brands only if selected
    if brand_list:
        brand_sites = " OR ".join([f"site:{b.lower().replace(' ', '')}.com" for b in brand_list])
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
        st.error(f"API Connection Error: {e}")
        return []

# 5. Main Display
st.title("☀️ Midnight Sun Style")

if st.sidebar.button("GLITTER SEARCH"):
    items = fetch_style_results()
    
    if items:
        # Filter by price manually (SerpApi price can be a string like "$45.00")
        filtered_items = []
        for item in items:
            raw_price = item.get('price', '0').replace('$', '').replace(',', '')
            try:
                if float(raw_price) <= max_price:
                    filtered_items.append(item)
            except ValueError:
                filtered_items.append(item) # Keep it if price is weirdly formatted
        
        if not filtered_items:
            st.warning("No items found under that price. Try increasing your budget!")
        else:
            cols = st.columns(3)
            for i, item in enumerate(filtered_items[:12]):
                with cols[i % 3]:
                    st.image(item.get('thumbnail', ''), use_container_width=True)
                    st.write(f"**{item.get('title', 'Clothing Item')[:40]}**")
                    st.write(f"{item.get('price', 'Price N/A')} at {item.get('source', 'Store')}")
                    
                    # ERROR FIX: Check if link exists before making button
                    item_link = item.get('link')
                    if item_link:
                        st.link_button("Shop Now", item_link)
                    else:
                        st.write("*(Link unavailable)*")
                    
                    if st.button("💖 Save", key=f"fav_{i}"):
                        st.session_state.favorites.append(item)
                        st.toast("Saved!")
    else:
        st.error("No results found. Try turning off 'Strict Filters' in the sidebar!")

# 6. Favorites
if st.session_state.favorites:
    st.divider()
    st.header("🦄 Your Sticker Book")
    fav_cols = st.columns(6)
    for idx, fav in enumerate(st.session_state.favorites):
        with fav_cols[idx % 6]:
            st.image(fav.get('thumbnail', ''), width=100)
