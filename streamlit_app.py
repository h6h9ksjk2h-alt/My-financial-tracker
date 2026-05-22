import streamlit as tf
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

# ➕ Section 1: Input Form (Places in sidebar for desktop, top of screen for mobile)
st.header("➕ Add New Expense")
with st.form("expense_form", clear_on_submit=True):
    date = st.date_input("Date", datetime.now())
    category = st.selectbox(
        "Category", 
        ["Food", "Gasoline", "Shopping", "Hospital", "Grocery", "For Child"]
    )
    amount = st.number_input("Amount ($)", min_value=0.0, step=1.0)
    description = st.text_input("Description (e.g., Weekly run)")
    
    submit_button = st.form_submit_button(label="Add Expense")

# 🧠 Logic: Append new entry when button is clicked
if submit_button:
    if amount > 0:
        new_row = pd.DataFrame([{
            "Date": date.strftime("%Y-%m-%d"), 
            "Category": category, 
            "Amount": amount, 
            "Description": description
        }])
        st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
        st.success(f"Added {category}: ${amount:.2f}!")
    else:
        st.warning("Please enter an amount greater than 0.")

# 📊 Section 2: Dashboard Visualization
if not st.session_state.expenses.empty:
    df = st.session_state.expenses
    
    st.markdown("---")
    
    # 🔢 Metric Card
    total_spent = df["Amount"].sum()
    st.metric(label="📊 Total Spent", value=f"${total_spent:.2f}")
    
    # 🎨 Chart: Spending Breakdown
    st.subheader("🍕 Spending Breakdown")
    # Group data by category for the chart
    df_chart = df.groupby("Category", as_index=False)["Amount"].sum()
    fig = px.pie(df_chart, values="Amount", names="Category", hole=0.3)
    # Optimize chart sizing for smaller smartphone screens
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # 📋 Data Table
    st.subheader("📋 Transaction History")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No expenses added yet. Use the form above to start tracking!")
