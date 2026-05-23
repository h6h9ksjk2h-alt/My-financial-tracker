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

# 🎨 แก้ไข: ปรับกลุ่มสีใหม่ให้แตกต่างกันชัดเจน (High Contrast) และใช้โทนเขียวเหนี่ยวทรัพย์
chart_colors = [
    "#EF6C00", # อาหารและขนม 🍔 (ส้มเข้ม)
    "#1565C0", # ค่าน้ำมันรถ 🚗 (น้ำเงิน)
    "#6A1B9A", # ช้อปปิ้ง 🛍️ (ม่วง)
    "#C62828", # โรงพยาบาล/ยา 🏥 (แดง)
    "#00838F", # ของชำเข้าบ้าน 🛒 (ฟ้าคราม)
    "#FBC02D", # เพื่อลูกรัก 👶 (เหลืองทอง)
    "#2E7D32"  # การออมเงิน 💰 (เขียวเหนี่ยวทรัพย์)
]

# สร้างแผนผังสีระบุรายหมวดเพื่อส่งเข้ากราฟทุกตัวให้สีตรงกันเสมอ
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
        # แก้ไขจุดที่ String ขาดเรียบร้อยแล้วครับ 🟢
        st.write(f"ใช้ไปแล้ว **฿{total_spent_this_month:,.2f}** จากงบรวม **฿{budget_limit:,.2f}** ({display_pct:.1f}%)")
        
        if display_pct >= 90.0:
            st.error("🚨 อุ๊ย! งบเดือนนี้ใช้ไปเกิน 90% แล้วนะจ๊ะ ชวนกันประหยัดหน่อยน้า 💕")
        elif display_pct >= 70.0:
            st.warning("⚠️ เริ่มใช้เงินเยอะแล้วนะจ๊ะ คอยดูกระเป๋าเงินกันดีๆ น้า 🐻🐰")
        else:
            st.success("🌸 เดือนนี้เราสองคนยังควบคุมงบได้ดีเยี่ยมเลยจ้า เก่งมาก! 🎉")
else:
    with st.container(border=True):
        st.write("🛒 **งบประมาณกินใช้ทั่วไป (ไม่รวมการลงทุน/การออม)**")
        st.progress(0.0)
        st.write(f"ใช้ไปแล้ว **฿0.00** จากงบรวม **฿{st.session_state.monthly_budget:,.2f}** (0.0%)")

# 📊 ส่วนแสดงผลหลอดความคืบหน้าเป้าหมายออมเงิน (Savings Goals Tracker)
with st.container(border=True):
    st.write("🎯 **ความคืบหน้าเป้าหมายเงินออมของเราประจำปี**")
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
    else:
        st.info("ยังไม่มีเป้าหมายออมเงินในระบบ สามารถเพิ่มเป้าหมายได้ที่เมนูด้านข้างเลยจ้า!")

# 🐻🐰 ส่วนที่ 2: การ์ดสรุปยอดเงินสะสมทั้งหมดของทั้งคู่ (เฉพาะจากการออมเท่านั้น)
if not st.session_state.expenses.empty:
    df_stats = st.session_state.expenses.copy()
    
    df_ado_savings = df_stats[(df_stats["User"] == "Ado") & (df_stats["Category"] == "การออมเงิน 💰")]
    df_paanpopy_savings = df_stats[(df_stats["User"] == "Paanpopy") & (df_stats["Category"] == "การออมเงิน 💰")]
    
    total_ado_savings = df_ado_savings["Amount"].sum()
    total_paanpopy_savings = df_paanpopy_savings["Amount"].sum()
    
    st.subheader("💕 ยอดเงินสะสมทั้งหมดของเราสองคน")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.metric(label="🐻 ยอดเงินออมสะสมของ Ado", value=f"฿{total_ado_savings:,.2f}")
    with col2:
        with st.container(border=True):
            st.metric(label="🐰 ยอดเงินออมสะสมของ Paanpopy", value=f"฿{total_paanpopy_savings:,.2f}")

