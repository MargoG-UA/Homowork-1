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

# --- КАСТОМНИЙ ЗАГОЛОВОК ІЗ ШРИФТОМ BILLION DOLLARS ---
# Зверніть увагу: щоб цей шрифт відображався у всіх користувачів, 
# він має бути встановлений на їхньому пристрої.
st.markdown(
    """
    <h1 style="font-family: 'Billion Dollars', sans-serif;">
        Your personal assistant to make a great product choice
    </h1>
    """, 
    unsafe_allow_html=True
)

# --- ДОДАВАННЯ ПЛАВАЮЧОЇ КНОПКИ (HTML/CSS) ---
floating_button_css = """
<style>
.floating-btn {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background-color: #FF4B4B;
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
    background-color: #FF6666;
}
</style>
<a href="#comments-section" class="floating-btn" title="Go to Comments">💬</a>
"""
st.markdown(floating_button_css, unsafe_allow_html=True)


# --- БОКОВА ПАНЕЛЬ (ЛІВИЙ КРАЙ) ---
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

# 5. Діапазон ціни (Динамічний)
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

# Кнопки також розміщуємо в боковій панелі
search_clicked = st.sidebar.button("Search", use_container_width=True)
sort_category_clicked = st.sidebar.button("Sort by Categories", use_container_width=True)


# --- ОСНОВНА ЧАСТИНА (РЕЗУЛЬТАТИ ПОШУКУ) ---
if search_clicked or sort_category_clicked:

    with st.spinner('Choosing the best for you...'):
        time.sleep(0.6)

        filtered_df = df.copy()

        # Фільтрація по обраним продуктам
        if selected_products:
            filtered_df = filtered_df[filtered_df['Label'].isin(selected_products)]

        # Фільтрація по типу шкіри
        if selected_skins:
            for skin in selected_skins:
                filtered_df = filtered_df[filtered_df[skin] == 1]

        # Фільтрація по бренду
        if selected_brands:
            filtered_df = filtered_df[filtered_df['Brand'].isin(selected_brands)]

        # Фільтрація по алергіях
        if selected_allergies:
            for allergy in selected_allergies:
                 filtered_df = filtered_df[
                    ~filtered_df['Ingredients'].str.lower().str.contains(allergy, na=False, regex=False)]

        # Фільтрація по ціні
        filtered_df = filtered_df[
            (filtered_df['Price'] >= selected_price_range[0]) &
            (filtered_df['Price'] <= selected_price_range[1])
            ]

        # Застосування сортування
        if sort_category_clicked:
            filtered_df = filtered_df.sort_values(by=["Label", "Name"], ascending=[True, True])
        else:
            if sort_option == "price increase":
                filtered_df = filtered_df.sort_values(by="Price", ascending=True)
            elif sort_option == "price decrease":
                filtered_df = filtered_df.sort_values(by="Price", ascending=False)

    # Вивід результатів 
    if not filtered_df.empty:
        st.success(f"Products found: {len(filtered_df)}")
        for index, row in filtered_df.iterrows():
            st.markdown(f"### {row['Name']} ({row['Brand']})")
            st.write(f"🧴 **Category:** {row['Label']} | 💵 **Price:** ${row['Price']} | ⭐ **Rate:** {row.get('Rank', 'NO DATA')}")
            st.markdown("---")
    else:
        st.error("Unfortunately, we don't have any data about this product. Please change the parameters.")

st.markdown("<br><br>", unsafe_allow_html=True)

# Створюємо "якір" (anchor), на який посилається плаваюча кнопка
st.markdown('<div id="comments-section"></div>', unsafe_allow_html=True)

st.subheader("Comments")
st.write("Haven't found your favourite product? Have an idea for development? Text us!")

# Форма для додавання коментаря
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

# Виведення всіх збережених коментарів
if st.session_state.comments:
    st.markdown("#### Comments:")
    for c in reversed(st.session_state.comments):
        st.info(f"**{c['name']}**: {c['text']}")
