# Load the required libraries
from faker import Faker
import pandas as pd
import numpy as np
import string
import random
random.seed(42)
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
fake = Faker()

# Download the Amazon Sales Data set from this site and save onto your device. This will contain products on Electronics and Home Appliances categories
# https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset/data

# Download Amazon Clothing.csv 2023 below. This will contain products on Clothing category.
# https://www.kaggle.com/datasets/lokeshparab/amazon-products-dataset?select=Clothing.csv

# Change your working directory to access the file in its location
import os
os.getcwd()
# os.chdir("C:/...")

# Data inspection, transformation of features
amazon_sales = pd.read_csv("amazon.csv")
amazon_sales.dtypes
amazon_sales.isnull().sum()                  # 2 observations have null rating

amazon_sales.dropna(subset = ['rating'], inplace = True)

# Keep only important columns
amazon_sales = amazon_sales[['category', 'actual_price', 'rating', 'review_id']]

# Transform actual_price and rating into numeric data types
# Rename the columns and convert actual_price from rupees to USD
amazon_sales['actual_price'] = amazon_sales['actual_price'].astype(str).str.replace('₹', '')
amazon_sales['actual_price'] = amazon_sales['actual_price'].str.replace(',', '')
amazon_sales['actual_price'] = pd.to_numeric(amazon_sales['actual_price'])

amazon_sales['rating'] = amazon_sales['rating'].str.replace('|', '')
amazon_sales['rating'] = pd.to_numeric(amazon_sales['rating'])

amazon_sales['actual_price'] = round(amazon_sales['actual_price']*0.012, 2)

amazon_sales['category'] = amazon_sales['category'].str.split('|').str[0]

# Remove categories that are not central to our analysis (We only want Home Appliances, Electronics, Clothing)
remove_set = {"MusicalInstruments", "OfficeProducts", "Toys&Games", "Car&Motorbike", "Health&PersonalCare"}
amazon_sales = amazon_sales[~amazon_sales['category'].isin(remove_set)]

# We will only have two main categories: Home appliances and Electronics
amazon_sales['category'] = amazon_sales['category'].replace(["Home&Kitchen"], "Home Appliances")
amazon_sales['category'] = amazon_sales['category'].replace(["Computers&Accessories"], "Electronics")
amazon_sales['category'] = amazon_sales['category'].replace(["HomeImprovement"], "Home Appliances")

amazon_sales['category'] = amazon_sales.category.astype('category')

# Simplify the review_ids, only keep the first string of review_id of observation
amazon_sales['review_id'] = amazon_sales['review_id'].str.split(',').str[0]
amazon_sales = amazon_sales.rename(columns = {'actual_price': 'Price', 'category': 'Category', 'rating': 'Rating'})

amazon_sales.dropna(subset = ['Rating'], inplace = True)  # Remove null Rating
amazon_sales = amazon_sales.drop_duplicates()          # Remove all duplicated rows

# We only have two product categories! We use another dataset, clothing.csv from Amazon Kaggle 2023, entirely on product category "Clothing"
clothing = pd.read_csv("Clothing.csv")

# Keep only important columns
clothing = clothing[['sub_category', 'actual_price', 'ratings']]

# Remove observations with missing values
clothing.isnull().sum()
clothing.dropna(subset = ['ratings'], inplace = True)
clothing.dropna(subset = ['actual_price'], inplace = True)

# Transform actual_price and rating into numeric data types
# Rename the columns and convert actual_price from rupees to USD
clothing['actual_price'] = clothing['actual_price'].astype(str).str.replace('₹', '')
clothing['actual_price'] = clothing['actual_price'].str.replace(',', '')
clothing['actual_price'] = pd.to_numeric(clothing['actual_price'])

clothing['ratings'] = pd.to_numeric(clothing['ratings'], errors = 'coerce')

clothing['actual_price'] = round(clothing['actual_price']*0.012, 2)
clothing['sub_category'] = clothing['sub_category'].astype('category')
clothing = clothing.rename(columns = {'actual_price': 'Price', 'sub_category': 'Category', 'ratings':'Rating'})

clothing.dropna(subset = ['Rating'], inplace = True)  # Remove null Rating
clothing = clothing.drop_duplicates()           # Drop all duplicated rows
clothing.head()

# 1. Generate review IDs for the Clothing observations, use the first review_id of amazon_sales as the sample
# amazon_sales['review_id'].str.split(',').str[0].head(1)  # "R3HXWT0LRP0NMF"

# Generate synthetic review IDs based on the sample review_id using a function using an imported library inside
def generate(sample_id, x):
    first = sample_id[0]  # Sample the 'R'
    
    # Synthetic IDs by generating random strings of the same length (consisting of both letters and numbers)
    lst = []
    for _ in range(x):
        random_body = ''.join(random.choices(string.ascii_uppercase + string.digits, k=len(sample_id)-1))
        synthetic_id = first + random_body
        lst.append(synthetic_id)
    
    return lst

review_ids = generate("R3HXWT0LRP0NMF", len(clothing))

# Add the generated synthetic review_ids to the clothing dataset as a new column
clothing['review_id'] = review_ids

# Add clothing dataset under amazon_sales dataset, and review_id should be of type string
amazons = pd.concat([amazon_sales, clothing])
amazons['review_id'] = amazons['review_id'].astype(pd.StringDtype())
amazons.head()

# 2. Sample order IDs from the orders table. This will be the primary key between orders table and reviews table
orders = pd.read_csv("Orders Table.csv")

# Obtain the order_ID from Orders table, and assign randomly
def assign_randomID(amazons, orders):
    # Randomly sample WITHOUT replacement
    sampled_ids = random.sample(list(orders['OrderID']), len(amazons))

    # Assign sampled order IDs to the DataFrame
    amazons['Order_ID'] = sampled_ids

    return amazons

amazons = assign_randomID(amazons, orders)
amazons['Order_ID'] = amazons['Order_ID'].astype(pd.StringDtype())

# Final checks
amazons.isnull().sum()     # No null values
# Drop observations which have duplicated order and review ids
amazons.drop_duplicates(subset='Order_ID', keep=False)
amazons.drop_duplicates(subset='review_id', keep=False)

# Finally, save the reviews table as a csv file
amazons.to_csv("reviews.csv", index=False)
