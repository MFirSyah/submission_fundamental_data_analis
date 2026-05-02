import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set config dashboard
st.set_page_config(page_title="Olist E-Commerce Dashboard", page_icon="🛒", layout="wide")

# Mengatur tema visual seaborn
sns.set_theme(style="whitegrid")

# --- HELPER FUNCTION UNTUK LOAD DATA DARI DRIVE ---
@st.cache_data
def load_data():
    # Mengambil ID file dari Streamlit Secrets
    file_id = st.secrets["google_drive"]["file_id"]
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    
    df = pd.read_csv(url)
    
    # Konversi kolom waktu ke datetime
    datetime_cols = ["order_purchase_timestamp", "order_approved_at", "order_delivered_customer_date"]
    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col])
    return df

try:
    all_df = load_data()
except Exception as e:
    st.error(f"Gagal memuat data dari Google Drive. Pastikan akses file diatur ke 'Anyone with the link'. Error: {e}")
    st.stop()

# ==============================================================================
# SIDEBAR (Fitur Interaktif)
# ==============================================================================
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.title("⚙️ Filter Data")
    
    # 1. Filter Rentang Waktu
    min_date = all_df["order_purchase_timestamp"].min().date()
    max_date = all_df["order_purchase_timestamp"].max().date()
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu Transaksi',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    # 2. Filter Status Pesanan
    order_status_options = all_df['order_status'].unique().tolist()
    selected_status = st.multiselect("Pilih Status Pesanan:", order_status_options, default=["delivered"])

# Filter data berdasarkan input pengguna
main_df = all_df[(all_df["order_purchase_timestamp"].dt.date >= start_date) & 
                 (all_df["order_purchase_timestamp"].dt.date <= end_date) &
                 (all_df["order_status"].isin(selected_status))]

# ==============================================================================
# HEADER & KPI
# ==============================================================================
st.title("🛒 Olist E-Commerce Analytics Dashboard")
st.markdown("**Nama:** Muhammad Firman Ardiansyah | **ID Dicoding:** cdcc012d6y1245")
st.markdown("*Dashboard ini menyajikan hasil analisis data e-commerce di Brazil tahun 2018, berfokus pada efisiensi logistik, sistem pembayaran, dan segmentasi pelanggan.*")

st.write("") 
st.subheader("📌 Key Performance Indicators (Pelanggan)")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Rata-rata Recency", f"{round(main_df['Recency'].mean(), 1)} Hari")
kpi2.metric("Rata-rata Frequency", f"{round(main_df['Frequency'].mean(), 2)} Pesanan")
kpi3.metric("Rata-rata Monetary", f"R$ {main_df['Monetary'].mean():,.2f}")
st.divider()

# ==============================================================================
# 1. PERTANYAAN BISNIS 1: LOGISTIK
# ==============================================================================
st.subheader("🚚 1. Dampak Ongkos Kirim Terhadap Kepuasan (Northeast & North Region)")

ne_north_states = ['MA', 'PI', 'CE', 'RN', 'PB', 'PE', 'AL', 'SE', 'BA', 'AM', 'RR', 'AP', 'PA', 'TO', 'RO', 'AC']
shipping_df = main_df[main_df['customer_state'].isin(ne_north_states)].copy()

shipping_df['shipping_price_ratio'] = (shipping_df['freight_value'] / shipping_df['price']) * 100
region_analysis = shipping_df.groupby("customer_state").agg({
    "shipping_price_ratio": "mean",
    "review_score": "mean"
}).sort_values(by="shipping_price_ratio", ascending=False).reset_index()

col_chart1, col_text1 = st.columns([2, 1])
with col_chart1:
    fig, ax1 = plt.subplots(figsize=(10, 5))
    sns.barplot(x='customer_state', y='shipping_price_ratio', data=region_analysis, color='salmon', ax=ax1)
    ax1.set_ylabel('Shipping-to-Price Ratio (%)', color='red')
    
    ax2 = ax1.twinx()
    sns.lineplot(x='customer_state', y='review_score', data=region_analysis, marker='o', color='blue', ax=ax2)
    ax2.set_ylabel('Rata-rata Review Score (1-5)', color='blue')
    ax2.set_ylim(0, 5)
    st.pyplot(fig)

with col_text1:
    st.info("""
    **🔍 Insight Logistik:**
    - **Rondonia (RO)** memiliki rasio ongkir tertinggi (**59.57%**).
    - Terdapat tren korelasi negatif antara rasio ongkir tinggi dengan skor ulasan yang lebih rendah di wilayah utara.
    """)
st.divider()

# ==============================================================================
# 2. PERTANYAAN BISNIS 2: PEMBAYARAN
# ==============================================================================
st.subheader("💳 2. Durasi Validasi Pembayaran (Mei - Juni 2018)")

sale_df = all_df[(all_df['order_purchase_timestamp'] >= '2018-05-01') & 
                 (all_df['order_purchase_timestamp'] <= '2018-06-30')]

target_payments = ['boleto', 'credit_card']
val_stats = sale_df[sale_df['payment_type'].isin(target_payments)].groupby("payment_type").agg({
    "validation_duration_hours": "mean"
}).reset_index()

col_text2, col_chart2 = st.columns([1, 2])
with col_text2:
    st.warning("""
    **⚠️ Insight Sistem Pembayaran:**
    - Validasi **Boleto (32.01 jam)** jauh melampaui **Credit Card (3.45 jam)**.
    - Hal ini berisiko menyebabkan *inventory lock* selama periode Flash Sale.
    """)

with col_chart2:
    fig2, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x='payment_type', y='validation_duration_hours', data=val_stats, palette='magma', ax=ax)
    ax.axhline(y=24, color='red', linestyle='--', label='Batas Aman (24 Jam)')
    st.pyplot(fig2)
st.divider()

# ==============================================================================
# 3. ANALISIS LANJUTAN (RFM & GEOSPATIAL)
# ==============================================================================
st.subheader("🎯 3. Segmentasi Pelanggan Berdasarkan RFM Score")
fig3, ax = plt.subplots(figsize=(12, 4))
rfm_counts = main_df['RFM_Score'].value_counts().head(10)
sns.barplot(x=rfm_counts.index, y=rfm_counts.values, palette='Blues_d', ax=ax)
st.pyplot(fig3)
st.success("**Insight RFM:** Pelanggan didominasi pembeli tunggal. Dibutuhkan strategi retensi yang lebih agresif.")

st.subheader("🗺️ 4. Peta Persebaran Lokasi Pelanggan")
map_data = main_df[['geolocation_lat', 'geolocation_lng']].dropna()
map_data.rename(columns={'geolocation_lat': 'lat', 'geolocation_lng': 'lon'}, inplace=True)
if not map_data.empty:
    st.map(map_data, zoom=3)
st.info("**Insight Geospasial:** Konsentrasi pasar terpusat di wilayah Tenggara (Sao Paulo & RJ), sedangkan wilayah Utara masih sangat minim pelanggan.")

# ==============================================================================
# KESIMPULAN
# ==============================================================================
st.subheader("📝 Kesimpulan & Rekomendasi")
st.markdown("""
- **Logistik:** Beban ongkir di wilayah Utara mencapai 59% (RO), menurunkan kepuasan pelanggan.
- **Pembayaran:** Efisiensi validasi pembayaran instan lebih baik untuk menjaga perputaran stok saat promo.
- **Aksi:** Bangun gudang distribusi regional di wilayah Utara untuk menekan rasio biaya kirim.
""")

st.caption("Copyright © Muhammad Firman Ardiansyah 2026")
