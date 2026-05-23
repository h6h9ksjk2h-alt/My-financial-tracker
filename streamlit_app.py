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

# 🗄️ โครงสร้างหน่วยความจำระบบ (session_state) พร้อมล็อกประเภทข้อมูลข้อความ (String) สำหรับ Note
if os.path.exists(CSV_FILE):
    st.session_state.expenses = pd.read_csv(CSV_FILE)
    st.session_state.expenses["Amount"] = st.session_state.expenses["Amount"].astype(float)
    
    if "Note" not in st.session_state.expenses.columns:
        st.session_state.expenses["Note"] = ""
    else:
        st.session_state.expenses["Note"] = st.session_state.expenses["Note"].astype(str)
else:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Description", "User", "Note"])
    st.session_state.expenses["Note"] = st.session_state.expenses["Note"].astype(str)

# 🧠 ระบบจำค่างบประมาณรายเดือนเริ่มต้น (20,000 บาท)
if "monthly_budget" not in st.session_state:
    st.session_state.monthly_budget = 20000.0

# 🏷️ หมวดหมู่และรายชื่อผู้ใช้งาน
categories = [
    "อาหารและขนม 🍔", 
    "ค่าน้ำมันรถ 🚗", 
    "ช้อปปิ้ง 🛍️", 
    "โรงพยาบาล/ยา 🏥", 
    "ของชำเข้าบ้าน 🛒", 
    "เพื่อลูกรัก 👶", 
    "การลงทุน 📈"
]
users_list = ["Ado", "Paanpopy"]

# 🎀 โทนสีพาสเทลสุดน่ารัก
chart_colors = ["#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", "#FFC6FF", "#BFFCC6"]

# 🛠️ เมนูด้านข้าง (Sidebar)
st.sidebar.header("⚙️ ตั้งค่าแอป")

st.session_state.monthly_budget = st.sidebar.number_input(
    "🎯 งบประมาณรวมประจำเดือน (บาท)",
    min_value=0.0,
    value=st.session_state.monthly_budget,
    step=500.0
)

edit_mode = st.sidebar.checkbox("📝 เปิดโหมดแก้ไขข้อมูล")

default_date = datetime.now()
default_cat_index = 0
default_amount = 0.0
default_desc = ""
default_user_index = 0
default_note = ""
row_to_edit = None

if edit_mode:
    if st.session_state.expenses.empty:
        st.sidebar.warning("⚠️ ยังไม่มีข้อมูลค่าใช้จ่าย ลองเพิ่มข้อมูลก่อนนะจ๊ะ!")
        edit_mode = False
    else:
        st.sidebar.subheader("✏️ เลือกแถวที่ต้องการแก้ไข")
        row_to_edit = st.sidebar.number_input(
            "ระบุเลขแถว", 
            min_value=0, 
            max_value=len(st.session_state.expenses)-1, 
            step=1
        )
        
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
            
        st.sidebar.info(f"ดึงข้อมูลแถวที่ {row_to_edit} มาแล้ว แก้ไขในฟอร์มหลักได้เลย")

st.sidebar.markdown("---")
st.sidebar.subheader("📥 ดาวน์โหลดข้อมูล")

if not st.session_state.expenses.empty:
    csv_data = st.session_state.expenses.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Download Expenses CSV",
        data=csv_data,
        file_name="our_expenses.csv",
        mime="text/csv",
        use_container_width=True
    )

today = datetime.now()
current_year = today.year
current_month = today.month
current_quarter = (today.month - 1) // 3 + 1
start_of_week = today - timedelta(days=7)

# 🎯 ส่วนที่ 1: งบประมาณรายเดือน และการ์ดแยกเงินลงทุน
st.subheader(f"📊 สรุปงบประจำเดือน {current_month}/{current_year}")

