import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

# 📱 Page configuration for a clean mobile look
st.set_page_config(
    page_title="Our Finance Tracker",
    page_icon="💝",
    layout="centered"
)

st.title("💝 Our Shared Finance Tracker")

# 📂 Define the local storage file name
CSV_FILE = "expenses.csv"

# 🗄️ Permanent Storage Logic: Load data from CSV or initialize a new one
if os.path.exists(CSV_FILE):
    st.session_state.expenses = pd.read_csv(CSV_FILE)
    st.session_state.expenses["Amount"] = st.session_state.expenses["Amount"].astype(float)
else:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Description", "User"])

categories = ["Food", "Gasoline", "Shopping", "Hospital", "Grocery", "For Child"]
users_list = ["Ado", "Paanpopy"]

# 🎀 Brand New Sweet Pastel Palette for a cute aesthetic
chart_colors = ["#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", "#FFC6FF"]

# 🛠️ Sidebar Control Panel
st.sidebar.header("⚙️ App Controls")
edit_mode = st.sidebar.checkbox("📝 Enable Edit Mode")

# Initialize default values for the input form
default_date = datetime.now()
default_cat_index = 0
default_amount = 0.0
default_desc = ""
default_user_index = 0
row_to_edit = None

# 🔍 Safety Check & Lookup Logic for Edit Mode
if edit_mode:
    if st.session_state.expenses.empty:
        st.sidebar.warning("⚠️ No expenses recorded yet. Add an expense first!")
        edit_mode = False
    else:
        st.sidebar.subheader("✏️ Select Row to Edit")
        row_to_edit = st.sidebar.number_input(
            "Enter Row Number to Edit", 
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
        st.sidebar.info(f"Loaded Row {row_to_edit}. Modify details in the main form.")

# 📥 Data Export Section inside the Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Export Data")

if not st.session_state.expenses.empty:
    csv_data = st.session_state.expenses.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Download Expenses CSV",
        data=csv_data,
        file_name="our_expenses.csv",
        mime="text/csv",
        use_container_width=True
    )

# 🐻🐰 SECTION 1: Couple Quick-Stats right at the top
if not st.session_state.expenses.empty:
    df_stats = st.session_state.expenses.copy()
    
    # Calculate totals for each person safely
    total_ado = df_stats[df_stats["User"] == "Ado"]["Amount"].sum()
    total_paanpopy = df_stats[df_stats["User"] == "Paanpopy"]["Amount"].sum()
    
    st.subheader("💕 Our Quick-Stats")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.metric(label="🐻 Ado's Total", value=f"฿{total_ado:.2f}")
            
    with col2:
        with st.container(border=True):
            st.metric(label="🐰 Paanpopy's Total", value=f"฿{total_paanpopy:.2f}")

# ➕ Main Form Section wrapped in a modern card container
with st.container(border=True):
    if edit_mode:
        st.subheader(f"✏️ Modify Expense (Row {row_to_edit})")
        form_label = "Save Changes"
    else:
        st.subheader("➕ Add New Expense")
        form_label = "Add Expense"

    with st.form("expense_form", clear_on_submit=not edit_mode):
        date = st.date_input("Date", default_date)
        category = st.selectbox("Category 🏷️", categories, index=default_cat_index)
        amount = st.number_input("Amount (฿) 💵", min_value=0.0, step=1.0, value=default_amount)
        description = st.text_input("Description 📝", value=default_desc)
        user = st.selectbox("Paid By 👤", users_list, index=default_user_index)
        
        submit_button = st.form_submit_button(label=form_label)

if submit_button:
    if amount > 0:
        if edit_mode and row_to_edit is not None:
            st.session_state.expenses.at[row_to_edit, "Date"] = date.strftime("%Y-%m-%d")
            st.session_state.expenses.at[row_to_edit, "Category"] = category
            st.session_state.expenses.at[row_to_edit, "Amount"] = amount
            st.session_state.expenses.at[row_to_edit, "Description"] = description
            st.session_state.expenses.at[row_to_edit, "User"] = user
            st.success("Updated successfully! ✨")
        else:
            new_row = pd.DataFrame([{
                "Date": date.strftime("%Y-%m-%d"), 
                "Category": category, 
                "Amount": amount, 
                "Description": description,
                "User": user
            }])
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
            st.success(f"Added successfully! ✨")
        
        st.session_state.expenses.to_csv(CSV_FILE, index=False)
        st.rerun()
    else:
        st.warning("Please enter an amount greater than 0.")

