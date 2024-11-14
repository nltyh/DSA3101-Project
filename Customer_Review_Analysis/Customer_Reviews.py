# Load the required libraries
import pandas as pd
import numpy as np
import random
random.seed(42)

amazon = pd.read_csv("amazon.csv")
# rating_count has 2 missing entries, accounting for 0.0014% of all observations
print(amazon.isnull().sum())

# No duplicated observations
print(amazon.duplicated().value_counts())

# Remove unnecessary columns
amazon = amazon[['category', 'actual_price', 'rating', 'review_id', 'review_title', 'review_content']]

# 2. Data type Conversions (Transforming numeric columns to make them look nicer)
amazon['actual_price'] = amazon['actual_price'].astype(str).str.replace('₹', '')
amazon['actual_price'] = amazon['actual_price'].str.replace(',', '')
amazon['actual_price'] = pd.to_numeric(amazon['actual_price'])

amazon['rating'] = amazon['rating'].str.replace('|', '')
amazon['rating'] = pd.to_numeric(amazon['rating'])

amazon['actual_price'] = round(amazon['actual_price']*0.012, 2)
amazon = amazon.rename(columns = {'actual_price': 'actual_price (USD)'})

amazon['category'] = amazon['category'].str.split('|').str[0]
amazon['category'].unique()

remove_set = {"MusicalInstruments", "OfficeProducts", "Toys&Games", "Car&Motorbike", "Health&PersonalCare", "Home&Kitchen", "HomeImprovement"}
amazon = amazon[~amazon['category'].isin(remove_set)]

amazon['category'] = amazon['category'].replace(["Computers&Accessories"], "Electronics")

amazon['category'] = amazon.category.astype('category')
amazon['category'].unique()

# Remove missing values
amazon.dropna(subset = ['rating'], inplace = True)

# 2. Sample order IDs from the orders table. Order ID is the primary key linking the Reviews Table to the Orders Table
orders = pd.read_csv("Orders Table.csv")

# Obtain the order_ID from Orders table, and assign without replacement
def assign_randomID(amazon, orders):
    # Randomly sample WITHOUT replacement
    sampled_ids = random.sample(list(orders['OrderID']), len(amazon))

    # Assign sampled order IDs to the DataFrame
    amazon['Order_ID'] = sampled_ids

    return amazon

amazons = assign_randomID(amazon, orders)
amazons['Order_ID'] = amazons['Order_ID'].astype(pd.StringDtype())

# Final checks
print(amazons.isnull().sum())    # No null values
# Drop observations which have duplicated order IDs
amazons.drop_duplicates(subset='Order_ID', keep=False)
amazons['review_id'] = amazons['review_id'].astype(pd.StringDtype())

# Finally, save the reviews table as a csv file
# amazons.to_csv("reviews_table.csv", index=False)