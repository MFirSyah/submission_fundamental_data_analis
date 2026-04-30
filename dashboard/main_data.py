# Menggabungkan data penting untuk dashboard
main_df = pd.merge(orders_df, order_reviews_df, on="order_id")
main_df = pd.merge(main_df, customers_df, on="customer_id")
main_df = pd.merge(main_df, order_items_df, on="order_id")
main_df = pd.merge(main_df, order_payments_df, on="order_id")

# Simpan ke folder dashboard
main_df.to_csv("dashboard/main_data.csv", index=False)