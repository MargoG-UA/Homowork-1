import os
import time
import re
import pandas as pd
import streamlit as st
import plotly.express as px

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

# --- КАСТОМНИЙ ЗАГОЛОВОК ---
st.markdown(
    "<h1 style='color: #950e4e;'>Your personal assistant to make a great product choice</h1>", 
    unsafe_allow_html=True
)

# --- КАСТОМІЗАЦІЯ ДИЗАЙНУ (CSS + ПЛАВАЮЧА КАРТИНКА В ПРАВОМУ НИЖНЬОМУ КУТУ) ---
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

/* Стиль для вашої картинки в правому нижньому куті (вище за кнопку коментарів або поруч) */
.corner-image {
    position: fixed;
    bottom: 20px;
    right: 100px; /* зсунуто вліво від кнопки коментарів, щоб вони не накладалися */
    width: 110px;  /* розмір картинки можна змінити за потреби */
    z-index: 999;
    pointer-events: none; /* щоб картинка не перекривала кліки на інші елементи */
    opacity: 0.9;
}

/* Зміна фону бокової панелі */
[data-testid="stSidebar"] > div:first-child {
    background-color: #fc6794 !important;
}

/* Білий текст для заголовків, міток (labels), радіокнопок у боковій панелі */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] .stRadio p {
    color: white !important;
}

/* Білий колір для ПОВЗУНКА (цифри, кружечки, лінія) */
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

/* Темний текст всередині полів вибору */
[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #31333F !important;
}
</style>
<a href="#comments-section" class="floating-btn" title="Go to Comments">💬</a>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Відображення картинки з локального файлу (назву файлу змініть на вашу, якщо потрібно)
if os.path.exists("girl_bow.png"):
    st.markdown('<img src="data:image/png;base64,' + ... + '" class="corner-image">', unsafe_allow_html=True) 
# Але в Streamlit найпростіше вивести картинку через вбудовану функцію або HTML:
st.markdown('<img src="https://raw.githubusercontent.com/.../girl_bow.png" class="corner-image">', unsafe_allow_html=True) # або локальний шлях нижче:
