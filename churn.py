# importing libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

conn = sqlite3.connect('customer_churn.db')

sql_query = """
    SELECT name 
    FROM sqlite_master
    WHERE type='table'
"""

tables = pd.read_sql(sql_query, conn)

# Creating dataframes
for table_name in tables['name']:
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    globals()[f"df_{table_name}"] = df
    print(f" Created Dataframes: df_{table_name}")

# for table_name in tables['name']:
#     print(f"\n Table Name: {table_name}")
#     # Get column information
#     columns_query = f"PRAGMA table_info({table_name})"
#     columns = pd.read_sql(columns_query, conn)
#     print(columns)
#     print(columns['name'].tolist())

# Close connection
conn.close()

# Data Cleaning
# print(df_db_customer.head())
# print(df_db_customer.tail())
# print(df_db_customer.info())

# a. Rename column 'name' to 'customer_name'
df_db_customer.rename(columns = {"name" : "customer_name"}, inplace= True)
# print(df_db_customer)

# b. drop columns interest & pincode
df_db_customer.drop(columns = ['interests', 'pincode'], inplace= True)
# print(df_db_customer)


# c. Convert date type - dob
df_db_customer['dob'] = pd.to_datetime(df_db_customer['dob'])
# print(df_db_customer)

# d. Standardization of gender column
# print(df_db_customer['gender'].unique())
df_db_customer['gender'] = df_db_customer['gender'].replace({'Men' : 'Male', 'Women' : 'Female'})
# print(df_db_customer['gender'])

# e. Replace null values in country
mapping = df_db_customer.dropna(subset= ['country']).set_index('state')['country'].to_dict()
df_db_customer['country'] = df_db_customer['country'].fillna(df_db_customer['state'].map(mapping))


# LETS MOVE THE ANOTHER TABLE
# print(df_db_subscription.head())
# print(df_db_subscription.tail())
# print(df_db_subscription.info())


# Convert the string datatype to date datatype
# df_db_subscription['subscription_start_date'] = pd.to_datetime(df_db_subscription['subscription_start_date'])
# df_db_subscription['renewal_date'] = pd.to_datetime(df_db_subscription['renewal_date'])
# df_db_subscription['cancellation_date'] = pd.to_datetime(df_db_subscription['cancellation_date'])

date_column = ['subscription_start_date', 'renewal_date', 'cancellation_date']
df_db_subscription[date_column] = df_db_subscription[date_column].apply(pd.to_datetime)
# print(df_db_subscription.info())


# LET'S MOVE TO THE LAST TABLE
# print(df_db_support.head())
# print(df_db_support.tail())
# print(df_db_support.info())

#a. Convert str datatype to date datatype
df_db_support['complaint_date'] = pd.to_datetime(df_db_support['complaint_date'])


#b. remove column 'col_1'
df_db_support.drop(columns = ['col_1', 'comment'], inplace= True)
# print(df_db_support.info())

# c. Removing duplicate customerid after counting the number of complaint and putting into another column
df_db_support['complaint_count'] = df_db_support.groupby('customerid')['customerid'].transform('count')
df_db_support = df_db_support.sort_values('complaint_date').drop_duplicates('customerid', keep= 'last')
# print(df_db_support)

# FEATURE ENGINEERING AND DATA ANALYTICS

df_db_subscription['churn_flag'] = np.where(df_db_subscription['cancellation_date'].notna(), 1, 0)
# print(df_db_subscription['churn_flag'])

# merging all the tables to df_db_subscription
df= (df_db_subscription
            .merge(df_db_customer, on = 'customerid', how= 'left')
            .merge(df_db_support, on = 'customerid', how= 'left'))
print(df.shape)
# print(df_db_subscription.shape)

# DATA ANALYSIS
df.to_csv('exported_churn_data.csv', index= False)

# 1. Churn Rate
# print(df.columns)
churn_rate = df['churn_flag'].mean()*100
# print(f'Churn Rate = {round(churn_rate, 2)} %' )

# 2. Retention Rate
retention_rate = 100 - churn_rate
# print(f"Retention Rate = {round(retention_rate, 2) } %")

# 3. Churn Rate by plan type
churn_by_plan = df.groupby('plan_type')['churn_flag'].mean().mul(100).round(2).reset_index(name= 'ChurnByPlan_pct')
# print(churn_by_plan)

# 4. Churn Rate by State
churn_by_state = df.groupby('state')['churn_flag'].mean().mul(100).round(2).reset_index(name= 'ChurnByState_pct')
# print(churn_by_state)

