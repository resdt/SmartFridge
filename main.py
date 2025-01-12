import streamlit as st


if "login" not in st.session_state:
    st.session_state.login = False

is_logged_in = st.session_state.login
if not is_logged_in:
    pages = [st.Page("app/login.py", title="Авторизация", icon=":material/login:")]
else:
    user_type = st.session_state.user_type
    pages = [st.Page("app/home.py", title="Главная страница", icon=":material/home:"),
             st.Page("app/logout.py", title="Выйти", icon=":material/logout:")]
    if user_type == "administrator":
        pages.append(st.Page("app/qr_scanner.py", title="Сканер QR-кодов", icon=":material/qr_code_scanner:"))
    pages.extend([st.Page("app/demand.py", title="Аналитика потребления", icon=":material/whatshot:"),
                  st.Page("app/product_list.py", title="Список покупок", icon=":material/receipt_long:")])
display_pages = st.navigation(pages)
display_pages.run()
