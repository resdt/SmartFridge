import streamlit as st


def display():
    st.session_state.is_logged_in = False
    st.rerun()


display()
