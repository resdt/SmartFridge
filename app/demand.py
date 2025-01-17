import pandas as pd
import streamlit as st
import datetime
import plotly.graph_objs as go

import utils.connections as conn


@st.cache_data(ttl=10 * 60, show_spinner=False)
def load_data():
    result = {}
    fridge_log_query = """
    SELECT product_name,
           action,
           action_date
    FROM fridge_log
    LEFT JOIN products AS p ON product_id = p.id;
    """
    df_fridge_log = pd.DataFrame(conn.execute_query(fridge_log_query))
    result["df_fridge_log"] = df_fridge_log

    return result


def display_demand_plot(src_df):
    df = src_df.copy()
    df_grouped = df.groupby(["action", "action_date"])["product_name"].count().reset_index(name="amount")
    fig = go.Figure()

    df_added = df_grouped[df_grouped["action"] == "add"]
    fig.add_trace(go.Scatter(x=df_added["action_date"],
                             y=df_added["amount"],
                             name="Добавленные товары",
                             mode="lines",
                             fill="tozeroy",
                             line=dict(color="rgba(135, 206, 250, 0.6)"),
                             fillcolor="rgba(173, 216, 230, 0.3)"))

    df_deleted = df_grouped[df_grouped["action"] == "delete"]
    fig.add_trace(go.Scatter(x=df_deleted["action_date"],
                             y=df_deleted["amount"],
                             name="Удаленные товары",
                             mode="lines",
                             fill="tozeroy",
                             line=dict(color="rgba(255, 99, 71, 0.6)"),
                             fillcolor="rgba(255, 160, 122, 0.3)"))

    fig.update_layout(xaxis=dict(title="Дата"),
                      yaxis=dict(title="Количество товаров"))

    st.plotly_chart(fig)


@st.fragment
def display_filter_block(src_df):
    df = src_df.copy()
    today = datetime.datetime.now()
    date_interval = st.date_input("Временной промежуток",
                                  (today - datetime.timedelta(weeks=1), today),
                                  datetime.date(today.year - 1, 1, 1),
                                  today,
                                  format="DD.MM.YYYY")
    if len(date_interval) == 1:
        df = df[df["action_date"] == date_interval[0]]
    elif len(date_interval) == 2:
        min_date = date_interval[0]
        max_date = date_interval[1]
        df = df[(df["action_date"] >= min_date)
                & (df["action_date"] <= max_date)]

    df.reset_index(drop=True, inplace=True)
    df.index += 1

    col1, col2 = st.columns(2)
    with col1:
        added_items = df[df["action"] == "add"].shape[0]
        st.metric("Товаров добавлено:", f"{added_items}")
    with col2:
        deleted_items = df[df["action"] == "delete"].shape[0]
        st.metric("Товаров удалено:", f"{deleted_items}")

    display_demand_plot(df)
    st.dataframe(df, use_container_width=True)


def display():
    st.title("Анализ потребляемых товаров")
    df_dict = load_data()

    df_fridge_log = df_dict["df_fridge_log"]
    display_filter_block(df_fridge_log)


display()