# ➕ ส่วนที่ 3: ฟอร์มกรอกข้อมูลการใช้เงิน / การออมเงิน
with st.container(border=True):
    if edit_mode:
        st.subheader(f"✏️ แก้ไขข้อมูล (แถวที่ {row_to_edit})")
        form_label = "บันทึกการเปลี่ยนแปลง ✨"
    else:
        st.subheader("➕ บันทึกค่าใช้จ่าย/การออมใหม่")
        form_label = "บันทึกข้อมูล 💖"

    with st.form("expense_form", clear_on_submit=not edit_mode):
        date = st.date_input("วันที่ 📅", default_date)
        category = st.selectbox("หมวดหมู่ 🏷️", categories, index=default_cat_index)
        amount = st.number_input("จำนวนเงิน (บาท) 💵", min_value=0.0, step=1.0, value=default_amount)
        description = st.text_input("รายละเอียด/หมายเหตุ 📝", value=default_desc, placeholder="ซื้อของกินเข้าบ้าน / ออมหุ้น")
        
        goal_list = st.session_state.goals["Goal_Name"].tolist()
        if "การลงทุน 📈" not in goal_list:
            goal_list.insert(0, "การลงทุน 📈")
            
        default_g_index = goal_list.index(default_goal) if default_goal in goal_list else 0
        savings_goal = st.selectbox("🎯 หากเป็นการออมเงิน ผูกกับเป้าหมายใดจ๊ะ?", goal_list, index=default_g_index)
        
        user = st.selectbox("ใครเป็นคนจ่ายจ๊ะ? 👤", users_list, index=default_user_index)
        note = st.text_input("โน้ตสั้นจากใจ/บันทึกเพิ่มเติม ✏️", value=default_note, placeholder="มื้อนี้ Ado เลี้ยงนะจ๊ะ")
        
        submit_button = st.form_submit_button(label=form_label)

if submit_button:
    if amount > 0:
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
            st.success("แก้ไขข้อมูลเรียบร้อยแล้วจ้า! ✨")
        else:
            new_row = pd.DataFrame([{
                "Date": date.strftime("%Y-%m-%d"), "Category": category, "Amount": amount, 
                "Description": description, "User": user, "Note": str(note), "Savings_Goal": goal_to_save
            }])
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
            st.success(f"บันทึกข้อมูลของ {user} เรียบร้อยแล้วจ้า! 🎈")
        
        st.session_state.expenses.to_csv(CSV_FILE, index=False)
        st.rerun()
    else:
        st.warning("กรุณากรอกจำนวนเงินที่มากกว่า 0 นะจ๊ะ")

# 📊 ส่วนที่ 4: แดชบอร์ดแสดงกราฟและตารางข้อมูล
st.markdown("---")

