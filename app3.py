import streamlit as st
import pandas as pd
import ssl
import altair as alt
import numpy as np

# 🔧 Обход SSL
ssl._create_default_https_context = ssl._create_unverified_context

# 📝 Заголовок
st.title("Исследование конкурентов")

# 🔗 CSV-ссылка вакансий
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSigXcrNvRJII0f0bRwOhUGr4r5chw6NqxGjuiw2H18PlcdoAuewonaMGgE_oy4a5MHbzVifX67wulr/pub?output=csv'
df = pd.read_csv(url)

# ✅ Переименование первой колонки
if 'Unnamed: 0' in df.columns:
    df.rename(columns={'Unnamed: 0': 'Компания'}, inplace=True)

# 🔄 Замена названий компаний
df['Компания'] = df['Компания'].replace({
    'Альфа': 'Альфа-Банк',
    'Озон': 'Ozon'
})

# 🔠 Сортировка компаний по алфавиту
company_list_sorted = sorted(df['Компания'].unique())

# ⚙️ Session state
if 'selected_companies' not in st.session_state:
    st.session_state.selected_companies = company_list_sorted

# 🔘 Кнопки управления выбором компаний
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Выбрать все"):
        st.session_state.selected_companies = company_list_sorted
with col2:
    if st.button("Сбросить"):
        st.session_state.selected_companies = []
with col3:
    if st.button("ТОП-5"):
        top5 = ['Авито', 'Альфа-Банк', 'Т-банк', 'Яндекс', 'Ozon']
        st.session_state.selected_companies = [c for c in top5 if c in df['Компания'].unique()]

# 🔍 Мультиселект компаний
companies = st.multiselect(
    "Выбери компании для отображения",
    options=company_list_sorted,
    default=st.session_state.selected_companies,
    key="selected_companies"
)

# ✅ Настройка цветов и порядка площадок
platform_order = ['Внутренние карьерные сайты', 'HH', 'Getmatch', 'Habr Career']
platform_colors = {
    'Getmatch': 'yellow',
    'HH': 'red',
    'Habr Career': 'green',
    'Внутренние карьерные сайты': 'skyblue'
}

# 🔍 Фильтр площадок
if 'selected_platforms' not in st.session_state:
    st.session_state.selected_platforms = platform_order

selected_platforms = st.multiselect(
    "Карьерные площадки",
    options=platform_order,
    default=st.session_state.selected_platforms,
    key="selected_platforms"
)

# 📌 Фильтрация DataFrame
filtered_df = df[df['Компания'].isin(companies)]

# 🔷 **Функция генерации компактной цветной легенды**
def render_platform_legend():
    legend_html = ""
    for p in selected_platforms:
        color = platform_colors[p]
        legend_html += f"<span style='font-size:12px; color:{color}; font-weight:bold'>⬤ {p}</span> &nbsp;&nbsp;"
    st.markdown(legend_html, unsafe_allow_html=True)

# 📈 **Bar chart**
st.subheader("Количество вакансий на площадках всего")
render_platform_legend()

if not filtered_df.empty:
    bar_df = filtered_df[['Компания'] + selected_platforms]
    vacancies_sum = bar_df.drop(columns=['Компания']).sum().reindex(selected_platforms).reset_index()
    vacancies_sum.columns = ['Площадка', 'Количество']

    color_scale = alt.Scale(domain=selected_platforms,
                            range=[platform_colors[p] for p in selected_platforms])

    bar_chart = alt.Chart(vacancies_sum).mark_bar().encode(
        x=alt.X('Площадка', sort=selected_platforms),
        y='Количество',
        color=alt.Color('Площадка', scale=color_scale, legend=None)
    ).properties(width=700)

    st.altair_chart(bar_chart)
else:
    st.write("Нет данных для отображения. Выберите хотя бы одну компанию.")

# 📈 **Line chart**
st.subheader("Количество вакансий на каждой из площадок")
render_platform_legend()

