import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

# 📱 ตั้งค่าหน้าตาแอปให้เหมาะกับมือถือ
st.set_page_config(
    page_title="บันทึกรายรับ-รายจ่ายของเรา",
    page_icon="💝",
    layout="centered"
)

st.title("💝 บันทึกการเงินของเรา")

# 📂 กำหนดชื่อไฟล์สำหรับบันทึกข้อมูล
CSV_FILE = "expenses.csv"
BUDGET_FILE = "budget.txt"
GOALS_FILE = "goals.csv"

# 🗄️ โครงสร้างหน่วยความจำระบบสำหรับเป้าหมายเงินออม
if os.path.exists(GOALS_FILE):
    st.session_state.goals = pd.read_csv(GOALS_FILE)
    st.session_state.goals["Target_Amount"] = st.session_state.goals["Target_Amount"].astype(float)
    st.session_state.goals["Current_Savings"] = st.session_state.goals["Current_Savings"].astype(float)
else:
    st.session_state.goals = pd.DataFrame([
        {"Goal_Name": "การลงทุน 📈", "Target_Amount": 100000.0, "Current_Savings": 0.0}
    ])
    st.session_state.goals.to_csv(GOALS_FILE, index=False)

# 🗄️ โครงสร้างหน่วยความจำระบบของข้อมูลค่าใช้จ่าย
if os.path.exists(CSV_FILE):
    st.session_state.expenses = pd.read_csv(CSV_FILE)
    st.session_state.expenses["Amount"] = st.session_state.expenses["Amount"].astype(float)
    
    if "Note" not in st.session_state.expenses.columns:
        st.session_state.expenses["Note"] = ""
    else:
        st.session_state.expenses["Note"] = st.session_state.expenses["Note"].astype(str)
        
    if "Savings_Goal" not in st.session_state.expenses.columns:
        st.session_state.expenses["Savings_Goal"] = ""
    else:
        st.session_state.expenses["Savings_Goal"] = st.session_state.expenses["Savings_Goal"].fillna("").astype(str)
else:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Description", "User", "Note", "Savings_Goal"])
    st.session_state.expenses["Note"] = st.session_state.expenses["Note"].astype(str)
    st.session_state.expenses["Savings_Goal"] = st.session_state.expenses["Savings_Goal"].astype(str)

# 🧠 ระบบจำค่างบประมาณรายเดือน
if "monthly_budget" not in st.session_state:
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r", encoding="utf-8") as f:
            try:
                st.session_state.monthly_budget = float(f.read().strip())
            except ValueError:
                st.session_state.monthly_budget = 20000.0
    else:
        st.session_state.monthly_budget = 20000.0
        with open(BUDGET_FILE, "w", encoding="utf-8") as f:
            f.write(str(st.session_state.monthly_budget))

# 🏷️ หมวดหมู่และรายชื่อผู้ใช้งาน
categories = [
    "อาหารและขนม 🍔", 
    "ค่าน้ำมันรถ 🚗", 
    "ช้อปปิ้ง 🛍️", 
    "โรงพยาบาล/ยา 🏥", 
    "ของชำเข้าบ้าน 🛒", 
    "เพื่อลูกรัก 👶", 
    "การออมเงิน 💰"
]
users_list = ["Ado", "Paanpopy"]

# 🎨 แก้ไข: ปรับกลุ่มสีใหม่ให้แตกต่างกันชัดเจน (High Contrast) บนจอมือถือ
chart_colors = [
    "#EF6C00", # อาหารและขนม 🍔 (ส้มเข้ม)
    "#1565C0", # ค่าน้ำมันรถ 🚗 (น้ำเงิน)
    "#6A1B9A", # ช้อปปิ้ง 🛍️ (ม่วง)
    "#C62828", # โรงพยาบาล/ยา 🏥 (แดง)
    "#00838F", # ของชำเข้าบ้าน 🛒 (ฟ้าคราม)
    "#FBC02D", # เพื่อลูกรัก 👶 (เหลืองทอง)
    "#2E7D32"  # การออมเงิน 💰 (เขียวเหนี่ยวทรัพย์) <-- นี่คือสีที่เราตกลงกันครับ
]

# 🛠️ เมนูด้านข้าง (Sidebar)
st.sidebar.header("⚙️ ตั้งค่าแอป")

new_budget = st.sidebar.number_input(
    "🎯 งบประมาณรวมประจำเดือน (บาท)",
    min_value=0.0,
    value=st.session_state.monthly_budget,
    step=500.0
)

if new_budget != st.session_state.monthly_budget:
    st.session_state.monthly_budget = new_budget
    with open(BUDGET_FILE, "w", encoding="utf-8") as f:
        f.write(str(new_budget))
    st.rerun()

# 🎯 ฟอร์มเพิ่มเป้าหมายออมเงินใหม่ใน Sidebar
with st.sidebar.form("goal_form", clear_on_submit=True):
    st.subheader("🎯 ตั้งเป้าหมายออมเงิน")
    goal_name = st.text_input("ชื่อเป้าหมาย (เช่น ทริปญี่ปุ่น) ✈️")
    target_amount = st.number_input("จำนวนเงินเป้าหมาย (บาท) 💰", min_value=0.0, step=1000.0)
    current_savings = st.number_input("เงินสะสมเริ่มต้น (บาท) 🧱", min_value=0.0, step=500.0)
    
    submit_goal = st.form_submit_button("บันทึกเป้าหมาย 💖")

if submit_goal:
    if goal_name and target_amount > 0:
        new_goal = pd.DataFrame([{
            "Goal_Name": goal_name,
            "Target_Amount": target_amount,
            "Current_Savings": current_savings
        }])
        st.session_state.goals = pd.concat([st.session_state.goals, new_goal], ignore_index=True)
        st.session_state.goals.to_csv(GOALS_FILE, index=False)
        st.sidebar.success(f"บันทึกเป้าหมาย '{goal_name}' เรียบร้อยแล้วจ้า! 🎉")
        st.rerun()
    else:
        st.sidebar.warning("กรุณากรอกชื่อเป้าหมายและจำนวนเงินที่มากกว่า 0 นะจ๊ะ")

edit_mode = st.sidebar.checkbox("📝 เปิดโหมดแก้ไขข้อมูล")

default_date = datetime.now()
default_cat_index = 0
default_amount = 0.0
default_desc = ""
default_user_index = 0
default_note = ""
default_goal = "การลงทุน 📈"
row_to_edit = None

if edit_mode:
    if st.session_state.expenses.empty:
        st.sidebar.warning("⚠️ ยังไม่มีข้อมูลค่าใช้จ่าย ลองเพิ่มข้อมูลก่อนนะจ๊ะ!")
        edit_mode = False
    else:
        st.sidebar.subheader("✏️ เลือกแถวที่ต้องการแก้ไข")
        row_to_edit = st.sidebar.number_input("ระบุเลขแถว", min_value=0, max_value=len(st.session_state.expenses)-1, step=1)
        
        old_row = st.session_state.expenses.iloc[row_to_edit]
        default_date = datetime.strptime(str(old_row['Date']), "%Y-%m-%d")
        if old_row['Category'] in categories:
            default_cat_index = categories.index(old_row['Category'])
        default_amount = float(old_row['Amount'])
        default_desc = str(old_row['Description'])
        if "User" in old_row and old_row['User'] in users_list:
            default_user_index = users_list.index(old_row['User'])
        if "Note" in old_row:
            default_note = str(old_row['Note']) if pd.notna(old_row['Note']) and str(old_row['Note']) != "nan" else ""
        if "Savings_Goal" in old_row and str(old_row['Savings_Goal']) != "nan" and str(old_row['Savings_Goal']) != "":
            default_goal = str(old_row['Savings_Goal'])

st.sidebar.markdown("---")
st.sidebar.subheader("📥 ดาวน์โหลดข้อมูล")

if not st.session_state.expenses.empty:
    csv_data = st.session_state.expenses.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Download Expenses CSV",
        data=csv_data, file_name="our_expenses.csv", mime="text/csv", use_container_width=True
    )

today = datetime.now()
current_year = today.year
current_month = today.month
current_quarter = (today.month - 1) // 3 + 1
start_of_week = today - timedelta(days=7)

# 🎯 ส่วนที่ 1: งบประมาณรายเดือน และระบบ Savings Goals Tracker
st.subheader(f"📊 สรุปงบประจำเดือน {current_month}/{current_year}")

if not st.session_state.expenses.empty:
    df_budget = st.session_state.expenses.copy()
    df_budget['Date_Parsed'] = pd.to_datetime(df_budget['Date'])
    
    df_this_month = df_budget[
        (df_budget['Date_Parsed'].dt.year == current_year) & 
        (df_budget['Date_Parsed'].dt.month == current_month) & 
        (df_budget['Category'] != "การออมเงิน 💰")
    ]
    total_spent_this_month = df_this_month["Amount"].sum()
    budget_limit = st.session_state.monthly_budget

    if budget_limit > 0:
        progress_pct = min(total_spent_this_month / budget_limit, 1.0)
        display_pct = (total_spent_this_month / budget_limit) * 100
    else:
        progress_pct = 0.0
        display_pct = 0.0

    with st.container(border=True):
        st.write("🛒 **งบประมาณกินใช้ทั่วไป (ไม่รวมการลงทุน/การออม)**")
        st.progress(progress_pct)
        st.write(f"ใช้ไปแล้ว **฿{total_spent_this_month:,.2f}http://googleusercontent.com/generated_image_content/0
