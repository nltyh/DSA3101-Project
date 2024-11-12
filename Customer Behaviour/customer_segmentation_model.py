import gdown

file_id = '1l7Tsvp_1w0ZO3j6ktxlN-i_ZrR_MfcNW'
url = f'https://drive.google.com/uc?id={file_id}'
output1 = 'Customers.csv'
gdown.download(url, output1, quiet=False)

file_id = '1hX2-KzS0nwyEuhi9dWy22PzRUczXVpn7'
url = f'https://drive.google.com/uc?id={file_id}'
output2 = 'Orders Table.csv'
gdown.download(url, output2, quiet=False)

file_id = '1ATwj5A6yDHafhI7Az1DKgwX1UsDkuuAn'
url = f'https://drive.google.com/uc?id={file_id}'
output3 = 'Products Table.csv'
gdown.download(url, output3, quiet=False)

import pandas as pd
import numpy as np

customers_df = pd.read_csv('Customers.csv')
customers_df.drop(columns=['Unnamed: 0'], inplace=True)

orders_df = pd.read_csv("Orders Table.csv")
orders_df.drop(columns=['Unnamed: 0'], inplace=True)
orders_df['Order Date'] = pd.to_datetime(orders_df['Order Date'], errors='coerce')

products_df = pd.read_csv("Products Table.csv")

# Create a copy of customers_df
customers_copy = customers_df.copy()

# Calculate the required new columns for each customer in customers_copy based on orders_df

# 1. ordered: 0 means customer has not made any orders before, 1 means yes but only on 1 day, 2 means yes and on >1 day
orders_per_day = orders_df.groupby('CustomerID')['Order Date'].nunique()
customers_copy['ordered'] = customers_copy['CustomerID'].map(lambda x: 2 if orders_per_day.get(x, 0) > 1 else (1 if orders_per_day.get(x, 0) == 1 else 0))

# 2. total_order: Total number of orders customer has ever made
total_orders = orders_df.groupby('CustomerID').size()
customers_copy['total_order'] = customers_copy['CustomerID'].map(total_orders).fillna(0).astype(int)

# 3. ave_monthly_orders: Average number of orders per month between the earliest and latest order of that customer
earliest_order = orders_df.groupby('CustomerID')['Order Date'].min()
latest_order = orders_df.groupby('CustomerID')['Order Date'].max()
tenure_months = (latest_order - earliest_order).dt.days / 30.44
ave_monthly_orders = total_orders / tenure_months
ave_monthly_orders[tenure_months < 1] = 0  # Setting 0 for customers with orders on <=1 day
customers_copy['ave_monthly_orders'] = customers_copy['CustomerID'].map(ave_monthly_orders).fillna(0)

# 4. days_last_order: The number of days between the latest date the customer made an order and the last date of the dataset
last_order_date = orders_df['Order Date'].max()
days_last_order = (last_order_date - latest_order).dt.days
customers_copy['days_last_order'] = customers_copy['CustomerID'].map(days_last_order)

# 5. only_promo_order: 1 means the customer has only placed order/s during the promotional period, 0 if otherwise
only_promo = orders_df.groupby('CustomerID')['Promotional Period'].all().astype(int)
customers_copy['only_promo_order'] = customers_copy['CustomerID'].map(only_promo).fillna(0).astype(int)

# Merging orders_df with products_df to get product prices and categories for each order
orders_with_products = orders_df.merge(products_df[['ProductID', 'Category', 'Price']], on='ProductID', how='left')

# Calculating the required new columns for each customer in customers_copy based on the merged orders_with_products

# 6. total spend: Total spending a customer has ever made
total_spend = orders_with_products.groupby('CustomerID')['Price'].sum()
customers_copy['total_spend'] = customers_copy['CustomerID'].map(total_spend).fillna(0)

# 7. ave_monthly_spending: Average spending per month between the earliest and latest order
# For customers who have ordered on >1 days
ave_monthly_spending = total_spend / tenure_months
ave_monthly_spending[tenure_months < 1] = 0  # Setting to 0 for customers with orders on <=1 day
customers_copy['ave_monthly_spending'] = customers_copy['CustomerID'].map(ave_monthly_spending).fillna(0)

# 8. most_ordered_cat: The category of products that the customer ordered the most
most_ordered_cat = orders_with_products.groupby('CustomerID')['Category'].agg(lambda x: x.mode()[0] if not x.mode().empty else '')
customers_copy['most_ordered_cat'] = customers_copy['CustomerID'].map(most_ordered_cat)

# 9
most_ordered_counts = orders_with_products.groupby(['CustomerID', 'Category']).size().unstack(fill_value=0)

# Update customers_copy to handle cases with no orders for moc_ratio calculation
def calculate_moc_ratio(row):
    if row['total_order'] > 0 and row['most_ordered_cat']:
        return most_ordered_counts.loc[row['CustomerID'], row['most_ordered_cat']] / row['total_order']
    else:
        return 0

# Apply function to calculate `moc_ratio`
customers_copy['moc_ratio'] = customers_copy.apply(calculate_moc_ratio, axis=1)


df=customers_copy.copy()
df.drop(columns=['Age', 'Gender', 'Churn', 'Complain'], inplace=True)

df['segment_1'] = (df['only_promo_order'] == 1) | (df['CouponUsed'] >= 2) | (df['CashbackAmount'] >= 196.06)
df['segment_2'] = (df['total_spend'] >= 61.78) & (df['ave_monthly_orders'] >= 0.45) & (df['Tenure'] >= 13)
df['segment_3'] = (df['ave_monthly_orders'] <= 0.15) & (df['HourSpendOnApp'] <= 2)
df['segment_4'] = (df['HourSpendOnApp'] >= 4) & (df['NumberOfDeviceRegistered'] >= 4)
df['segment_5'] = df['moc_ratio'] >= 1
df['segment_6'] = (df['ordered'] == 0) & (df['Tenure'] >= 13)

# Display a few rows to verify the results
df[['CustomerID', 'segment_1', 'segment_2', 'segment_3', 'segment_4', 'segment_5', 'segment_6']].head()

# Define total number of customers and segment names
total_customers = 100000
segments = ['Discount_seekers', 'Loyal High-Spenders', 'Occasional Shoppers', 'Tech-Savvy Users', 'Single-Category Shoppers', 'Long-Tenured Non-Buyers']
segment_counts = {}

# Calculate the number of True values and percentages for each segment
for i in range(1, 7):  # Segment columns are named segment_1 to segment_6
    count_true = df[f'segment_{i}'].sum()
    percentage = (count_true / total_customers) * 100
    segment_counts[segments[i-1]] = (count_true, percentage)  # Mapping each segment name correctly

# Create the report based on the calculated counts and percentages
report = [f"{count_true} customers are {segment} ({percentage:.2f}%)"
          for segment, (count_true, percentage) in segment_counts.items()]

print(report)
