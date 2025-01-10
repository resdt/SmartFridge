import hashlib

import streamlit as st
import utils.connections as conn


st.title("Авторизация")
with st.form("login_form"):
    username = st.text_input("Имя пользователя")
    password = st.text_input("Пароль", type="password")
    submit_button = st.form_submit_button("Войти")
    if submit_button:
        try:
            cur_user_query = """
SELECT username,
       hashed_password,
       user_type
  FROM users
 WHERE username = %s;
    """
            user_data = conn.execute_query(cur_user_query, username)
            if not user_data:
                st.error("Неправильный логин или пароль")
                st.stop()

            user = user_data[0]
            user_hashed_password = user["hashed_password"]
            user_type = user["user_type"]

            if user_hashed_password != hashlib.sha256(password.encode()).hexdigest():
                st.error("Неправильный логин или пароль")
                st.stop()

            st.session_state.user_type = user_type
            st.session_state.login = True
            st.rerun()
        except Exception:
            st.error("Неправильный логин или пароль")
            st.stop()