if not filtered_df.empty:
    line_df = filtered_df[['Компания'] + selected_platforms]
    line_df['Всего вакансий'] = line_df[selected_platforms].sum(axis=1)
    line_df = line_df.sort_values('Всего вакансий', ascending=False)
    line_df.drop(columns=['Всего вакансий'], inplace=True)

    line_df_melt = line_df.melt(id_vars='Компания', var_name='Площадка', value_name='Количество')
    line_df_melt = line_df_melt[line_df_melt['Площадка'].isin(selected_platforms)]

    line_chart = alt.Chart(line_df_melt).mark_line(point=True).encode(
        x=alt.X('Компания', sort=line_df['Компания'].tolist()),
        y='Количество',
        color=alt.Color('Площадка', scale=color_scale, legend=None)
    ).properties(width=700)

    st.altair_chart(line_chart)
else:
    st.write("Нет данных для отображения линейного графика.")

# 🖥️ **Отображаем таблицу**
st.subheader("Данные по выбранным компаниям")
st.dataframe(filtered_df, use_container_width=True)

# 📌 ================================
# 🔷 ДОБАВЛЕНИЕ ВТОРОГО ЛИСТА - РЕЙТИНГИ
# 📌 ================================

ratings_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSigXcrNvRJII0f0bRwOhUGr4r5chw6NqxGjuiw2H18PlcdoAuewonaMGgE_oy4a5MHbzVifX67wulr/pub?gid=1694021447&single=true&output=tsv'
ratings_df = pd.read_csv(ratings_url, encoding='utf-8', sep='\t')
ratings_df.rename(columns=lambda x: x.strip(), inplace=True)

# 🔄 Замена названий компаний как в первом DataFrame
ratings_df['Компания'] = ratings_df['Компания'].replace({
    'Альфа': 'Альфа-Банк',
    'Озон': 'Ozon'
})

# 🔷 Фильтрация рейтингов по выбранным компаниям
ratings_df = ratings_df[ratings_df['Компания'].isin(companies)]

# 🔷 Список колонок для рейтингов
platform_rating_cols = ['DreamJob', 'Habr Career', 'Glassdoor']

# 🔠 Сортировка компаний по убыванию DreamJob
ratings_df = ratings_df.sort_values('DreamJob', ascending=False)

# 🔷 Заголовок
st.subheader("Рейтинги компаний по площадкам")

# 🔷 Легенда
rating_platform_colors = {
    'DreamJob': 'red',
    'Habr Career': 'green',
    'Glassdoor': 'gray',
}

legend_html = ""
for p in rating_platform_colors.keys():
    color = rating_platform_colors[p]
    legend_html += f"<span style='font-size:12px; color:{color}; font-weight:bold'>⬤ {p}</span> &nbsp;&nbsp;"
st.markdown(legend_html, unsafe_allow_html=True)

# 🔄 Melt для Altair
ratings_melt = ratings_df.melt(
    id_vars=['Компания'],
    value_vars=platform_rating_cols,
    var_name='Площадка',
    value_name='Рейтинг'
)

# ✅ Убираем 'отсутствует'
ratings_melt['Рейтинг'] = ratings_melt['Рейтинг'].replace('отсутствует', np.nan)

# 🎨 Color scale
color_scale_ratings = alt.Scale(
    domain=list(rating_platform_colors.keys()),
    range=[rating_platform_colors[p] for p in rating_platform_colors.keys()]
)

# 🔷 Chart
line_chart_ratings = alt.Chart(ratings_melt).mark_line(point=True).encode(
    x=alt.X('Компания', sort=ratings_df['Компания'].tolist(), title='Компания'),
    y=alt.Y('Рейтинг', title='Рейтинг', scale=alt.Scale(reverse=True)),
    color=alt.Color('Площадка', scale=color_scale_ratings, legend=None)
).transform_filter(
    alt.datum.Рейтинг != None
).properties(width=800)

st.altair_chart(line_chart_ratings)

# 📌 ================================
# 🔷 ЦИТАТЫ СОТРУДНИКОВ
# 📌 ================================
st.subheader("Цитаты сотрудников по компаниям")
selected_company_rating = st.selectbox("Выбери компанию для просмотра цитаты", ratings_df['Компания'].tolist())

quote_row = ratings_df[ratings_df['Компания'] == selected_company_rating]
if not quote_row.empty:
    quote_text = quote_row['Цитаты сотрудников (PO)'].values[0]

    st.markdown(
        f"""
        <div style='background-color:black; color:white; padding:20px; border-radius:10px; position:relative;'>
            <span style='position:absolute; top:10px; right:20px; cursor:pointer; font-size:20px;' onclick="this.parentElement.style.display='none';">&times;</span>
            <p>{quote_text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
