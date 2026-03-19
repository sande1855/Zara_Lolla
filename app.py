import streamlit as st
import pandas as pd
from serpapi import GoogleSearch

# 1. Page Config & Session State
st.set_page_config(page_title="Lisa Frank x Zara Larsson", layout="wide")

if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# 2. Lisa Frank Aesthetic Styling
st.markdown("""
    <style>
    /* Rainbow Gradient Header */
    .main .block-container h1 {
        background: linear-gradient(to right, #FF00FF, #00FFFF, #FFD700, #32CD32, #FF69B4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        font-weight: 900;
        font-size: 3.8rem;
        text-align: center;
        text-shadow: 2px 2px #00000011;
    }
    
    /* Lisa Frank Sidebar - Electric Cyan to Yellow */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(#6EF7F7, #FFD700);
        border-right: 5px solid #FF00FF;
    }
    
    .stSelectbox label, .stSlider label, .stTextInput label {
        color: #ac3cfe !important;
        font-weight: bold;
        font-size: 1.1rem;
    }

    /* Bubble Buttons */
    div.stButton > button:first-child {
        background-color: #FF00FF;
        color: white;
        border-radius: 50px;
        border: 4px solid #00FFFF;
        font-weight: bold;
        font-size: 1.2rem;
        transition: 0.3s;
    }
    
    div.stButton > button:hover {
        transform: scale(1.05);
        border-color: #FFD700;
    }

    /* Product Image Glow */
    img {
        border: 6px solid #FFD700;
        border-radius: 30px;
        box-shadow: 5px 5px 15px rgba(255, 0, 255, 0.3);
    }

    /* Favorites Section Background */
    .fav-box {
        background-color: #fdf2ff;
        border: 2px dashed #ac3cfe;
        border-radius: 15px;
        padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Zara's Tour Palette & Filters
st.sidebar.title("🌈 Style Wizard")

# Tour-specific categories
category = st.sidebar.selectbox("Choose Your Vibe", [
    "Asymmetrical Ruffle Skirt", 
    "Butterfly Mesh Top", 
    "Hibiscus Print Dress", 
    "Airbrushed Baby Tee",
    "Metallic Sequin Set"
])

# Lisa Frank & Tour Colors
color_theme = st.sidebar.select_slider(
    "Select Color Story",
    options=["Neon Fuchsia", "Electric Cyan", "Sunset Orange", "Rainbow", "Silver Sparkle"]
)

brand_list = st.sidebar.multiselect(
    "Trusted Retailers", 
    ["Revolve", "ASOS", "Urban Outfitters", "Nordstrom", "Etsy"],
    default=["Revolve", "ASOS", "Urban Outfitters"]
)

max_price = st.sidebar.slider("Budget ($)", 10, 500, 125)

# 4. Search Function (Constructing the pop-star query)
def fetch_style_results():
    brand_query = " OR ".join([f"site:{b.lower().replace(' ', '')}.com" for b in brand_list])
    # Targeted keywords from Zara's wardrobe tour
    full_query = f"Zara Larsson Midnight Sun {category} {color_theme} {brand_query}"
    
    params = {
        "engine": "google_shopping",
        "q": full_query,
        "location": "United States",
        "api_key": st.secrets["SERP_API_KEY"]
    }
    search = GoogleSearch(params)
    return search.get_dict().get("shopping_results", [])

# 5. Main Content Area
st.title("☀️ Midnight Sun x Lisa Frank")

if st.sidebar.button("SEARCH MAGICAL LOOKS"):
    with st.spinner('Sprinkling glitter on your search...'):
        items = fetch_style_results()
        
        if items:
            cols = st.columns(3)
            for i, item in enumerate(items[:12]):
                # Price filtering logic
                price_str = item.get('price', '$1000').replace('$', '').replace(',', '')
                try:
                    current_price = float(price_str)
                except:
                    current_price = 1000.0

                if current_price <= max_price:
                    with cols[i % 3]:
                        st.image(item.get('thumbnail'), use_container_width=True)
                        st.markdown(f"**{item.get('title')[:45]}...**")
                        st.write(f"💖 **{item.get('price')}** @ {item.get('source')}")
                        
                        # Favorite button
                        if st.button(f"Add to Collection", key=f"fav_{i}"):
                            if item not in st.session_state.favorites:
                                st.session_state.favorites.append(item)
                                st.toast("Saved to your stickers! 🌈")
                        
                        st.link_button("View Item", item.get('link'))
        else:
            st.warning("No outfits found! Try changing the color or category.")

# 6. Your Collection (The Sticker Book)
st.divider()
st.header("🦄 Your Tour Collection")
if st.session_state.favorites:
    fav_cols = st.columns(5)
    for idx, fav in enumerate(st.session_state.favorites):
        with fav_cols[idx % 5]:
            st.image(fav.get('thumbnail'), width=120)
            st.caption(f"{fav.get('source')} - {fav.get('price')}")
else:
    st.info("Click 'Add to Collection' to start your Lisa Frank sticker book!")
