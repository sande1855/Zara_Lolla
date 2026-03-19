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
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px #FF00FF;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Filters
st.sidebar.title("🌈 Midnight Sun Wizard")

# Diversity of product types
product_categories = st.sidebar.multiselect(
    "Choose Your Vibe", 
    ["Asymmetrical Ruffle Skirt", "Hibiscus Mesh Dress", "Butterfly Crop Top", "Airbrush Baby Tee", "Sequin Festival Set"],
    default=["Asymmetrical Ruffle Skirt", "Hibiscus Mesh Dress"]
)

# Optional Retailer Filter
use_retailers = st.sidebar.checkbox("Limit to Specific Stores?", value=False)
selected_brands = []
if use_retailers:
    selected_brands = st.sidebar.multiselect(
        "Trusted Retailers", 
        ["Revolve", "ASOS", "Urban Outfitters", "Nordstrom", "Free People"],
        default=["Revolve", "ASOS"]
    )

max_price = st.sidebar.slider("Max Price ($)", 30, 1000, 200)

# 4. Search Logic with Marketplace Exclusion
def fetch_midnight_sun_results():
    # Primary aesthetic keywords
    aesthetic = "Cyber Y2K Scandinavian Barbie European Hawaii"
    
    # Category building
    cat_query = " OR ".join(product_categories) if product_categories else "festival tour outfit"
    
    # EXCLUSION LOGIC: Remove eBay, Depop, Poshmark, and Etsy
    exclusions = "-site:ebay.com -site:depop.com -site:poshmark.com -site:etsy.com"
    
    # Brand logic
    brand_query = ""
    if use_retailers and selected_brands:
        brand_sites = " OR ".join([f"site:{b.lower().replace(' ', '')}.com" for b in selected_brands])
        brand_query = f"({brand_sites})"
    
    full_query = f"{cat_query} {aesthetic} {brand_query} {exclusions}"
    
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

# 5. Main Content
st.title("☀️ Midnight Sun Style Finder")

if st.sidebar.button("GLITTER SEARCH"):
    results = fetch_midnight_sun_results()
    
    if results:
        # Final filter for price and stock verification (simplified)
        valid_items = []
        for item in results:
            price_str = item.get('price', '$0').replace('$', '').replace(',', '')
            try:
                if float(price_str) <= max_price:
                    valid_items.append(item)
            except:
                continue
        
        if not valid_items:
            st.warning("No matches found in this price range. Try broadening your budget!")
        else:
            cols = st.columns(3)
            for i, item in enumerate(valid_items[:12]):
                with cols[i % 3]:
                    st.image(item.get('thumbnail'), use_container_width=True)
                    st.subheader(item.get('title')[:50] + "...")
                    st.write(f"**{item.get('price')}** at **{item.get('source')}**")
                    
                    # Size availability often found in 'extensions'
                    if 'extensions' in item:
                        st.caption(f"Details: {', '.join(item['extensions'])}")
                    
                    # Direct link to site
                    st.link_button("Shop Now", item.get('link'))
    else:
        st.error("No results found. Try removing specific retailer filters!")
