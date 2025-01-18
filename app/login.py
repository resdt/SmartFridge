import hashlib

import streamlit as st

import utils.connections as conn


def display():
    st.title("Авторизация")
    with st.form("login_form"):
        username = st.text_input("Имя пользователя").strip().lower()
        password = st.text_input("Пароль", type="password")
        submit_button = st.form_submit_button("Войти")
        if submit_button:
            try:
                cur_user_query = """
                SELECT TRUE
                FROM users
                WHERE username = $1 AND hashed_password = $2;
                """
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                user_data = conn.execute_query(cur_user_query, username, hashed_password)

                if not user_data:
                    st.error("Неправильный логин или пароль")
                    st.stop()

                st.session_state.is_logged_in = True
                st.rerun()
            except Exception:
                st.error("Неправильный логин или пароль")
                st.stop()


display()
