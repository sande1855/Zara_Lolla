import streamlit as st
import pandas as pd
from serpapi import GoogleSearch

# 1. Page Config & State
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
        width: 100%;
    }
    img {
        border: 4px solid #FFD700;
        border-radius: 20px;
        transition: 0.3s;
    }
    img:hover { transform: scale(1.02); box-shadow: 0 0 15px #FF00FF; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Adaptive Filters
st.sidebar.title("🌈 Style Wizard")

# Multi-select category to avoid limiting to one product type
categories = st.sidebar.multiselect(
    "Styles to Include", 
    ["Ruffle Skirt", "Butterfly Top", "Mesh Dress", "Baby Tee", "Sequin Set", "Metallic Boots"],
    default=["Ruffle Skirt", "Butterfly Top"]
)

# Optional Retailer Filter
use_retailers = st.sidebar.checkbox("Limit to Specific Stores?", value=False)
selected_brands = []
if use_retailers:
    selected_brands = st.sidebar.multiselect(
        "Select Trusted Retailers", 
        ["Revolve", "ASOS", "Urban Outfitters", "Nordstrom", "Free People"],
        default=["Revolve", "ASOS"]
    )

max_price = st.sidebar.slider("Max Price ($)", 20, 1000, 250)

# 4. Search Logic
def fetch_multi_category_results():
    # Build a broader query to ensure variety
    cat_query = " OR ".join(categories) if categories else "Zara Larsson tour outfits"
    brand_query = ""
    if use_retailers and selected_brands:
        brand_sites = " OR ".join([f"site:{b.lower().replace(' ', '')}.com" for b in selected_brands])
        brand_query = f"({brand_sites})"
    
    full_query = f"{cat_query} {brand_query} Cyber Y2K Scandinavian Barbie aesthetic"
    
    params = {
        "engine": "google_shopping",
        "q": full_query,
        "location": "United States",
        "gl": "us",
        "hl": "en",
        "api_key": st.secrets["SERP_API_KEY"]
    }
    
    try:
        search = GoogleSearch(params)
        return search.get_dict().get("shopping_results", [])
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

# 5. Main Content
st.title("☀️ Midnight Sun Style Finder")

if st.sidebar.button("GLITTER SEARCH"):
    results = fetch_multi_category_results()
    
    if results:
        # Filter by price and ensure product has a name/link
        valid_items = []
        for item in results:
            price_str = item.get('price', '$0').replace('$', '').replace(',', '')
            try:
                price_val = float(price_str)
                if price_val <= max_price and item.get('title') and item.get('link'):
                    valid_items.append(item)
            except:
                continue
        
        if not valid_items:
            st.warning("No items found matching those filters. Try broadening your budget or retailers!")
        else:
            cols = st.columns(3)
            for i, item in enumerate(valid_items[:15]): # Show up to 15 items
                with cols[i % 3]:
                    st.image(item.get('thumbnail'), use_container_width=True)
                    st.subheader(item.get('title')[:50] + "...")
                    st.write(f"**Price:** {item.get('price')}")
                    st.write(f"**Store:** {item.get('source')}")
                    
                    # Display sizes if available in the API response snippet
                    extensions = item.get('extensions', [])
                    if extensions:
                        st.caption(f"Details: {', '.join(extensions)}")
                    
                    st.link_button("Shop This Look", item.get('link'))
                    
                    if st.button("💖 Save", key=f"fav_{i}"):
                        st.session_state.favorites.append(item)
                        st.toast("Added to stickers!")
    else:
        st.error("The search returned nothing. Check your API key or connection.")

# 6. Favorites
if st.session_state.favorites:
    st.divider()
    st.header("🦄 Your Sticker Book")
    f_cols = st.columns(6)
    for idx, fav in enumerate(st.session_state.favorites):
        with f_cols[idx % 6]:
            st.image(fav.get('thumbnail'), width=100)
            st.caption(fav.get('price'))
