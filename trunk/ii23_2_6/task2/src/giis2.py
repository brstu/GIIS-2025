import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Визуализация данных", layout="wide")

st.title("Интерактивная визуализация данных")

uploaded_file = st.file_uploader("Загрузите CSV или Excel файл", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Просмотр данных")
    st.dataframe(df)

    df = df.dropna()

    st.subheader("Построение графика")

    chart_type = st.selectbox("Тип визуализации",
                              ["Линейный график", "Гистограмма", "Диаграмма рассеяния", "Круговая диаграмма"])

    x_column = st.selectbox("Ось X", df.columns)
    y_column = st.selectbox("Ось Y", df.select_dtypes(include='number').columns)

    fig = None

    if chart_type == "Линейный график":
        fig = px.line(df, x=x_column, y=y_column)
    elif chart_type == "Гистограмма":
        fig = px.histogram(df, x=x_column, y=y_column)
    elif chart_type == "Диаграмма рассеяния":
        fig = px.scatter(df, x=x_column, y=y_column)
    elif chart_type == "Круговая диаграмма":
        pie_column = st.selectbox("Категориальный столбец для круговой диаграммы", df.columns)
        count_data = df[pie_column].value_counts().reset_index()
        count_data.columns = [pie_column, "count"]
        fig = px.pie(count_data, names=pie_column, values="count")

    if fig:
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Экспорт визуализации")
        export_format = st.selectbox("Формат экспорта", ["PNG", "JPEG", "PDF"])

        try:
            import plotly.io as pio

            buffer = io.BytesIO()
            fig.write_image(buffer, format=export_format.lower())
            st.download_button(
                label=f"Скачать график как {export_format}",
                data=buffer,
                file_name=f"chart.{export_format.lower()}",
                mime=f"image/{export_format.lower()}"
            )
        except ValueError as e:
            st.warning(f" Для экспорта в изображение установите пакет Kaleido:\n```\npip install -U kaleido\n```")
        except Exception as ex:
            st.error(f"Ошибка экспорта: {ex}")

    st.subheader("Группировка данных")
    group_col = st.selectbox("Столбец для группировки", df.columns)
    agg_func = st.selectbox("Функция агрегации", ["mean", "sum", "max", "min"])

    numeric_cols = [col for col in df.select_dtypes(include='number').columns if col != group_col]

    try:
        df_grouped = df.groupby(group_col)[numeric_cols].agg(agg_func).reset_index()
        st.write("Результат группировки:")
        st.dataframe(df_grouped)
    except Exception as e:
        st.error(f"❗ Ошибка при группировке: {e}")