# 📊 Visual Dashboard Section
st.markdown("---")

if not st.session_state.expenses.empty:
    df = st.session_state.expenses.copy()
    df['Date_Parsed'] = pd.to_datetime(df['Date'])
    
    if "User" not in df.columns:
        df["User"] = "Unknown"
    df["User"] = df["User"].fillna("Unknown")

    today = datetime.now()
    current_year = today.year
    current_month = today.month
    current_quarter = (today.month - 1) // 3 + 1
    start_of_week = today - timedelta(days=7)

    # 🔍 Interactive Dashboard Filter
    st.subheader("🔍 Filter Dashboard View")
    user_filter = st.selectbox(
        "Show data for:",
        ["All Entries 📊", "Ado 🐻", "Paanpopy 🐰"]
    )
    
    # Map the clean filter labels back to data values
    if user_filter == "Ado 🐻":
        df_filtered = df[df["User"] == "Ado"]
    elif user_filter == "Paanpopy 🐰":
        df_filtered = df[df["User"] == "Paanpopy"]
    else:
        df_filtered = df

    # 📋 Current Summaries Tabs
    st.subheader(f"📊 Current Summaries")
    tab1, tab2, tab3, tab4 = st.tabs(["🗓️ Week", "📊 Month", "📈 Quarter", "💰 Year"])
    
    def render_summary_tab(filtered_dataset, period_name):
        if filtered_dataset.empty:
            st.info(f"No expenses recorded for this {period_name}.")
        else:
            with st.container(border=True):
                total = filtered_dataset["Amount"].sum()
                st.metric(label=f"Total Spent ({period_name})", value=f"฿{total:.2f}")
                
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
                st.dataframe(filtered_dataset[["Date", "Category", "Amount", "Description", "User"]], use_container_width=True)

    with tab1:
        render_summary_tab(df_filtered[df_filtered['Date_Parsed'] >= start_of_week], "week")
    with tab2:
        render_summary_tab(df_filtered[(df_filtered['Date_Parsed'].dt.year == current_year) & (df_filtered['Date_Parsed'].dt.month == current_month)], "month")
    with tab3:
        render_summary_tab(df_filtered[(df_filtered['Date_Parsed'].dt.year == current_year) & (((df_filtered['Date_Parsed'].dt.month - 1) // 3 + 1) == current_quarter)], "quarter")
    with tab4:
        render_summary_tab(df_filtered[df_filtered['Date_Parsed'].dt.year == current_year], "year")

    # 📈 Trends & Comparisons (Stacked Bar Chart)
    st.markdown("---")
    st.subheader("🧱 Spending Trends & Comparisons")
    
    if not df_filtered.empty:
        with st.container(border=True):
            time_view = st.radio(
                "Compare spending by:",
                ["Weekly", "Monthly", "Yearly"],
                horizontal=True,
                key="time_view_radio"
            )
            
            df_filtered['Year'] = df_filtered['Date_Parsed'].dt.strftime('%Y')
            df_filtered['Month'] = df_filtered['Date_Parsed'].dt.strftime('%Y-%m')
            df_filtered['Week'] = df_filtered['Date_Parsed'].dt.to_period('W').dt.start_time.dt.strftime('%Y-%m-%d')

            if time_view == "Weekly":
                group_col = 'Week'
                lbl = "Starting Week"
            elif time_view == "Monthly":
                group_col = 'Month'
                lbl = "Month"
            else:
                group_col = 'Year'
                lbl = "Year"
                
            df_trend = df_filtered.groupby([group_col, 'Category'], as_index=False)['Amount'].sum()
            
            fig_bar = px.bar(
                df_trend,
                x=group_col,
                y="Amount",
                color="Category",
                color_discrete_sequence=chart_colors,
                labels={group_col: lbl, "Amount": "Total (฿)"}
            )
            fig_bar.update_layout(
                margin=dict(l=10, r=10, t=20, b=10),
                height=300,
                barmode='stack',
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_bar, use_container_width=True, key=f"trend_bar_{user_filter}")
    else:
        st.info("No trend data available for this view.")

else:
    st.info("No expenses added yet. Start tracking your adventures together above!")
