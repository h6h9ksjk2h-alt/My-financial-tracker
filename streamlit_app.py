import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 📱 Page configuration for a clean mobile look
st.set_page_config(
    page_title="Finance Tracker",
    page_icon="💰",
    layout="centered"
)

st.title("💰 Personal Finance Tracker")

# 🗄️ Initialize data storage (Session State) so data persists while browsing
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])

categories = ["Food", "Gasoline", "Shopping", "Hospital", "Grocery", "For Child"]

# 🛠️ Sidebar Control Panel
st.sidebar.header("⚙️ App Controls")
edit_mode = st.sidebar.checkbox("📝 Enable Edit Mode")

# Initialize default values for the input form
default_date = datetime.now()
default_cat_index = 0
default_amount = 0.0
default_desc = ""
row_to_edit = None

# 🔍 Safety Check & Lookup Logic for Edit Mode
if edit_mode:
    if st.session_state.expenses.empty:
        st.sidebar.warning("⚠️ No expenses recorded yet. Add an expense first!")
        edit_mode = False  # Force edit mode off since there is nothing to edit
    else:
        st.sidebar.subheader("✏️ Select Row to Edit")
        # Let the user pick a row number based on the table's index numbers
        row_to_edit = st.sidebar.number_input(
            "Enter Row Number to Edit", 
            min_value=0, 
            max_value=len(st.session_state.expenses)-1, 
            step=1
        )
        
        # Pull the old values to pre-populate the form
        old_row = st.session_state.expenses.iloc[row_to_edit]
        default_date = datetime.strptime(old_row['Date'], "%Y-%m-%d")
        if old_row['Category'] in categories:
            default_cat_index = categories.index(old_row['Category'])
        default_amount = float(old_row['Amount'])
        default_desc = old_row['Description']
        st.sidebar.info(f"Loaded Row {row_to_edit}. Modify the details in the main form.")

# ➕ Main Form Section (Handles both Adding and Editing)
if edit_mode:
    st.header(f"✏️ Modify Expense (Row {row_to_edit})")
    form_label = "Save Changes"
else:
    st.header("➕ Add New Expense")
    form_label = "Add Expense"

with st.form("expense_form", clear_on_submit=not edit_mode):
    date = st.date_input("Date", default_date)
    category = st.selectbox("Category", categories, index=default_cat_index)
    amount = st.number_input("Amount (฿)", min_value=0.0, step=1.0, value=default_amount)
    description = st.text_input("Description (e.g., Weekly run)", value=default_desc)
    
    submit_button = st.form_submit_button(label=form_label)

# 🧠 Processing Logic for Form Submission
if submit_button:
    if amount > 0:
        if edit_mode and row_to_edit is not None:
            # 🔄 Update the specific existing row
            st.session_state.expenses.at[row_to_edit, "Date"] = date.strftime("%Y-%m-%d")
            st.session_state.expenses.at[row_to_edit, "Category"] = category
            st.session_state.expenses.at[row_to_edit, "Amount"] = amount
            st.session_state.expenses.at[row_to_edit, "Description"] = description
            st.success(f"Updated Row {row_to_edit} successfully!")
            # Turn off edit mode after saving so the user returns to normal mode
            st.rerun()
        else:
            # ➕ Append a completely new row
            new_row = pd.DataFrame([{
                "Date": date.strftime("%Y-%m-%d"), 
                "Category": category, 
                "Amount": amount, 
                "Description": description
            }])
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
            st.success(f"Added {category}: ฿{amount:.2f}!")
    else:
        st.warning("Please enter an amount greater than 0.")

# 📊 Visual Dashboard Section
if not st.session_state.expenses.empty:
    df = st.session_state.expenses
    
    st.markdown("---")
    
    # 🔢 Metric Card (Updated to Thai Baht symbol)
    total_spent = df["Amount"].sum()
    st.metric(label="📊 Total Spent", value=f"฿{total_spent:.2f}")
    
    # 🎨 Chart: Spending Breakdown
    st.subheader("🍕 Spending Breakdown")
    df_chart = df.groupby("Category", as_index=False)["Amount"].sum()
    fig = px.pie(df_chart, values="Amount", names="Category", hole=0.3)
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # 📋 Data Table (Shows the row index numbers clearly)
    st.subheader("📋 Transaction History")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No expenses added yet. Use the form above to start tracking!")
