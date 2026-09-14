Customer Churn Analysis

A Python project that analyzes customer churn using data pulled from a SQLite database. It covers data cleaning, feature engineering, KPI calculation, and visualization to understand why customers cancel and where revenue is at risk.

Overview

The project connects to a customer_churn.db SQLite database containing three tables — customer, subscription, and support data — cleans and merges them into a single dataframe, then computes churn-related metrics and produces charts to visualize trends.

Data Source
Database: customer_churn.db (SQLite)
Tables:
db_customer — customer demographics (name, dob, gender, country, state, etc.)
db_subscription — subscription details (plan type, subscription type, start/renewal/cancellation dates, monthly charges)
db_support — customer support interactions (complaints, escalations)

Tables are loaded dynamically into pandas dataframes named df_<table_name>.

Requirements
numpy
pandas
matplotlib
seaborn
sqlite3 (standard library)

Install dependencies with:

bash
pip install numpy pandas matplotlib seaborn
Project Structure / Workflow
1. Data Loading

Connects to the SQLite database, discovers all tables, and loads each into its own dataframe.

2. Data Cleaning
Customer table: renames columns, drops unused columns (interests, pincode), converts dob to datetime, standardizes gender labels, and fills missing country values based on state.
Subscription table: converts date columns (subscription_start_date, renewal_date, cancellation_date) to datetime.
Support table: converts complaint_date to datetime, drops unused columns, and deduplicates by customer while keeping a complaint_count.
3. Feature Engineering & Merging
Creates a churn_flag (1 if a customer has a cancellation date, else 0).
Merges the subscription, customer, and support tables into a single dataframe df.
Exports the merged dataset to exported_churn_data.csv.
Adds derived features: tenure_days, encoded escalations, and a categorical churn_risk (low/med/high) based on churn_score.
4. Data Analysis (KPIs)

Computes key metrics, including:

Overall churn and retention rate
Churn rate by plan type, subscription type, and state
Revenue by state and subscription type
Number of users by state and subscription type
Average Revenue Per User (ARPU)
Average customer tenure
Revenue at risk from churned users
Escalation rate and average complaints per user
Correlation between escalations and churn
5. Data Visualization

Generates charts using Matplotlib:

Monthly churn trend (line chart)
Churn rate by plan type (bar chart)
Churn rate by state (bar chart)
Output
exported_churn_data.csv — the cleaned, merged dataset used for analysis
Inline chart visualizations (churn trend, churn by plan, churn by state)
Usage
Place customer_churn.db in the project directory.
Run the script:
bash
   python churn_analysis.py
Review the printed KPIs (uncomment print statements as needed) and generated charts.
Notes
Several print() statements are commented out throughout the script — uncomment them to inspect intermediate results while debugging.
churn_score must already exist in the merged dataset for the churn_risk categorization step to work.
