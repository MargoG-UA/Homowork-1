import os
import time
import re
import pandas as pd
import streamlit as st
import plotly.express as px

# --- ІНІЦІАЛІЗАЦІЯ СТАНУ ---
if 'comments' not in st.session_state:
    st.session_state.comments = []

if 'splash_shown' not in st.session_state:
    st.session_state.splash_shown = False


@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "cosmatics_dataset.csv")
    df = pd.read_csv(file_path)
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


# --- ЛОГІКА СПЛЕШ-СКРИЇНУ (ПЕРШІ 5 СЕКУНД) ---
if not st.session_state.splash_shown:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("welcome_poster.jpg"):
            st.image("welcome_poster.jpg", use_column_width=True)
        else:
            st.markdown(
                "<h1 style='text-align: center; color: #950e4e;'>YOU'RE AMAZING, AWESOME, FABULOUS!</h1>", 
                unsafe_allow_html=True
            )
    
    time.sleep(5)
    st.session_state.splash_shown = True
    st.rerun()


# --- КАСТОМНИЙ ЗАГОЛОВОК ---
st.markdown(
    "<h1 style='color: #950e4e;'>Your personal assistant to make a great product choice</h1>", 
    unsafe_allow_html=True
)


# --- КАСТОМІЗАЦІЯ ДИЗАЙНУ (CSS) ---
custom_css = """
<style>
/* Плаваюча кнопка для коментарів */
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

/* Зміна фону бокової панелі */
[data-testid="stSidebar"] > div:first-child {
    background-color: #fc6794 !important;
}

/* Білий текст для заголовків, міток, радіокнопок у боковій панелі */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] .stRadio p {
    color: white !important;
}

/* Колір для ПОВЗУНКА */
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

/* Темний текст всередині полів вибору */
[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #31333F !important;
}
</style>
<a href="#comments-section" class="floating-btn" title="Go to Comments">💬</a>
"""

st.markdown(custom_css, unsafe_allow_html=True)


# --- БОКОВА ПАНЕЛЬ (ФІЛЬТРИ ЗЛІВА) ---
st.sidebar.header("Filters")

product_types = sorted(list(df['Label'].unique()))
selected_products = st.sidebar.multiselect(
    "Which type of product do you want?",
    options=product_types
)

if selected_products:
    ingredients_source_df = df[df['Label'].isin(selected_products)]
else:
    ingredients_source_df = df

all_unique_ingredients = get_all_ingredients(ingredients_source_df)

skin_types = ['Combination', 'Dry', 'Normal', 'Oily', 'Sensitive']
selected_skins = st.sidebar.multiselect(
    "Skin type:", 
    options=skin_types
)

all_brands = sorted(df['Brand'].dropna().unique())
selected_brands = st.sidebar.multiselect(
    "Brands:",
    options=all_brands
)

selected_allergies = st.sidebar.multiselect(
    "Avoided ingredients:",
    options=all_unique_ingredients
)

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

sort_option = st.sidebar.radio(
    "Sort by:",
    ("relevance", "price increase", "price decrease")
)

st.sidebar.markdown("---")

search_clicked = st.sidebar.button("Search", use_container_width=True)
sort_category_clicked = st.sidebar.button("Sort by Categories", use_container_width=True)


# --- ОСНОВНА ЧАСТИНА ---

# 1. ДИНАМІЧНА КРУГОВА ДІАГРАМА З ФІКСОВАНИМИ КОЛЬОРАМИ ТА ПІДСВІТКОЮ
category_counts = df['Label'].value_counts().reset_index()
category_counts.columns = ['Category', 'Count']

fixed_colors = {
    'Moisturizer': '#880e4f',
    'Cleanser': '#ad1457',
    'Face Mask': '#d81b60',
    'Treatment': '#e91e63',
    'Eye cream': '#ec407a',
    'Sun protect': '#f06292'
}

def get_sector_color(row):
    cat = row['Category']
    base_color = fixed_colors.get(cat, '#950e4e')
    
    if not selected_products or cat in selected_products:
        return base_color
    else:
        h = base_color.lstrip('#')
        rgb = tuple(int(h[j:j+2], 16) for j in (0, 2, 4))
        return f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.25)'

category_counts['Color'] = category_counts.apply(get_sector_color, axis=1)

fig = px.pie(
    category_counts, 
    names='Category', 
    values='Count', 
    hole=0.4,
    color='Category',
    color_discrete_map=fixed_colors
)

fig.update_traces(
    textposition='inside', 
    textinfo='percent+label',
    textfont=dict(color='white'),
    marker=dict(
        colors=category_counts['Color'],
        line=dict(color='#ffffff', width=2)
    )
)

fig.update_layout(
    margin=dict(t=10, b=10, l=10, r=10),
    height=400,
    showlegend=True,
    transition=dict(duration=500, easing='cubic-in-out')
)

st.plotly_chart(fig, use_container_width=True)
st.markdown("---")


# 2. РЕЗУЛЬТАТИ ПОШУКУ
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
