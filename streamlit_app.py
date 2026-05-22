import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 📱 Page configuration for a clean mobile look
st.set_page_config(
    page_title="Finance Tracker",
    page_icon="💰",
    layout="centered"
)

# Custom CSS to inject a modern app feel with rounded corners
st.markdown("""
    <style>
    .stButton>button {
        border-radius: 12px;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    </style>
""", unsafe_html=True)

st.title("💰 Personal Finance Tracker")

# 🗄️ Initialize data storage (Session State)
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])

categories = ["Food", "Gasoline", "Shopping", "Hospital", "Grocery", "For Child"]

# 🛠️ Sidebar Control Panel
st.sidebar.header("⚙️ App Controls")

# 🎨 Theme Selection
theme_choice = st.sidebar.selectbox(
    "🎨 Choose Dashboard Theme",
    ["Midnight Sleek", "Emerald Wealth"]
)

# Define color palettes based on selection
if theme_choice == "Midnight Sleek":
    chart_colors = ["#00F0FF", "#FF007A", "#9D00FF", "#FFB800", "#00FF66", "#FF4D00"]
    metric_color = "🎒"
else:
    chart_colors = ["#064E3B", "#059669", "#34D399", "#A7F3D0", "#F59E0B", "#D97706"]
    metric_color = "💸"

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
        default_date = datetime.strptime(old_row['Date'], "%Y-%m-%d")
        if old_row['Category'] in categories:
            default_cat_index = categories.index(old_row['Category'])
        default_amount = float(old_row['Amount'])
        default_desc = old_row['Description']
        st.sidebar.info(f"Loaded Row {row_to_edit}. Modify details in the main form.")

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
        category = st.selectbox("Category", categories, index=default_cat_index)
        amount = st.number_input("Amount (฿)", min_value=0.0, step=1.0, value=default_amount)
        description = st.text_input("Description (e.g., Weekly run)", value=default_desc)
        
        submit_button = st.form_submit_button(label=form_label)

if submit_button:
    if amount > 0:
        if edit_mode and row_to_edit is not None:
            st.session_state.expenses.at[row_to_edit, "Date"] = date.strftime("%Y-%m-%d")
            st.session_state.expenses.at[row_to_edit, "Category"] = category
            st.session_state.expenses.at[row_to_edit, "Amount"] = amount
            st.session_state.expenses.at[row_to_edit, "Description"] = description
            st.success(f"Updated Row {row_to_edit} successfully!")
            st.rerun()
        else:
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

# 📊 Visual Dashboard Section with Mobile-Friendly Tabs
st.markdown("---")
st.subheader("📊 Financial Summaries")

if not st.session_state.expenses.empty:
    df = st.session_state.expenses.copy()
    df['Date_Parsed'] = pd.to_datetime(df['Date'])
    
    today = datetime.now()
    current_year = today.year
    current_month = today.month
    current_quarter = (today.month - 1) // 3 + 1
    start_of_week = today - timedelta(days=7)

    tab1, tab2, tab3, tab4 = st.tabs(["🗓️ Week", "📊 Month", "📈 Quarter", "💰 Year"])
    
    def render_summary_tab(filtered_df, period_name):
        if filtered_df.empty:
            st.info(f"No expenses recorded for {period_name}.")
        else:
            # Display inside a modern bordered container card
            with st.container(border=True):
                total = filtered_df["Amount"].sum()
                st.metric(label=f"Total Spent ({period_name})", value=f"฿{total:.2f}")
                
                # Modern Donut Chart with custom color sequence
                df_chart = filtered_df.groupby("Category", as_index=False)["Amount"].sum()
                fig = px.pie(
                    df_chart, 
                    values="Amount", 
                    names="Category", 
                    hole=0.4,  # Turns the pie chart into a modern donut chart
                    color_discrete_sequence=chart_colors
                )
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10), 
                    height=260,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(filtered_df[["Date", "Category", "Amount", "Description"]], use_container_width=True)

    with tab1:
        df_week = df[df['Date_Parsed'] >= start_of_week]
        render_summary_tab(df_week, "Last 7 Days")

    with tab2:
        df_month = df[(df['Date_Parsed'].dt.year == current_year) & (df['Date_Parsed'].dt.month == current_month)]
        render_summary_tab(df_month, "This Month")

    with tab3:
        df_quarter = df[(df['Date_Parsed'].dt.year == current_year) & (((df['Date_Parsed'].dt.month - 1) // 3 + 1) == current_quarter)]
        render_summary_tab(df_quarter, "This Quarter")

    with tab4:
        df_year = df[df['Date_Parsed'].dt.year == current_year]
        render_summary_tab(df_year, "This Year")

else:
    st.info("No expenses added yet. Use the form above to start tracking!")