if not st.session_state.expenses.empty:
    df_budget = st.session_state.expenses.copy()
    df_budget['Date_Parsed'] = pd.to_datetime(df_budget['Date'])
    
    # 🛒 1. กรองเดือนปัจจุบันแบบ "ไม่รวม" การลงทุน เพื่อคิดงบกินใช้ทั่วไป
    df_this_month = df_budget[
        (df_budget['Date_Parsed'].dt.year == current_year) & 
        (df_budget['Date_Parsed'].dt.month == current_month) & 
        (df_budget['Category'] != "การลงทุน 📈")
    ]
    total_spent_this_month = df_this_month["Amount"].sum()
    budget_limit = st.session_state.monthly_budget

    # 📈 2. กรองเดือนปัจจุบันแบบ "เลือกเฉพาะ" การลงทุน
    df_investment_this_month = df_budget[
        (df_budget['Date_Parsed'].dt.year == current_year) & 
        (df_budget['Date_Parsed'].dt.month == current_month) & 
        (df_budget['Category'] == "การลงทุน 📈")
    ]
    total_investment_this_month = df_investment_this_month["Amount"].sum()

    if budget_limit > 0:
        progress_pct = min(total_spent_this_month / budget_limit, 1.0)
        display_pct = (total_spent_this_month / budget_limit) * 100
    else:
        progress_pct = 0.0
        display_pct = 0.0

    # แสดงผลหลอดงบกินใช้ทั่วไป
    with st.container(border=True):
        st.write("🛒 **งบประมาณกินใช้ทั่วไป (ไม่รวมการลงทุน)**")
        st.progress(progress_pct)
        st.write(f"ใช้ไปแล้ว **฿{total_spent_this_month:,.2f}** จากงบรวม **฿{budget_limit:,.2f}** ({display_pct:.1f}%)")
        
        if display_pct >= 90.0:
            st.error("🚨 อุ๊ย! งบเดือนนี้ใช้ไปเกิน 90% แล้วนะจ๊ะ ชวนกันประหยัดหน่อยน้า 💕")
        elif display_pct >= 70.0:
            st.warning("⚠️ เริ่มใช้เงินเยอะแล้วนะจ๊ะ คอยดูกระเป๋าเงินกันดีๆ น้า 🐻🐰")
        else:
            st.success("🌸 เดือนนี้เราสองคนยังควบคุมงบได้ดีเยี่ยมเลยจ้า เก่งมาก! 🎉")

    # 🌟 แสดงการ์ดเงินลงทุนแยกออกมาด้านล่างหลอดงบประมาณ
    with st.container(border=True):
        st.metric(label="📈 ยอดเงินลงทุนสะสมเดือนนี้", value=f"฿{total_investment_this_month:,.2f}")
else:
    with st.container(border=True):
        st.write("🛒 **งบประมาณกินใช้ทั่วไป (ไม่รวมการลงทุน)**")
        st.progress(0.0)
        st.write(f"ใช้ไปแล้ว **฿0.00** จากงบรวม **฿{st.session_state.monthly_budget:,.2f}** (0.0%)")
    with st.container(border=True):
        st.metric(label="📈 ยอดเงินลงทุนสะสมเดือนนี้", value="฿0.00")

# 🐻🐰 ส่วนที่ 2: การ์ดสรุปยอดเงินรวมทั้งหมดของทั้งคู่
if not st.session_state.expenses.empty:
    df_stats = st.session_state.expenses.copy()
    total_ado = df_stats[df_stats["User"] == "Ado"]["Amount"].sum()
    total_paanpopy = df_stats[df_stats["User"] == "Paanpopy"]["Amount"].sum()
    
    st.subheader("💕 ยอดสะสมทั้งหมดของเราสองคน")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.metric(label="🐻 ยอดรวมของ Ado", value=f"฿{total_ado:,.2f}")
    with col2:
        with st.container(border=True):
            st.metric(label="🐰 ยอดรวมของ Paanpopy", value=f"฿{total_paanpopy:,.2f}")

# ➕ ส่วนที่ 3: ฟอร์มกรอกข้อมูลการใช้เงินพร้อมช่องบันทึกเพิ่มเติม
with st.container(border=True):
    if edit_mode:
        st.subheader(f"✏️ แก้ไขข้อมูล (แถวที่ {row_to_edit})")
        form_label = "บันทึกการเปลี่ยนแปลง ✨"
    else:
        st.subheader("➕ บันทึกค่าใช้จ่ายใหม่")
        form_label = "บันทึกข้อมูล 💖"

    with st.form("expense_form", clear_on_submit=not edit_mode):
        date = st.date_input("วันที่ 📅", default_date)
        category = st.selectbox("หมวดหมู่ 🏷️", categories, index=default_cat_index)
        amount = st.number_input("จำนวนเงิน (บาท) 💵", min_value=0.0, step=1.0, value=default_amount)
        description = st.text_input("รายละเอียด/หมายเหตุ 📝", value=default_desc, placeholder="เช่น ซื้อของกินเข้าบ้าน")
        user = st.selectbox("ใครเป็นคนจ่ายจ๊ะ? 👤", users_list, index=default_user_index)
        note = st.text_input("โน้ตสั้นจากใจ/บันทึกเพิ่มเติม ✏️", value=default_note, placeholder="เช่น มื้อนี้ Ado เลี้ยงนะจ๊ะ")
        
        submit_button = st.form_submit_button(label=form_label)

