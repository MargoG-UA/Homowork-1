import os
import time
import re
import pandas as pd
import streamlit as st

# Ініціалізація стану для збереження коментарів
if 'comments' not in st.session_state:
    st.session_state.comments = []


@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "cosmatics_dataset.csv")
    df = pd.read_csv(file_path)
    return df


@st.cache_data
def get_all_ingredients(df):
    all_ingredients = set()
    for ingredients_str in df['Ingredients'].dropna():
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
all_unique_ingredients = get_all_ingredients(df)

st.title("Your personal assistant to make a great product choice")

# --- КАСТОМІЗАЦІЯ ДИЗАЙНУ (CSS) ---
custom_css = """
<style>
/* 1. Плаваюча кнопка для коментарів */
.floating-btn {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background-color: #950e4e !important;
    color: white !important;
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
}
.floating-btn:hover {
    background-color: #7a0b3f !important;
}

/* 2. Зміна фону бокової панелі */
[data-testid="stSidebar"] > div:first-child {
    background-color: #fc6794 !important;
}

/* 3. Білий текст для заголовків, міток (labels), радіокнопок */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] .stRadio p {
    color: white !important;
}

/* 4. Білий колір для ПОВЗУНКА (цифри, кружечки, лінія) */
[data-testid="stSidebar"] .stSlider div[data-testid="stTickBar"] > div,
[data-testid="stSidebar"] .stSlider div[data-testid="stTickBarMin"],
[data-testid="stSidebar"] .stSlider div[data-testid="stTickBarMax"],
[data-testid="stSidebar"] .stSlider p {
    color: white !important;
}

[data-testid="stSidebar"] .stSlider [role="slider"] {
    background-color: white !important;
    border: 2px solid white !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] > div > div:first-child > div {
    background-color: white !important;
}

[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] > div > div:first-child {
    background-color: rgba(255, 255, 255, 0.4) !important;
}

[data-testid="stSidebar"] .stSlider [role="slider"]:hover,
[data-testid="stSidebar"] .stSlider [role="slider"]:active {
    background-color: white !important;
}

/* 5. Темний текст всередині полів вибору */
[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #31333F !important;
}

/* 6. ЖОРСТКА ЗМІНА КОЛЬОРУ ТЕГІВ (#950e4e) */
div[data-baseweb="select"] span[data-baseweb="tag"] {
    background-color: #950e4e !important;
    color: white !important;
}

/* Робимо хрестик на тегах білим */
div[data-baseweb="select"] span[data-baseweb="tag"] svg {
    fill: white !important;
}

/* 7. ЖОРСТКА ЗМІНА КОЛЬОРУ АКТИВНОЇ РАДІОКНОПКИ (#950e4e) */
div[data-testid="stRadio"] div[role="radio"][aria-checked="true"] > div {
    background-color: #950e4e !important;
    border-color: #950e4e !important;
}
div[data-testid="stRadio"] div[role="radio"][aria-checked="true"] > div > div {
    background-color: #950e4e !important;
}
</style>
<a href="#comments-section" class="floating-btn" title="Go to Comments">💬</a>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# --- БОКОВА ПАНЕЛЬ (ФІЛЬТРИ ЗЛІВА) ---
st.sidebar.header("Filters")

# 1. Вибір продукту
product_types = sorted(list(df['Label'].unique()))
selected_products = st.sidebar.multiselect(
    "Which type of product do you want?",
    options=product_types
)

# 2. Тип шкіри
skin_types = ['Combination', 'Dry', 'Normal', 'Oily', 'Sensitive']
selected_skins = st.sidebar.multiselect(
    "Оберіть ваш тип шкіри:", 
    options=skin_types
)

# 3. Вибір бренду
all_brands = sorted(df['Brand'].dropna().unique())
selected_brands = st.sidebar.multiselect(
    "Brands:",
    options=all_brands
)

# 4. Вибір алергій
selected_allergies = st.sidebar.multiselect(
    "Avoided products:",
    options=all_unique_ingredients
)

# 5. Динамічний діапазон ціни
if selected_brands:
    price_df = df[df['Brand'].isin(selected_brands)]
else:
    price_df = df

min_price = int(price_df['Price'].min())
max_price = int(price_df['Price'].max())

if min_price == max_price:
    max_price += 1

selected_price_range = st.sidebar.slider(
    "Price range ($):",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

# 6. Сортування
sort_option = st.sidebar.radio(
    "Sort by:",
    ("relevance", "price increase", "price decrease")
)

st.sidebar.markdown("---")

search_clicked = st.sidebar.button("Search", use_container_width=True)
sort_category_clicked = st.sidebar.button("Sort by Categories", use_container_width=True)


# --- ОСНОВНА ЧАСТИНА (РЕЗУЛЬТАТИ) ---
if search_clicked or sort_category_clicked:

    with st.spinner('Choosing the best for you...'):
        time.sleep(0.6)

        filtered_df = df.copy()

        if selected_products:
            filtered_df = filtered_df[filtered_df['Label'].isin(selected_products)]

        if selected_skins:
            for skin in selected_skins:
                filtered_df = filtered_df[filtered_df[skin] == 1]

        if selected_brands:
            filtered_df = filtered_df[filtered_df['Brand'].isin(selected_brands)]

        if selected_allergies:
            for allergy in selected_allergies:
                 filtered_df = filtered_df[
                    ~filtered_df['Ingredients'].str.lower().str.contains(allergy, na=False, regex=False)]

        filtered_df = filtered_df[
            (filtered_df['Price'] >= selected_price_range[0]) &
            (filtered_df['Price'] <= selected_price_range[1])
            ]

        if sort_category_clicked:
            filtered_df = filtered_df.sort_values(by=["Label", "Name"], ascending=[True, True])
        else:
            if sort_option == "price increase":
                filtered_df = filtered_df.sort_values(by="Price", ascending=True)
            elif sort_option == "price decrease":
                filtered_df = filtered_df.sort_values(by="Price", ascending=False)

    if not filtered_df.empty:
        st.success(f"Products found: {len(filtered_df)}")
        for index, row in filtered_df.iterrows():
            st.markdown(f"### {row['Name']} ({row['Brand']})")
            st.write(f"🧴 **Category:** {row['Label']} | 💵 **Price:** ${row['Price']} | ⭐ **Rate:** {row.get('Rank', 'NO DATA')}")
            st.markdown("---")
    else:
        st.error("Unfortunately, we don't have any data about this product. Please change the parameters.")

st.markdown("<br><br>", unsafe_allow_html=True)

# Якір для плаваючої кнопки коментарів
st.markdown('<div id="comments-section"></div>', unsafe_allow_html=True)

st.subheader("Comments")
st.write("Haven't found your favourite product? Have an idea for development? Text us!")

# Форма коментарів
with st.form("comment_form", clear_on_submit=True):
    user_name = st.text_input("Name (not necessarily):")
    new_comment = st.text_area("your comment:")
    submit_button = st.form_submit_button("send")

    if submit_button:
        if new_comment.strip():
            name_to_display = user_name.strip() if user_name.strip() else "Anonymous"
            st.session_state.comments.append({"name": name_to_display, "text": new_comment})

            st.balloons()
            st.success("The comment is successfully added!")
        else:
            st.warning("The comment can't be empty.")

if st.session_state.comments:
    st.markdown("#### Comments:")
    for c in reversed(st.session_state.comments):
        st.info(f"**{c['name']}**: {c['text']}")
