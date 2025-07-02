import streamlit as st
import pandas as pd
import ssl
import altair as alt

# 🔧 Обход SSL
ssl._create_default_https_context = ssl._create_unverified_context

# 📝 Заголовок
st.title("Простой дашборд Google Sheets")

# 🔗 CSV-ссылка
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSigXcrNvRJII0f0bRwOhUGr4r5chw6NqxGjuiw2H18PlcdoAuewonaMGgE_oy4a5MHbzVifX67wulr/pub?output=csv'

# 📊 Загрузка данных
df = pd.read_csv(url)

# ✅ Переименование первой колонки (если Unnamed: 0)
if 'Unnamed: 0' in df.columns:
    df.rename(columns={'Unnamed: 0': 'Компания'}, inplace=True)

# 🔄 Замена названий компаний
df['Компания'] = df['Компания'].replace({
    'Альфа': 'Альфа-Банк',
    'Озон': 'Ozon'
})

# 🔠 Сортировка компаний по алфавиту
company_list_sorted = sorted(df['Компания'].unique())

# ⚙️ Session state для компаний
if 'selected_companies' not in st.session_state:
    st.session_state.selected_companies = company_list_sorted

# 🔘 Кнопки управления выбором компаний
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Выбрать все компании"):
        st.session_state.selected_companies = company_list_sorted
with col2:
    if st.button("Сбросить все компании"):
        st.session_state.selected_companies = []
with col3:
    if st.button("Выбрать ТОП-5"):
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
    "Выбери площадки для отображения",
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
st.subheader("Bar chart: количество вакансий по площадкам (выбранные компании)")
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
st.subheader("Line chart: вакансии по площадкам для каждой компании")
render_platform_legend()

if not filtered_df.empty:
    line_df = filtered_df[['Компания'] + selected_platforms]
    # ➡️ Сортировка компаний по убыванию суммы вакансий
    line_df['Всего вакансий'] = line_df[selected_platforms].sum(axis=1)
    line_df = line_df.sort_values('Всего вакансий', ascending=False)
    line_df.drop(columns=['Всего вакансий'], inplace=True)

    # melt для Altair
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
