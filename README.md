# Mamaearth Growth Analytics

This repository contains an end-to-end data analytics and engineering project for Mamaearth Growth Analytics.

---

## 1. SQL Relational Store & Reports
To load the database and run reports:
1. Load `sql/schema.sql` and `sql/seed_data.sql` into your SQLite database (e.g., via `sql/load_db.py`).
2. Run the core report queries located in `sql/reports.sql`.

---

## 2. Data Cleaning, EDA & Visualizations
1. Run the data cleaning and exploratory data analysis script:
   ```bash
   python analysis/clean_and_eda.py