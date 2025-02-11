import streamlit as st
import pandas as pd
import mysql.connector

# Load database credentials from Streamlit secrets
DB_CONFIG = {
    "host": st.secrets["db_host"],
    "user": st.secrets["db_user"],
    "password": st.secrets["db_password"],
    "database": st.secrets["db_database"]
}

# Function to connect to MySQL and fetch data
def get_data(query):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)  # Fetch results as dictionaries
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data)

# Load data from MySQL instead of Google Drive
orders_query = "SELECT OrderDate AS Data, TotalAmount AS Valor_Total FROM Orders"
inventory_query = "SELECT item_name AS Nome, StockQuantity AS Unidades, Amount/12 AS Dúzias, UnitPrice AS Preço FROM Inventory"

orders_df = get_data(orders_query)
inventory_df = get_data(inventory_query)

if not orders_df.empty and not inventory_df.empty:
    # Streamlit Dashboard
    st.title("📊 Monica's Business Dashboard")

    # Revenue Stats
    st.subheader("💰 Sumário de Receita")
    orders_df["Data"] = pd.to_datetime(orders_df["Data"])

    # Create full date range and fill missing revenue days with 0
    full_date_range = pd.date_range(start=orders_df["Data"].min(), end=orders_df["Data"].max())
    daily_revenue = orders_df.groupby("Data")["Valor_Total"].sum().reindex(full_date_range, fill_value=0)

    st.line_chart(daily_revenue)

    # Inventory Stats
    st.subheader("📦 Inventário Atual")
    inventory_cols = ["Nome", "Unidades", "Dúzias", "Preço"]
    st.write(inventory_df[inventory_cols])

else:
    st.warning("Could not load data. Check MySQL connection or database tables.")
