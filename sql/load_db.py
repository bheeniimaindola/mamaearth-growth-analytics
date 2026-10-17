import pandas as pd

import sqlite3

conn = sqlite3.connect('sql/mamaearth.db')
cur = conn.cursor()

with open('sql/schema.sql') as f:
    cur.executescript(f.read())

customers_df = pd.read_csv('data/customers.csv')
orders_df = pd.read_csv('data/orders.csv')
products_df = pd.read_csv('data/products.csv')

# Clean up the dataframes to replace NaN values with None
orders_df['discount_pct'] = orders_df['discount_pct'].where(orders_df['discount_pct'].notnull(), None)
orders_df['rating'] = orders_df['rating'].where(orders_df['rating'].notnull(), None)

#write to sql
customers_df.to_sql('customers', conn, if_exists='replace', index=False)
orders_df.to_sql('orders', conn, if_exists='replace', index=False)
products_df.to_sql('products', conn, if_exists='replace', index=False)

conn.commit()

#verify the counts
print("customers count:", pd.read_sql("SELECT COUNT(*) FROM customers", conn).iloc[0, 0])
print("orders count:", pd.read_sql("SELECT COUNT(*) FROM orders", conn).iloc[0, 0])
print("products count:", pd.read_sql("SELECT COUNT(*) FROM products", conn).iloc[0, 0])




