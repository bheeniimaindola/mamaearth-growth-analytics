# Mamaearth Returns & Growth Intelligence Pipeline

This repository contains an end-to-end data analytics and engineering project analyzing customer orders, returns, revenue trends, and operational segments for Mamaearth Growth Analytics.

---

## 1. SQL Relational Store & Reports (`sql/`)

To set up the relational database and verify all 9 core SQL reports:

1. **Initialize Database Schema & Load Seed Data:**
   Run the database loader script to create tables (`customers`, `products`, `orders`), clean raw data, and insert seed records into `sql/mamaearth.db`:
   ```bash
   python sql/load_db.py