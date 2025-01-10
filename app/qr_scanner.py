import pandas as pd
import streamlit as st
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
import io

import utils.connections as conn


@st.cache_data(ttl=10 * 60 * 60, show_spinner=False)
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


def decode_qr_code(image):
    decoded_objects = decode(image)
    decoded_data = [obj.data.decode("utf-8") for obj in decoded_objects]
    return decoded_data


def add_to_fridge(item_id):
    addition_query = """
INSERT INTO fridge (product_id) VALUES (%s);
    """
    conn.execute_query(addition_query, item_id)

    log_query = """
INSERT INTO fridge_log (product_id, action, action_date)
VALUES (%s, 'add', CURRENT_DATE);
    """
    conn.execute_query(log_query, item_id)


def delete_from_fridge(item_id):
    deletion_query = """
DELETE FROM fridge
WHERE product_id = %s;
    """
    conn.execute_query(deletion_query, item_id)

    log_query = """
INSERT INTO fridge_log (product_id, action, action_date)
VALUES (%s, 'delete', CURRENT_DATE);
    """
    conn.execute_query(log_query, item_id)


@st.fragment
def generate_qr_code(df_products):
    item = st.selectbox("Выберите товар для создания QR-кода", options=df_products["product_name"].unique(), index=None)
    item_query = """
SELECT p.id,
       product_name,
       product_type,
       manufacture_date,
       release_date,
       quantity,
       measure,
       nutritional_value,
       measure_type
FROM products AS p
LEFT JOIN product_types AS pt ON product_type_id = pt.id
WHERE product_name = %s;
    """
    if st.button("Показать QR-код"):
        if not item:
            st.error("Выберите наименование товара")
            st.stop()

        item_data = conn.execute_query(item_query, item)[0]
        product_info = f"""
ID: {item_data["id"]}
Название: {item_data["product_name"]}
Тип: {item_data["product_type"]}
Дата изготовления: {item_data["manufacture_date"]}
Годен до: {item_data["release_date"]}
Количество: {item_data["quantity"]} {item_data["measure"]}
Пищевая ценность: {item_data["nutritional_value"]}
Тип измерения: {item_data["measure_type"]}
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(product_info)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        buffer_ = io.BytesIO()
        img.save(buffer_, format="PNG")
        buffer_.seek(0)
        st.image(buffer_, caption="QR Code")


st.title("QR-сканер")
df_dict = load_data()

qr_code = st.camera_input("Сфотографируйте QR-код")
if qr_code:
    image = Image.open(qr_code)
    decoded_data = decode_qr_code(image)
    if not decoded_data:
        st.error("Ошибка чтения QR-кода")
        st.stop()

    mode = st.pills(label="Что Вы хотите сделать?", options=["Просмотреть", "Добавить в холодильник", "Удалить из холодильника"], default="Просмотреть")
    if mode == "Просмотреть":
        for data in decoded_data:
            for line in data.split("\n"):
                st.write(line)
    elif mode == "Добавить в холодильник":
        for data in decoded_data:
            for line in data.split("\n"):
                line_data = line.split(": ")
                if line_data[0] == "ID":
                    item_id = int(line_data[1])
                    break
        try:
            add_to_fridge(item_id)
            st.success("Продукт успешно добавлен")
        except Exception as e:
            st.error(e)
            st.stop()
    else:
        for data in decoded_data:
            for line in data.split("\n"):
                line_data = line.split(": ")
                if line_data[0] == "ID":
                    item_id = int(line_data[1])
                    break
        try:
            delete_from_fridge(item_id)
            st.success("Продукт успешно удален")
        except Exception as e:
            st.error(e)
            st.stop()

st.header("Генерация QR-кодов")
df_products = df_dict["df_products"]
generate_qr_code(df_products)
