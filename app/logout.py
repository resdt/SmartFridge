import streamlit as st


def display():
    st.session_state.is_logged_in = False
    st.session_state.user_type = None
    st.rerun()


display()
