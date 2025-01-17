import pandas as pd
import streamlit as st

import utils.connections as conn


@st.cache_data(ttl=10 * 60, show_spinner=False)
def load_data():
    result = {}
    product_query = """
    SELECT product_name,
           product_type,
           measure_type,
           manufacture_date,
           release_date
    FROM products
    LEFT JOIN product_types AS pt ON product_type_id = pt.id;
    """
    df_products = pd.DataFrame(conn.execute_query(product_query))
    result["df_products"] = df_products

    return result


@st.fragment
def display_product_list():
    df_products = st.session_state.df_products
    df_display = st.session_state.df_display

    col1, col2 = st.columns(2)
    with col1:
        product_name = st.selectbox(label="Выберите название товара", options=df_products["product_name"].unique(), index=None)
    with col2:
        quantity = st.number_input(label="Выберите количество товара", min_value=1)

    if st.button("Добавить", use_container_width=True):
        if product_name is not None:
            new_row = pd.DataFrame({"Название товара": [product_name], "Количество товара": [quantity]})
            df_display = pd.concat([df_display, new_row], ignore_index=True)
            df_display.reset_index(drop=True, inplace=True)
            df_display.index += 1
            st.session_state.df_display = df_display
        else:
            st.error("Выберите название товара")
    if not df_display.empty:
        st.dataframe(df_display, use_container_width=True)
        if st.button("Очистить"):
            df_display = pd.DataFrame()
            st.rerun()


def display():
    st.title("Список покупок")
    df_dict = load_data()

    df_products = df_dict["df_products"]
    st.session_state.df_products = df_products
    st.session_state.df_display = pd.DataFrame(columns=["Название товара", "Количество товара"])
    display_product_list()


display()