if not st.session_state.expenses.empty:
    df = st.session_state.expenses.copy()
    df['Date_Parsed'] = pd.to_datetime(df['Date'])
    df["User"] = df["User"].fillna("Unknown")
    df["Note"] = df["Note"].fillna("")
    df["Savings_Goal"] = df["Savings_Goal"].fillna("")

    st.subheader("🔍 ตัวกรองแดชบอร์ด")
    user_filter = st.selectbox("เลือกดูข้อมูลของ:", ["ดูทั้งหมดของเรา 📊", "Ado 🐻", "Paanpopy 🐰"])
    
    if user_filter == "Ado 🐻":
        df_filtered = df[df["User"] == "Ado"]
    elif user_filter == "Paanpopy 🐰":
        df_filtered = df[df["User"] == "Paanpopy"]
    else:
        df_filtered = df

    st.subheader(f"📊 สรุปยอดตามช่วงเวลา")
    tab1, tab2, tab3, tab4 = st.tabs(["🗓️ สัปดาห์นี้", "📊 เดือนนี้", "📈 ไตรมาสนี้", "💰 ปีนี้"])
    
    def render_summary_tab(filtered_dataset, period_name):
        if filtered_dataset.empty:
            st.info(f"ยังไม่มีข้อมูลบันทึกในส่วนของ {period_name} เลยจ้า")
        else:
            with st.container(border=True):
                total = filtered_dataset["Amount"].sum()
                
                if period_name == "เดือนนี้":
                    first_day_this_month = today.replace(day=1)
                    last_day_last_month = first_day_this_month - timedelta(days=1)
                    lm_month = last_day_last_month.month
                    lm_year = last_day_last_month.year
                    
                    df_all_budget = st.session_state.expenses.copy()
                    df_all_budget['Date_Parsed'] = pd.to_datetime(df_all_budget['Date'])
                    
                    if user_filter == "Ado 🐻":
                        df_lm = df_all_budget[df_all_budget["User"] == "Ado"]
                    elif user_filter == "Paanpopy 🐰":
                        df_lm = df_all_budget[df_all_budget["User"] == "Paanpopy"]
                    else:
                        df_lm = df_all_budget
                        
                    df_lm_filtered = df_lm[
                        (df_lm['Date_Parsed'].dt.year == lm_year) & 
                        (df_lm['Date_Parsed'].dt.month == lm_month) & 
                        (df_lm['Category'] != "การออมเงิน 💰")
                    ]
                    total_last_month = df_lm_filtered["Amount"].sum()
                    
                    total_spent_now = filtered_dataset[filtered_dataset["Category"] != "การออมเงิน 💰"]["Amount"].sum()
                    amount_diff = total_spent_now - total_last_month
                    
                    if total_last_month > 0:
                        pct_change = (amount_diff / total_last_month) * 100
                    else:
                        pct_change = 0.0
                        
                    st.metric(
                        label=f"รวมยอดกินใช้ทั่วไป ({period_name})", 
                        value=f"฿{total_spent_now:,.2f}",
                        delta=f"฿{amount_diff:,.2f} ({pct_change:+.1f}%) จากเดือนที่แล้ว",
                        delta_color="inverse"
                    )
                    
                    total_invest_now = filtered_dataset[filtered_dataset["Category"] == "การออมเงิน 💰"]["Amount"].sum()
                    if total_invest_now > 0:
                        st.caption(f"📈 *ในเดือนนี้มีการเก็บออมเพิ่มอีก ฿{total_invest_now:,.2f} (ยอดรวมทุกหมวดหมู่: ฿{total:,.2f})*")
                else:
                    st.metric(label=f"รวมยอดที่จ่าย ({period_name})", value=f"฿{total:,.2f}")
                
                df_chart = filtered_dataset.groupby("Category", as_index=False)["Amount"].sum()
                
                # ส่ง color_discrete_map ไปที่แผนภูมิวงกลมเพื่อให้รหัสสีตรงกัน
                fig = px.pie(
                    df_chart, values="Amount", names="Category", hole=0.4,
                    color="Category", color_discrete_map=category_color_map
                )
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10), height=240, showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig, use_container_width=True, key=f"pie_{period_name}_{user_filter}")
                
                display_df = filtered_dataset[["Date", "Category", "Amount", "Description", "User", "Note", "Savings_Goal"]].copy()
                display_df["Note"] = display_df["Note"].replace("nan", "")
                display_df["Savings_Goal"] = display_df["Savings_Goal"].replace("", "-")
                display_df.columns = ["วันที่", "หมวดหมู่", "จำนวนเงิน (บาท)", "รายละเอียด", "คนจ่าย", "บันทึกเพิ่มเติม", "เป้าหมายการออม"]
                st.dataframe(display_df, use_container_width=True)

    with tab1:
        render_summary_tab(df_filtered[df_filtered['Date_Parsed'] >= start_of_week], "สัปดาห์นี้")
    with tab2:
        render_summary_tab(df_filtered[(df_filtered['Date_Parsed'].dt.year == current_year) & (df_filtered['Date_Parsed'].dt.month == current_month)], "เดือนนี้")
    with tab3:
        render_summary_tab(df_filtered[(df_filtered['Date_Parsed'].dt.year == current_year) & (((df_filtered['Date_Parsed'].dt.month - 1) // 3 + 1) == current_quarter)], "ไตรมาสนี้")
    with tab4:
        render_summary_tab(df_filtered[df_filtered['Date_Parsed'].dt.year == current_year], "ปีนี้")

    st.markdown("---")
    st.subheader("🧱 กราฟเปรียบเทียบแนวโน้มการใช้เงิน")
    
    if not df_filtered.empty:
        with st.container(border=True):
            time_view = st.radio("เปรียบเทียบข้อมูลราย:", ["สัปดาห์", "เดือน", "ปี"], horizontal=True, key="time_view_radio")
            
            df_filtered['Year'] = df_filtered['Date_Parsed'].dt.strftime('%Y')
            df_filtered['Month'] = df_filtered['Date_Parsed'].dt.strftime('%Y-%m')
            df_filtered['Week'] = df_filtered['Date_Parsed'].dt.to_period('W').dt.start_time.dt.strftime('%Y-%m-%d')

            if time_view == "สัปดาห์":
                group_col = 'Week'
                lbl = "สัปดาห์ที่เริ่มต้น"
            elif time_view == "เดือน":
                group_col = 'Month'
                lbl = "เดือน"
            else:
                group_col = 'Year'
                lbl = "ปี"
                
            df_trend = df_filtered.groupby([group_col, 'Category'], as_index=False)['Amount'].sum()
            
            # เรียงลำดับช่วงเวลาจากใหม่ไปเก่า (ปัจจุบันอยู่บนสุด)
            df_trend = df_trend.sort_values(by=group_col, ascending=False)
            
            # 📊 ปรับปรุงโครงสร้างกราฟแท่งแนวนอน (Horizontal) และส่งแผนผังสีที่ถูกต้องลงไป
            fig_bar = px.bar(
                df_trend, x="Amount", y=group_col, color="Category",
                color_discrete_map=category_color_map, 
                orientation="h",
                labels={group_col: lbl, "Amount": "ยอดรวม (บาท)"}
            )
            fig_bar.update_layout(
                margin=dict(l=80, r=10, t=20, b=10), height=350, barmode='stack',
                yaxis={'categoryorder': 'array', 'categoryarray': df_trend[group_col].unique()},
                legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_bar, use_container_width=True, key=f"trend_bar_{user_filter}")
else:
    st.info("ยังไม่มีข้อมูลค่าใช้จ่ายเลย เริ่มบันทึกความทรงจำการเงินของเราสองคนด้านบนได้เลยจ้า! 💖")