if submit_button:
    if amount > 0:
        if edit_mode and row_to_edit is not None:
            st.session_state.expenses.at[row_to_edit, "Date"] = date.strftime("%Y-%m-%d")
            st.session_state.expenses.at[row_to_edit, "Category"] = category
            st.session_state.expenses.at[row_to_edit, "Amount"] = amount
            st.session_state.expenses.at[row_to_edit, "Description"] = description
            st.session_state.expenses.at[row_to_edit, "User"] = user
            st.session_state.expenses.at[row_to_edit, "Note"] = str(note)
            st.success("แก้ไขข้อมูลเรียบร้อยแล้วจ้า! ✨")
        else:
            new_row = pd.DataFrame([{
                "Date": date.strftime("%Y-%m-%d"), 
                "Category": category, 
                "Amount": amount, 
                "Description": description,
                "User": user,
                "Note": str(note)
            }])
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
            st.success(f"บันทึกรายจ่ายของ {user} เรียบร้อยแล้วจ้า! 🎈")
        
        st.session_state.expenses.to_csv(CSV_FILE, index=False)
        st.rerun()
    else:
        st.warning("กรุณากรอกจำนวนเงินที่มากกว่า 0 นะจ๊ะ")

# 📊 ส่วนที่ 4: แดชบอร์ดแสดงกราฟและตารางข้อมูล
st.markdown("---")

if not st.session_state.expenses.empty:
    df = st.session_state.expenses.copy()
    df['Date_Parsed'] = pd.to_datetime(df['Date'])
    
    if "User" not in df.columns:
        df["User"] = "Unknown"
    df["User"] = df["User"].fillna("Unknown")
    if "Note" not in df.columns:
        df["Note"] = ""
    df["Note"] = df["Note"].fillna("")

    st.subheader("🔍 ตัวกรองแดชบอร์ด")
    user_filter = st.selectbox(
        "เลือกดูข้อมูลของ:",
        ["ดูทั้งหมดของเรา 📊", "Ado 🐻", "Paanpopy 🐰"]
    )
    
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
                st.metric(label=f"รวมยอดที่จ่าย ({period_name})", value=f"฿{total:,.2f}")
                
                df_chart = filtered_dataset.groupby("Category", as_index=False)["Amount"].sum()
                fig = px.pie(
                    df_chart, values="Amount", names="Category", hole=0.4,
                    color_discrete_sequence=chart_colors
                )
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10), height=240, showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig, use_container_width=True, key=f"pie_{period_name}_{user_filter}")
                
                display_df = filtered_dataset[["Date", "Category", "Amount", "Description", "User", "Note"]].copy()
                display_df["Note"] = display_df["Note"].replace("nan", "")
                display_df.columns = ["วันที่", "หมวดหมู่", "จำนวนเงิน (บาท)", "รายละเอียด", "คนจ่าย", "บันทึกเพิ่มเติม"]
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
            time_view = st.radio(
                "เปรียบเทียบข้อมูลราย:",
                ["สัปดาห์", "เดือน", "ปี"],
                horizontal=True,
                key="time_view_radio"
            )
            
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
            
            fig_bar = px.bar(
                df_trend,
                x=group_col,
                y="Amount",
                color="Category",
                color_discrete_sequence=chart_colors,
                labels={group_col: lbl, "Amount": "ยอดรวม (บาท)"}
            )
            fig_bar.update_layout(
                margin=dict(l=10, r=10, t=20, b=10),
                height=300,
                barmode='stack',
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_bar, use_container_width=True, key=f"trend_bar_{user_filter}")
    else:
        st.info("ยังไม่มีข้อมูลเพียงพอในการแสดงกราฟแนวโน้มจ้า")

else:
    st.info("ยังไม่มีข้อมูลค่าใช้จ่ายเลย เริ่มบันทึกความทรงจำการเงินของเราสองคนด้านบนได้เลยจ้า! 💖")
