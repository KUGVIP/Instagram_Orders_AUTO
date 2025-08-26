import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import pandas as pd

# ======== Google Sheets Setup ========
SHEET_NAME = "Instagram Orders"
SHEET_TAB = "Đơn Hàng"

def connect_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).worksheet(SHEET_TAB)
    return sheet

def parse_order(message: str):
    fields = {
        "Tên IG": r"Tên IG[:：]\s*(.+)",
        "Tên người nhận": r"Tên người nhận[:：]\s*(.+)",
        "SĐT": r"SĐT[:：]\s*(.+)",
        "Địa chỉ": r"Địa chỉ[:：]\s*(.+)",
        "Ảnh mẫu": r"Ảnh mẫu[:：]\s*(.+)",
        "Số lượng bó": r"Số lượng bó[:：]\s*(.+)",
        "Note yêu cầu khách hàng": r"Note yêu cầu khách hàng[:：]\s*(.+)"
    }

    data = []
    for key, pattern in fields.items():
        match = re.search(pattern, message, re.IGNORECASE)
        data.append(match.group(1).strip() if match else "")
    return data

def save_to_sheet(data_row):
    sheet = connect_gsheet()
    sheet.append_row(data_row)

def load_orders():
    sheet = connect_gsheet()
    records = sheet.get_all_records()
    return pd.DataFrame(records)

# === Streamlit App ===
st.set_page_config(page_title="Quản lý đơn IG", layout="centered")
st.title("🌸 Nhập đơn hàng Instagram")

st.markdown("Dán nội dung tin nhắn đã tổng hợp từ Instagram vào ô dưới:")

message = st.text_area("📥 Tin nhắn đơn hàng", height=200)

if st.button("✅ Ghi vào Google Sheet"):
    if message.strip() == "":
        st.warning("Vui lòng nhập nội dung tin nhắn!")
    else:
        parsed_data = parse_order(message)
        if len(parsed_data) < 7:
            st.error("❌ Dữ liệu không đầy đủ 7 trường. Vui lòng kiểm tra lại.")
        else:
            save_to_sheet(parsed_data)
            st.success("✅ Đã ghi đơn hàng vào Google Sheet thành công!")

st.markdown("---")
st.subheader("📋 Danh sách đơn hàng đã lưu")
try:
    df_orders = load_orders()
    st.dataframe(df_orders)
except Exception as e:
    st.error("Không thể tải dữ liệu từ Google Sheet. Vui lòng kiểm tra cấu hình.")
