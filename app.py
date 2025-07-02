import streamlit as st
import pandas as pd

st.title("Простой дашборд Google Sheets")

# Вставь свою CSV-ссылку
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSigXcrNvRJII0f0bRwOhUGr4r5chw6NqxGjuiw2H18PlcdoAuewonaMGgE_oy4a5MHbzVifX67wulr/pub?output=csv'

# Загрузи данные
df = pd.read_csv(url)

# Покажи таблицу
st.write(df)
