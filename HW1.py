import os
import time
import re
import json
import math
import pandas as pd
import streamlit as st
import plotly.express as px

# --- ШЛЯХ ДО ФАЙЛУ З КОМЕНТАРЯМИ ---
COMMENTS_FILE = "comments.json"

def load_comments():
    if os.path.exists(COMMENTS_FILE):
        try:
            with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_comments(comments_list):
    with open(COMMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(comments_list, f, ensure_ascii=False, indent=4)

# --- ІНІЦІАЛІЗАЦІЯ СТАНУ ---
if 'comments' not in st.session_state:
    st.session_state.comments = load_comments()

if 'splash_shown' not in st.session_state:
    st.session_state.splash_shown = False

if 'page' not in st.session_state:
    st.session_state.page = "main"

if 'cart' not in st.session_state:
    st.session_state.cart = {}


@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "cosmatics_dataset.csv")
    df = pd.read_csv(file_path)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(15.0)
    df['Rank'] = pd.to_numeric(df['Rank'], errors='coerce').fillna(0.0)
    return df


@st.cache_data
def get_all_ingredients(df_subset):
    all_ingredients = set()
    for ingredients_str in df_subset['Ingredients'].dropna():
        raw_ingredients = [i.strip().lower() for i in ingredients_str.split(',')]

        for i in raw_ingredients:
            if 'name?' in i or not i:
                continue

            i = re.sub(r'\(.*?\)', '', i)
            i = re.sub(r'[^a-z\s-]', '', i)
            i = i.strip(' -')

            if i:
                i = re.sub(r'\s+', ' ', i)
                all_ingredients.add(i)

    return sorted(list(all_ingredients))


df = load_data()


# --- ЛОГІКА СПЛЕШ-СКРИЇНУ (ПЕРШІ 2 СЕКУНДИ) ---
if not st.session_state.splash_shown:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("welcome_poster.jpg"):
            st.image("welcome_poster.jpg", use_column_width=True)
        else:
            st.markdown(
                "<h1 style='text-align: center; color: black;'>YOU'RE AMAZING, AWESOME, FABULOUS!</h1>", 
                unsafe_allow_html=True
            )
    
    time.sleep(2)
    st.session_state.splash_shown = True
    st.rerun()


# --- ЧОРНО-БІЛИЙ ДИЗАЙН (CSS) ---
bw_css = """
<style>
:root {
    --bg-color: #ffffff;
    --text-color: #000000;
    --accent-color: #000000;
}

.floating-btn {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background-color: var(--accent-color) !important;
    color: #ffffff !important;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    text-align: center;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    font-size: 30px;
    line-height: 60px;
    z-index: 1000;
    text-decoration: none;
    transition: background-color 0.3s ease;
    border: 2px solid var(--accent-color);
}
.floating-btn:hover {
    background-color: #333333 !important;
    border-color: #333333 !important;
}

div.stButton > button {
    background-color: var(--accent-color) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    border: 2px solid var(--accent-color) !important;
    transition: all 0.3s ease;
    font-weight: 500;
}

div.stButton > button p {
    color: #ffffff !important;
}

div.stButton > button:hover {
    background-color: #ffffff !important;
    color: var(--accent-color) !important;
    border: 2px solid var(--accent-color) !important;
}

div.stButton > button:hover p {
    color: var(--accent-color) !important;
}

[data-testid="stSidebar"] > div:first-child {
    background-color: #000000 !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] .stRadio p,
[data-testid="stSidebar"] .stSlider p,
[data-testid="stSidebar"] .stMultiSelect p,
[data-testid="stSidebar"] .stSelectbox p,
[data-testid="stSidebar"] .stTextInput p {
    color: #ffffff !important;
}

[data-testid="stSidebar"] [role="slider"] {
    background-color: #ffffff !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] > div > div:first-child {
    background-color: rgba(255,255,255,0.3) !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] > div > div:first-child > div {
    background-color: #ffffff !important;
}

[data-testid="stNotification"] {
    background-color: #f0f0f0 !important;
    border: 1px solid #cccccc !important;
    color: #000000 !important;
}
[data-testid="stNotification"] p {
    color: #000000 !important;
}
[data-testid="stNotification"] button {
    color: #000000 !important;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--text-color) !important;
}
hr {
    border-top: 1px solid #cccccc !important;
}
a {
    color: #555555 !important;
}

[data-testid="stForm"] {
    border: 1px solid #cccccc !important;
    padding: 15px !important;
    border-radius: 8px !important;
}
</style>
"""

st.markdown(bw_css, unsafe_allow_html=True)
if st.session_state.page == "main":
    st.markdown('<a href="#comments-section" class="floating-btn" title="Go to Comments">💬</a>', unsafe_allow_html=True)


# ==========================================
# РЕЖИМ 1: МАГАЗИН ТА РОЗРАХУНОК НАБОРУ
# ==========================================
if st.session_state.page == "shop":
    st.markdown("<h1>Cosmetic Shop & Bundle Calculator</h1>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Main Assistant", key="back_main_btn"):
        st.session_state.page = "main"
        st.rerun()

    st.markdown("---")
    
    col_shop1, col_shop2 = st.columns([2, 1])

    with col_shop1:
        st.subheader("Select Products by Category & Budget")
        
        categories = sorted(list(df['Label'].unique()))
        chosen_category = st.selectbox("Choose Category:", categories)
        
        cat_df = df[df['Label'] == chosen_category]
        
        min_p = int(cat_df['Price'].min())
        max_p = int(cat_df['Price'].max())
        if min_p == max_p:
            max_p += 1
            
        budget_range = st.slider(
            "Your Budget Range ($):",
            min_value=min_p,
            max_value=max_p,
            value=(min_p, max_p),
            key="shop_budget_slider"
        )
        
        filtered_cat_df = cat_df[(cat_df['Price'] >= budget_range[0]) & (cat_df['Price'] <= budget_range[1])]
        
        if filtered_cat_df.empty:
            st.warning("No products found in this price range. Please adjust your budget.")
        else:
            product_names = sorted(filtered_cat_df['Name'].unique())
            
            selected_specific_product = st.selectbox(
                "Choose specific product (optional):", 
                ["— View all products in category —"] + product_names
            )
            
            if selected_specific_product != "— View all products in category —":
                display_df = filtered_cat_df[filtered_cat_df['Name'] == selected_specific_product]
            else:
                display_df = filtered_cat_df

            st.markdown(f"#### 🧴 Products in '{chosen_category}':")
            
            for idx, r in display_df.head(10).iterrows():
                p_name = r['Name']
                p_brand = r['Brand']
                p_price = r['Price']
                
                is_in_cart = p_name in st.session_state.cart
                
                col_info, col_action, col_alt = st.columns([2.5, 1, 1])
                with col_info:
                    st.write(f"• **{p_name}** ({p_brand}) — **${p_price}**")
                
                with col_action:
                    if not is_in_cart:
                        if st.button("＋", key=f"add_{r.name}"):
                            st.session_state.cart[p_name] = {
                                'row': r.to_dict(), 
                                'category': chosen_category, 
                                'months': 3
                            }
                            st.rerun()
                    else:
                        st.markdown("✅ Added")
                
                with col_alt:
                    if st.button("🔄", key=f"alt_btn_{r.name}"):
                        st.session_state[f"show_alt_{r.name}"] = not st.session_state.get(f"show_alt_{r.name}", False)
                
                if st.session_state.get(f"show_alt_{r.name}", False):
                    st.info(f"✨ Alternatives for **{p_name}**:")
                    cheaper_alt = filtered_cat_df[filtered_cat_df['Price'] < p_price].sort_values(by='Price', ascending=False).head(2)
                    expensive_alt = filtered_cat_df[filtered_cat_df['Price'] > p_price].sort_values(by='Price', ascending=True).head(2)
                    alt_box_df = pd.concat([cheaper_alt, expensive_alt])
                    
                    if alt_box_df.empty:
                        st.write("No other alternatives in this budget range.")
                    else:
                        for _, alt_r in alt_box_df.iterrows():
                            alt_name = alt_r['Name']
                            alt_brand = alt_r['Brand']
                            alt_price = alt_r['Price']
                            if st.button(f"Switch to: {alt_name} (${alt_price})", key=f"switch_{r.name}_{alt_r.name}"):
                                old_months = st.session_state.cart.get(p_name, {}).get('months', 3)
                                if p_name in st.session_state.cart:
