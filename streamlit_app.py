import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

# 📱 ตั้งค่าหน้าตาแอปให้เหมาะกับมือถือแนวตั้ง
st.set_page_config(
    page_title="บันทึกรายรับ-รายจ่ายของเรา",
    page_icon="🌸",
    layout="centered"
)

# 🎀 ตกแต่งความโค้งมนสไตล์ Kawaii โดยใช้ตัวแปรระบบเพื่อให้รองรับทั้ง Light และ Dark Mode อัตโนมัติ
st.markdown("""
    <style>
    /* ใช้ตัวแปรระบบ เพื่อให้สีขอบและสีปุ่มปรับตามโหมดมืด/สว่างอัตโนมัติ */
    div.stButton > button:first-child {
        border-radius: 20px;
        border: 1px solid var(--primary-color, #FFB7B2);
        background-color: var(--primary-color, #FFB7B2);
        color: white;
    }
    div[data-testid="stMetric"] {
        border-radius: 15px;
        padding: 10px;
        border: 1px solid var(--decorations-color, #FFE5B4);
    }
    div[data-testid="stForm"] {
        border-radius: 20px;
        border: 1px solid var(--decorations-color, #FFE5B4);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌸 บันทึกการเงินของเรา (Yatta! 🎉)")

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

# 🎨 ปรับเฉดสีกลุ่ม Medium-Pastel เพื่อให้โดดเด่นคมชัดทั้งบนพื้นหลังสีขาวและสีดำ
chart_colors = [
    "#FF9E9E", # อาหารและขนม 🍔 (ชมพูซากุระเข้มขึ้นนิดนึง)
    "#5C9EAD", # ค่าน้ำมันรถ 🚗 (ฟ้าพาสเทลหม่นเข้ม)
    "#B39DDB", # ช้อปปิ้ง 🛍️ (ม่วงพาสเทลเด่น)
    "#FF7043", # โรงพยาบาล/ยา 🏥 (ส้มแดงพาสเทล)
    "#FFCC80", # ของชำเข้าบ้าน 🛒 (ครีมส้มพาสเทล)
    "#FFF59D", # เพื่อลูกรัก 👶 (เหลืองพาสเทลสว่าง)
    "#81C784"  # การออมเงิน 💰 (เขียวมัทฉะพาสเทลที่คมชัดในที่มืด)
]

category_color_map = dict(zip(categories, chart_colors))

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
    if not st.session_state.expenses.empty:
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

    progress_pct = min(total_spent_this_month / budget_limit, 1.0) if budget_limit > 0 else 0.0
    display_pct = (total_spent_this_month / budget_limit) * 100 if budget_limit > 0 else 0.0

    with st.container(border=True):
        st.write("🛒 **งบประมาณกินใช้ทั่วไป (ไม่รวมการลงทุน/การออม)**")
        st.progress(progress_pct)
        st.write(f"ใช้ไปแล้ว **฿{total_spent_this_month:,.2f}** จากงบรวม **฿{budget_limit:,.2f}** ({display_pct:.1f}%)")
else:
    with st.container(border=True):
        st.write("🛒 **งบประมาณกินใช้ทั่วไป (ไม่รวมการลงทุน/การออม)**")
        st.progress(0.0)
        st.write(f"ใช้ไปแล้ว **฿0.00** จากงบรวม **฿{st.session_state.monthly_budget:,.2f}** (0.0%)")

# 📊 ส่วนแสดงผลหลอดความคืบหน้าเป้าหมายออมเงิน
with st.container(border=True):
    st.write("🍵 **ความคืบหน้าเป้าหมายเงินออมของเราประจำปี**")
    if not st.session_state.goals.empty:
        for index, row in st.session_state.goals.iterrows():
            g_name = row["Goal_Name"]
            g_target = row["Target_Amount"]
            g_init = row["Current_Savings"]
            
            if not st.session_state.expenses.empty:
                df_exp_copy = st.session_state.expenses.copy()
                df_exp_copy['Date_Parsed'] = pd.to_datetime(df_exp_copy['Date'])
                df_goal_saved = df_exp_copy[
                    (df_exp_copy['Date_Parsed'].dt.year == current_year) & 
                    (df_exp_copy['Category'] == "การออมเงิน 💰") & 
                    (df_exp_copy['Savings_Goal'] == g_name)
                ]
                total_goal_saved = df_goal_saved["Amount"].sum()
            else:
                total_goal_saved = 0.0
                
            total_savings = g_init + total_goal_saved
            progress_ratio = min(total_savings / g_target, 1.0) if g_target > 0 else 0.0
            progress_pct = progress_ratio * 100
            
            st.write(f"🔹 **{g_name}**")
            st.write(f"สะสมแล้ว **฿{total_savings:,.2f}** จากเป้าหมาย **฿{g_target:,.2f}** ({progress_pct:.1f}%)")
            st.progress(progress_ratio)

# 🐻🐰 ส่วนที่ 2: การ์ดสรุปยอดเงินสะสมทั้งหมดของทั้งคู่
if not st.session_state.expenses.empty:
    df_stats = st.session_state.expenses.copy()
    df_ado_savings = df_stats[(df_stats["User"] == "Ado") & (df_stats["Category"] == "การออมเงิน 💰")]
    df_paanpopy_savings = df_stats[(df_stats["User"] == "Paanpopy") & (df_stats["Category"] == "การออมเงิน 💰")]
    
    total_ado_savings = df_ado_savings["Amount"].sum()
    total_paanpopy_savings = df_paanpopy_savings["Amount"].sum()
    
    st.subheader("💕 ยอดเงินสะสมทั้งหมดของเราสองคน")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🐻 ยอดเงินออมของ Ado", value=f"฿{total_ado_savings:,.2f}")
    with col2:
        st.metric(label="🐰 ยอดเงินออมของ Paanpopy", value=f"฿{total_paanpopy_savings:,.2f}")

# ➕ ส่วนที่ 3: ฟอร์มกรอกข้อมูลการใช้เงิน / การออมเงิน
with st.container(border=True):
    st.subheader("✏️ บันทึกรายการเงิน")
    with st.form("expense_form", clear_on_submit=not edit_mode):
        date = st.date_input("วันที่ 📅", default_date)
        category = st.selectbox("หมวดหมู่ 🏷️", categories, index=default_cat_index)
        amount = st.number_input("จำนวนเงิน (บาท) 💵", min_value=0.0, step=1.0, value=default_amount)
        description = st.text_input("รายละเอียด/หมายเหตุ 📝", value=default_desc)
        
        goal_list = st.session_state.goals["Goal_Name"].tolist()
        if "การลงทุน 📈" not in goal_list:
            goal_list.insert(0, "การลงทุน 📈")
            
        default_g_index = goal_list.index(default_goal) if default_goal in goal_list else 0
        savings_goal = st.selectbox("🎯 ผูกกับเป้าหมายออมเงินใดจ๊ะ?", goal_list, index=default_g_index)
        
        user = st.selectbox("ใครเป็นคนจ่ายจ๊ะ? 👤", users_list, index=default_user_index)
        note = st.text_input("บันทึกเพิ่มเติม ✏️", value=default_note)
        
        submit_button = st.form_submit_button(label="บันทึกข้อมูลเรียบร้อยจ้า! (Yatta! 🎉)" if edit_mode else "บันทึกข้อมูล 🌸")

if submit_button and amount > 0:
    goal_to_save = savings_goal if category == "การออมเงิน 💰" else ""
    
    if category == "การออมเงิน 💰" and goal_to_save not in st.session_state.goals["Goal_Name"].values:
        auto_goal = pd.DataFrame([{"Goal_Name": goal_to_save, "Target_Amount": 100000.0, "Current_Savings": 0.0}])
        st.session_state.goals = pd.concat([st.session_state.goals, auto_goal], ignore_index=True)
        st.session_state.goals.to_csv(GOALS_FILE, index=False)

    if edit_mode and row_to_edit is not None:
        st.session_state.expenses.at[row_to_edit, "Date"] = date.strftime("%Y-%m-%d")
        st.session_state.expenses.at[row_to_edit, "Category"] = category
        st.session_state.expenses.at[row_to_edit, "Amount"] = amount
        st.session_state.expenses.at[row_to_edit, "Description"] = description
        st.session_state.expenses.at[row_to_edit, "User"] = user
        st.session_state.expenses.at[row_to_edit, "Note"] = str(note)
        st.session_state.expenses.at[row_to_edit, "Savings_Goal"] = goal_to_save
    else:
        new_row = pd.DataFrame([{
            "Date": date.strftime("%Y-%m-%d"), "Category": category, "Amount": amount, 
            "Description": description, "User": user, "Note": str(note), "Savings_Goal": goal_to_save
        }])
        st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
    
    st.session_state.expenses.to_csv(CSV_FILE, index=False)
    st.rerun()

# 📊 ส่วนที่ 4: แดชบอร์ดแสดงกราฟและตารางข้อมูล
st.markdown("---")

if not st.session_state.expenses.empty:
    df = st.session_state.expenses.copy()
    df['Date_Parsed'] = pd.to_datetime(df['Date'])
    
    user_filter = st.selectbox("เลือกดูข้อมูลของ:", ["ดูทั้งหมดของเรา 📊", "Ado 🐻", "Paanpopy 🐰"])
    df_filtered = df[df["User"] == user_filter.split()[0]] if "ดูทั้งหมด" not in user_filter else df

    st.subheader("📊 สรุปยอดตามช่วงเวลา")
    tab1, tab2, tab3, tab4 = st.tabs(["🗓️ สัปดาห์นี้", "📊 เดือนนี้", "📈 ไตรมาสนี้", "💰 ปีนี้"])
    
    def render_summary_tab(filtered_dataset, period_name):
        if not filtered_dataset.empty:
            with st.container(border=True):
                total = filtered_dataset["Amount"].sum()
                st.metric(label=f"รวมยอดเงินของช่วง {period_name}", value=f"฿{total:,.2f}")
                
                df_chart = filtered_dataset.groupby("Category", as_index=False)["Amount"].sum()
                fig = px.pie(
                    df_chart, values="Amount", names="Category", hole=0.4,
                    color="Category", color_discrete_map=category_color_map
                )
                # 🟢 แก้ไข: ใช้ template="none" เพื่อให้สีฟอนต์ปรับเป็น ขาว/ดำ ตามธีมของระบบโดยอัตโนมัติ
                fig.update_layout(
                    template="none",
                    margin=dict(l=10, r=10, t=10, b=10), height=240,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                # 🟢 แก้ไข: เพิ่มพารามิเตอร์ key เพื่อป้องกันไม่ให้เกิดปัญหา Duplicate Element ID
                st.plotly_chart(fig, use_container_width=True, key=f"pie_chart_{period_name}")

    with tab1: render_summary_tab(df_filtered[df_filtered['Date_Parsed'] >= start_of_week], "สัปดาห์นี้")
    with tab2: render_summary_tab(df_filtered[(df_filtered['Date_Parsed'].dt.year == current_year) & (df_filtered['Date_Parsed'].dt.month == current_month)], "เดือนนี้")
    with tab3: render_summary_tab(df_filtered[(df_filtered['Date_Parsed'].dt.year == current_year) & (((df_filtered['Date_Parsed'].dt.month - 1) // 3 + 1) == current_quarter)], "ไตรมาสนี้")
    with tab4: render_summary_tab(df_filtered[df_filtered['Date_Parsed'].dt.year == current_year], "ปีนี้")

    # 📊 กราฟแท่งแนวนอนสไตล์เรียงลำดับเวลาปัจจุบันขึ้นก่อน
    st.markdown("---")
    st.subheader("🧱 กราฟเปรียบเทียบแนวโน้มการใช้เงิน")
    
    with st.container(border=True):
        time_view = st.radio("เปรียบเทียบข้อมูลราย:", ["สัปดาห์", "เดือน", "ปี"], horizontal=True)
        df_filtered['Year'] = df_filtered['Date_Parsed'].dt.strftime('%Y')
        df_filtered['Month'] = df_filtered['Date_Parsed'].dt.strftime('%Y-%m')
        df_filtered['Week'] = df_filtered['Date_Parsed'].dt.to_period('W').dt.start_time.dt.strftime('%Y-%m-%d')

        group_col = 'Week' if time_view == "สัปดาห์" else ('Month' if time_view == "เดือน" else 'Year')
        
        df_trend = df_filtered.groupby([group_col, 'Category'], as_index=False)['Amount'].sum()
        df_trend = df_trend.sort_values(by=group_col, ascending=False)
        
        fig_bar = px.bar(
            df_trend, x="Amount", y=group_col, color="Category",
            color_discrete_map=category_color_map, orientation="h",
            labels={group_col: time_view, "Amount": "ยอดรวม (บาท)"}
        )
        # 🟢 แก้ไข: ใช้ template="none" เพื่อให้แกนและตัวอักษรกราฟแท่งแนวนอนปรับตาม Light/Dark Mode อัตโนมัติ
        fig_bar.update_layout(
            template="none",
            margin=dict(l=80, r=10, t=20, b=10), height=350, barmode='stack',
            yaxis={'categoryorder': 'array', 'categoryarray': df_trend[group_col].unique()},
            legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="trend_bar_chart_final")
else:
    st.info("ยังไม่มีข้อมูลค่าใช้จ่ายเลย เริ่มบันทึกความทรงจำการเงินของเราสองคนด้านบนได้เลยจ้า! 💖")
