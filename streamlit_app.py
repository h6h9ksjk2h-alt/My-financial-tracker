import streamlit as nn
import pandas as pd
import os
from datetime import datetime

# ตั้งค่าหน้าเว็บ ⚙️
nn.set_page_config(page_title="Financial Tracker", layout="centered")
nn.title("🤖 Financial Tracker & Savings Dashboard")

DATA_FILE = "expenses.csv"

# โหลดข้อมูล 📁
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])

# ส่วนที่ 1: ฟอร์มกรอกข้อมูล ➕
nn.header("📝 บันทึกรายการเงิน")
with nn.form("financial_form", clear_on_submit=True):
    date_input = nn.date_input("วันที่", datetime.now())
    # "การลงทุน 📈" จะเป็นค่าเริ่มต้นตามระบบความปลอดภัยที่วางไว้
    category_input = nn.selectbox(
        "หมวดหมู่", 
        ["การลงทุน 📈", "Food 🍔", "Gasoline 🚗", "Shopping 🛍️", "Hospital 🏥", "Grocery 🛒", "For Child 👶"]
    )
    amount_input = nn.number_input("จำนวนเงิน (บาท)", min_value=0.0, step=100.0)
    desc_input = nn.text_input("รายละเอียดเพิ่มเติม")
    
    submitted = nn.form_submit_button("บันทึกรายการ")
    
    if submitted:
        new_data = pd.DataFrame([{
            "Date": date_input.strftime("%Y-%m-%d"),
            "Category": category_input,
            "Amount": amount_input,
            "Description": desc_input
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        nn.success("บันทึกข้อมูลเรียบร้อยแล้ว! 🎉")

# ส่วนที่ 2: การคำนวณและแสดงผลยอดสะสม 📊
nn.header("💰 สรุปยอดเงินสะสม")

# 🎯 ตรรกะที่แก้ไข: คำนวณยอดสะสมเฉพาะจากหมวด "การลงทุน 📈" เท่านั้น
total_savings = df[df['Category'] == "การลงทุน 📈"]['Amount'].sum()

# แสดงผลตัวเลขขนาดใหญ่บนหน้าจอ
nn.metric(label="ยอดสะสมรวมทั้งหมดของเราสองคน (จากการออมเท่านั้น) 🐻🐰", value=f"{total_savings:,.2f} บาท")

# ส่วนที่ 3: ตารางแสดงประวัติรายการ 📋
nn.header("📜 ประวัติรายการทั้งหมด")
if not df.empty:
    nn.dataframe(df.sort_values(by="Date", ascending=False))
else:
    nn.info("ยังไม่มีข้อมูลถูกบันทึกในระบบ")
