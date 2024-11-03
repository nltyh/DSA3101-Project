import pandas as pd
import numpy as np

customers_df = pd.read_csv('Customers.csv')
customers_df.drop(columns=['Unnamed: 0'], inplace=True)

orders_df = pd.read_csv("Orders Table.csv")
orders_df.drop(columns=['Unnamed: 0'], inplace=True)
orders_df['Order Date'] = pd.to_datetime(orders_df['Order Date'], errors='coerce')

products_df = pd.read_csv("Products Table.csv")
products_df.drop(columns=['Unnamed: 0'], inplace=True)

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

# 5. returned: 0 means the customer has never returned any orders before, 1 if otherwise
returns = orders_df.groupby('CustomerID')['Returns'].max()
customers_copy['returned'] = customers_copy['CustomerID'].map(returns).fillna(0).astype(int)

# 6. only_promo_order: 1 means the customer has only placed order/s during the promotional period, 0 if otherwise
only_promo = orders_df.groupby('CustomerID')['Promotional Period'].all().astype(int)
customers_copy['only_promo_order'] = customers_copy['CustomerID'].map(only_promo).fillna(0).astype(int)

# Merging orders_df with products_df to get product prices and categories for each order
orders_with_products = orders_df.merge(products_df[['ProductID', 'Category', 'Price']], on='ProductID', how='left')

# Calculating the required new columns for each customer in customers_copy based on the merged orders_with_products

# 7. total spend: Total spending a customer has ever made
total_spend = orders_with_products.groupby('CustomerID')['Price'].sum()
customers_copy['total_spend'] = customers_copy['CustomerID'].map(total_spend).fillna(0)

# 8. ave_monthly_spending: Average spending per month between the earliest and latest order
# For customers who have ordered on >1 days
ave_monthly_spending = total_spend / tenure_months
ave_monthly_spending[tenure_months < 1] = 0  # Setting to 0 for customers with orders on <=1 day
customers_copy['ave_monthly_spending'] = customers_copy['CustomerID'].map(ave_monthly_spending).fillna(0)

# 9. most_ordered_cat: The category of products that the customer ordered the most
most_ordered_cat = orders_with_products.groupby('CustomerID')['Category'].agg(lambda x: x.mode()[0] if not x.mode().empty else None)
customers_copy['most_ordered_cat'] = customers_copy['CustomerID'].map(most_ordered_cat)

df=customers_copy
df.dropna(inplace=True)

from sklearn.preprocessing import StandardScaler

# Drop 'CustomerID' as it is a unique identifier and not a feature for clustering
df_features = df.drop(columns=['CustomerID'])

# Convert categorical columns to numerical format
categorical_columns = df_features.select_dtypes(include=['object']).columns
df_features_encoded = pd.get_dummies(df_features, columns=categorical_columns, drop_first=True)


scaler = StandardScaler()
df_features_scaled = scaler.fit_transform(df_features_encoded)

from sklearn.manifold import TSNE
# Apply t-SNE
tsne_2 = TSNE(n_components=2, random_state=42, perplexity=50, learning_rate=200)
tsne_data_2 = tsne_2.fit_transform(df_features_scaled)

from sklearn.cluster import KMeans
X = tsne_data_2
kmeans = KMeans(n_clusters=64, random_state=42)
cluster_labels = kmeans.fit_predict(X)

from sklearn.metrics import silhouette_score, davies_bouldin_score
silhoette = silhouette_score(X,cluster_labels)
db_score = davies_bouldin_score(X,cluster_labels)


#Output
df['Cluster_Label'] = cluster_labels
print(f"silhouette score is {silhoette}, davies-bouldin index is {db_score}")