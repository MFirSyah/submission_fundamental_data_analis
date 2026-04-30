import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Set Page Config
st.set_page_config(page_title="E-Commerce Public Dashboard", layout="wide")

# Penanganan Path File secara otomatis (Sesuai saran reviewer)
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "main_data.csv")

# Load Data
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    st.error(f"Gagal memuat data. Pastikan '{file_path}' tersedia.")
    st.stop()

# Perbaikan Nama Kolom & Konversi Datetime
if "order_purchase_timestamp_x" in df.columns:
    df.rename(columns={
        "order_purchase_timestamp_x": "order_purchase_timestamp",
        "order_delivered_customer_date_x": "order_delivered_customer_date"
    }, inplace=True)

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
for column in datetime_columns:
    if column in df.columns:
        df[column] = pd.to_datetime(df[column])

# Sidebar - Fitur Interaktif (Filtering berdasarkan Tanggal)
with st.sidebar:
    st.title("Filter Data")
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    min_date = df["order_purchase_timestamp"].min()
    max_date = df["order_purchase_timestamp"].max()
    
    try:
        start_date, end_date = st.date_input(
            label='Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except Exception:
        start_date, end_date = min_date, max_date

# Filtered Data
main_df = df[(df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & 
            (df["order_purchase_timestamp"] <= pd.to_datetime(end_date))]

# Header
st.header('E-Commerce Performance Dashboard 🛍️')

# Pertanyaan 1: Logistics & Review Score
st.subheader("1. Logistics Performance vs Customer Satisfaction")
col1, col2 = st.columns(2)

with col1:
    if "order_delivered_customer_date" in main_df.columns:
        main_df['delivery_duration'] = (main_df['order_delivered_customer_date'] - main_df['order_purchase_timestamp']).dt.days
        avg_delivery = round(main_df['delivery_duration'].mean(), 1)
        st.metric("Rata-rata Durasi Pengiriman", value=f"{avg_delivery} Hari")

with col2:
    if 'review_score' in main_df.columns:
        avg_review = round(main_df['review_score'].mean(), 2)
        st.metric("Rata-rata Skor Review", value=avg_review)

# Visualisasi 1
if not main_df.empty and 'review_score' in main_df.columns:
    fig, ax = plt.subplots(figsize=(10, 5))
    delivery_stats = main_df.groupby('delivery_duration')['review_score'].mean().reset_index()
    sns.regplot(x='delivery_duration', y='review_score', data=delivery_stats, scatter_kws={'alpha':0.5}, line_kws={'color':'red'}, ax=ax)
    ax.set_title("Korelasi Durasi Pengiriman vs Skor Review")
    st.pyplot(fig)

st.markdown("---")

# Pertanyaan 2: Payment Comparison
st.subheader("2. Payment Behavior Analysis")
col3, col4 = st.columns([1, 2])

with col3:
    if 'payment_type' in main_df.columns:
        payment_count = main_df.groupby("payment_type").order_id.nunique().sort_values(ascending=False).reset_index()
        payment_count.columns = ['Metode Pembayaran', 'Jumlah Transaksi']
        st.write(payment_count)

with col4:
    if 'payment_type' in main_df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='payment_type', y='payment_value', data=main_df, palette='viridis', ax=ax, estimator="mean")
        ax.set_title("Rata-rata Nilai Transaksi per Metode Pembayaran")
        st.pyplot(fig)

st.caption('Copyright (C) 2026 - Muhammad Firman Ardiansyah')