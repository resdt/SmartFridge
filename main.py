import streamlit as st


def main():
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False

    is_logged_in = st.session_state.is_logged_in
    if not is_logged_in:
        pages = [st.Page("app/login.py", title="Авторизация", icon=":material/login:")]
    else:
        pages = [st.Page("app/home.py", title="Главная страница", icon=":material/home:"),
                 st.Page("app/logout.py", title="Выйти", icon=":material/logout:"),
                 st.Page("app/qr_scanner.py", title="Сканер QR-кодов", icon=":material/qr_code_scanner:"),
                 st.Page("app/demand.py", title="Аналитика потребления", icon=":material/whatshot:"),
                 st.Page("app/product_list.py", title="Список покупок", icon=":material/receipt_long:")]

    display_pages = st.navigation(pages)
    display_pages.run()


if __name__ == "__main__":
    main()
