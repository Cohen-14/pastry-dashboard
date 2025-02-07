import streamlit as st
import pandas as pd
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials

# Google Drive Folder ID where CSVs are stored
FOLDER_ID = "19ORGAVIga8ebjGX73tuXOcqfl6qwucVh"  # Replace with your actual folder ID

# Authenticate Google Drive API
@st.cache_data
def get_drive_service():
    creds = Credentials.from_service_account_file("credentials.json", scopes=["https://www.googleapis.com/auth/drive"])
    return build("drive", "v3", credentials=creds)

# Get file ID from Google Drive by name
def get_file_id(service, file_name):
    query = f"'{FOLDER_ID}' in parents and name='{file_name}' and mimeType='text/csv'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    return files[0]["id"] if files else None

# Download CSV from Google Drive
def download_csv_from_drive(file_name):
    service = get_drive_service()
    file_id = get_file_id(service, file_name)
    if not file_id:
        st.error(f"File {file_name} not found in Drive folder.")
        return None
    
    request = service.files().get_media(fileId=file_id)
    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    
    file_stream.seek(0)
    return pd.read_csv(file_stream)

# Load data dynamically from Google Drive
orders_df = download_csv_from_drive("encomendas.csv")
inventory_df = download_csv_from_drive("inventario.csv")

if orders_df is not None and inventory_df is not None:
    # Streamlit Dashboard
    st.title("📊 Monica's Business Dashboard")

    # Revenue Stats
    st.subheader("💰 Sumário de Receita")
    # Ensure date column is in datetime format
    orders_df["Data"] = pd.to_datetime(orders_df["Data"])
    # Create full date range from the first to the last order date
    full_date_range = pd.date_range(start=orders_df["Data"].min(), end=orders_df["Data"].max())
    # Group by date and sum revenue
    daily_revenue = orders_df.groupby("Data")["Valor_Total"].sum()
    # Reindex with full date range and fill missing values with 0
    daily_revenue = daily_revenue.reindex(full_date_range, fill_value=0)
    st.line_chart(daily_revenue)

    # Inventory Stats
    st.subheader("📦 Inventário Atual")
    # Filter out columns
    inventory_cols = ["Nome", "Unidades", "Dúzias", "Preço"]
    st.write(inventory_df[inventory_cols])

else:
    st.warning("Could not load CSV files. Check Google Drive permissions or filename.")
