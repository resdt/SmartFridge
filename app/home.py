import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

import utils.connections as conn


# @st.cache_data(ttl=10 * 60 * 60, show_spinner=False)
def load_data():
    result = {}
    fridge_query = """
SELECT product_name,
       product_type,
       quantity,
       measure,
       manufacture_date,
       release_date
FROM fridge
LEFT JOIN products AS p ON product_id = p.id
LEFT JOIN product_types AS pt ON product_type_id = pt.id;
    """
    df_fridge = pd.DataFrame(conn.execute_query(fridge_query))
    cur_date = datetime.now()
    df_fridge["product_state"] = df_fridge["release_date"].apply(
        lambda x: "ОК" if cur_date + timedelta(days=7) <= pd.to_datetime(x) else
        "Истекает срок годности" if cur_date <= pd.to_datetime(x) <= cur_date + timedelta(days=3) else
        "Просрочено"
    )
    result["df_fridge"] = df_fridge

    return result


def color_rows(row):
    color = ("" if row["product_state"] == "ОК" else
             "#FABD2F" if row["product_state"] == "Истекает срок годности" else
             "#FB4934")
    return ["color: " + color] * len(row)


@st.fragment
def display_search_field(src_df):
    df = src_df.copy()
    search_name = st.text_input("Введите название или тип товара:")
    if search_name:
        search_result = (
            df[(df["product_name"].str.contains(search_name, case=False))
               | (df["product_type"].str.contains(search_name, case=False))]
            .reset_index()
            .drop(columns="index")
        )
        search_result.index += 1
        if not search_result.empty:
            st.dataframe(search_result.style.apply(color_rows, axis=1))
        else:
            st.write(f"Продукт/тип товара {search_name} не найдены.")


st.title("Главная страница")
df_dict = load_data()

st.header("Состояние холодильника")
df_fridge = df_dict["df_fridge"]

display_search_field(df_fridge)

all_quantity = df_fridge.shape[0]
st.metric("Всего товаров:", f"{all_quantity: d}")
col1, col2, col3 = st.columns(3)
with col1:
    ok_quantity = df_fridge[df_fridge["product_state"] == "ОК"].shape[0]
    st.metric("Качественных:", f"{ok_quantity: d}")
with col2:
    almost_bad_quantity = df_fridge[df_fridge["product_state"] == "Истекает срок годности"].shape[0]
    st.metric("Истекает срок годности:", f"{almost_bad_quantity: d}")
with col3:
    bad_quantity = df_fridge[df_fridge["product_state"] == "Просрочено"].shape[0]
    st.metric("Просроченных:", f"{bad_quantity: d}")

df_display = df_fridge.copy()
df_display.index += 1
df_display = df_display.style.apply(color_rows, axis=1)
st.dataframe(df_display, use_container_width=True)
