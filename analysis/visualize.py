import os
import matplotlib.pyplot as plt
import pandas as pd

# Load data and replicate cleaning steps to ensure exact reproducibility
orders = pd.read_csv('data/orders.csv')
products = pd.read_csv('data/products.csv')
customers = pd.read_csv('data/customers.csv')

# Standardize payment method
orders['payment_method'] = orders['payment_method'].str.strip().str.upper()

# Drop duplicates
natural_key = [
    'customer_id',
    'product_id',
    'order_date',
    'quantity',
    'discount_pct',
    'payment_method',
    'rating',
    'returned',
]
orders_clean = orders.drop_duplicates(
    subset=natural_key, keep='first'
).copy()

# Impute
orders_clean['discount_pct'] = orders_clean['discount_pct'].fillna(0)
orders_clean['rating'] = orders_clean['rating'].fillna(
    orders_clean['rating'].median()
)

# Merge
merged_df = orders_clean.merge(products, on='product_id', how='left').merge(
    customers, on='customer_id', how='left'
)
merged_df['order_value'] = (
    merged_df['quantity']
    * merged_df['price']
    * (1 - merged_df['discount_pct'] / 100.0)
)

# IQR Outlier filter
Q1 = merged_df['quantity'].quantile(0.25)
Q3 = merged_df['quantity'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
merged_df['is_outlier'] = (merged_df['quantity'] < lower_bound) | (
    merged_df['quantity'] > upper_bound
)

os.makedirs('visualizations', exist_ok=True)

# --- Chart 1: return_rate_by_payment.png ---
plt.figure(figsize=(8, 5))
payment_return = (
    merged_df.groupby('payment_method')['returned'].mean() * 100
).sort_values(ascending=False)
bars = plt.bar(
    payment_return.index,
    payment_return.values,
    color=['#e74c3c', '#3498db', '#2ecc71'],
)

plt.title(
    'COD Returns at 44.4% — 3x Card', fontsize=14, fontweight='bold', pad=15
)
plt.xlabel('Payment Method', fontsize=12)
plt.ylabel('Return Rate (%)', fontsize=12)
plt.ylim(0, 55)

for bar in bars:
  yval = bar.get_height()
  plt.text(
      bar.get_x() + bar.get_width() / 2.0,
      yval + 1.5,
      f'{yval:.1f}%',
      ha='center',
      va='bottom',
      fontsize=11,
      fontweight='bold',
  )

plt.tight_layout()
plt.savefig('visualizations/return_rate_by_payment.png', dpi=300)
plt.close()

# --- Chart 2: monthly_revenue_trend.png ---
merged_df['order_date'] = pd.to_datetime(merged_df['order_date'])
merged_df['year_month'] = merged_df['order_date'].dt.to_period('M')
monthly_corrected = (
    merged_df[~merged_df['is_outlier']]
    .groupby('year_month')['order_value']
    .sum()
)

plt.figure(figsize=(9, 5))
months_str = [str(m) for m in monthly_corrected.index]
plt.plot(
    months_str,
    monthly_corrected.values,
    marker='o',
    color='#2c3e50',
    linewidth=2.5,
    markersize=8,
)

plt.title(
    'Outlier-Corrected Monthly Revenue Trend (Peak: March 2026)',
    fontsize=14,
    fontweight='bold',
    pad=15,
)
plt.xlabel('Year-Month', fontsize=12)
plt.ylabel('Revenue (INR)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

for x, y in zip(months_str, monthly_corrected.values):
  plt.text(
      x,
      y + 800,
      f'₹{y:,.1f}',
      ha='center',
      va='bottom',
      fontsize=10,
      fontweight='bold',
  )

plt.tight_layout()
plt.savefig('visualizations/monthly_revenue_trend.png', dpi=300)
plt.close()

print(
    'Successfully generated both charts in visualizations/ folder!'
)