# 5. Revenue generate per state
state_revenue = df.groupby('state')['monthly_charges'].sum().reset_index(name= 'State_revenue')
# print(state_revenue)

# 6. Number of users from each state
users = df.groupby('state')['customerid'].count().reset_index(name= 'Total_users')
# print(users)

# 7. Churn by subscription type
churn_by_subscription = df.groupby('subscription_type')['churn_flag'].mean().mul(100).round(2).reset_index(name= 'ChurnBySubscription_pct')
# print(churn_by_subscription)

# 8. Revenue generate by subscription types
subscription_revenue = df.groupby('subscription_type')['monthly_charges'].sum().reset_index(name= 'Subscription_revenue')
# print(subscription_revenue)

# 9. Number of user in each subscription type
sub_users = df.groupby('subscription_type')['customerid'].count().reset_index(name= 'subcription_users')
# print(sub_users)

# 10. Average Revenue per user
ARPU = df['monthly_charges'].mean().round(2)
# print(f'ARPU= {ARPU}')

# 11. Average customer Tenure
# if not cancel then calculate it by today else by cancelation data
today = pd.Timestamp.today()

df['tenure_days'] = np.where(df['cancellation_date'].notna(), 
            (df['cancellation_date'] - df['subscription_start_date']).dt.days,
            (today - df['subscription_start_date']).dt.days)
# print(df['tenure_days'])
avg_tenure = df['tenure_days'].mean()
# print(f"Average Tenure: {round(avg_tenure, 0)})

# 12. Revenue loss from churned users
revene_at_risk = df.loc[df['churn_flag']== 1, 'monthly_charges'].sum()
# print(f"Revenue at risk: {revene_at_risk}K")

# 13. Escalation Rate
escalation_rate = (df['escalations']=='Y').mean()*100
# print(f"Escalation Rate: {round(escalation_rate, 2)} %")

# 14. Average complaint per user
avg_complaint = df['complaint_count'].sum() / df['customerid'].nunique()
# print(f"Average complaint per user: {avg_complaint}")

# 15. Correlation Escalation vs Churn
df['escalations'] = np.where(df['escalations']=='Y', 1, 0) #Encoding
corr_df = df[['escalations', 'churn_flag']].dropna()
# print(corr_df)
correlation = corr_df['escalations'].corr(corr_df['churn_flag'])
# print(f"The correlation between escalation and churn_flag: {round(correlation, 2)*100}%")

# 16. Create a new column 'churn_risk' using exsiting column 'churn_score'
conditions = [(df['churn_score'] < 50),
              (df['churn_score'] >= 50) & (df['churn_score'] < 70),
              (df['churn_score'] >= 70)
]
choice = ['low', 'med', 'high']
df['churn_risk'] = np.select(conditions, choice, default='unknown')
# print(df[['churn_risk', 'churn_score']])

# DATA VISUALIZATION

df_visual = df.copy() 

# 1. Monthly churn trend (Time Series KPI)
df_visual['cancellation_month'] = (df_visual['cancellation_date'].dt.to_period('M')) 
churn_trend = df_visual[df_visual['churn_flag']==1].groupby('cancellation_month').size()
# print(churn_trend)
plt.figure(figsize=(8,3))
plt.plot(churn_trend.index.astype(str), churn_trend.values, color='violet', marker='o', linestyle='dotted', linewidth=2, markersize=12)
plt.title("Monthly churn trend")
plt.xlabel("Month")
plt.ylabel("Churn Customer")
# plt.show()


# 2. Churn by plan type
churn_plan = df_visual.groupby('plan_type')['churn_flag'].mean()
# print(churn_plan)
# colors = ['red', 'blue', 'yellow']
colors = plt.cm.Set2(np.linspace(0, 1, len(churn_plan)))
plt.figure(figsize=(10,5))
plt.bar(churn_plan.index, churn_plan.values, color= colors)
plt.title('Churn by Plan Type')
plt.xlabel('Plans')
plt.ylabel('Average Churn rate')
# plt.show()


# 3. Churn by States
churn_state = df_visual.groupby('state')['churn_flag'].mean()
# print(churn_state)
colors1 = plt.cm.Set2(np.linspace(0, 1, len(churn_state)))
plt.figure(figsize=(12, 5))
plt.bar(churn_state.index, churn_state.values, color=colors1)
plt.title("Churn by State")
plt.xlabel("States")
plt.ylabel("Average churn rate")
plt.show()

# VISUALIZATION BY SEABORN



