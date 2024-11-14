import numpy as np 
import pandas as pd 

df = pd.read_csv("ecommerce_customer_data_large.csv")
df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], format='%Y-%m-%d %H:%M:%S')

"""
Checking if 'Total Purchase Amount' is consistently equal to 'Product Price' * 'Quantity' for each row.
"""
df['Calculated_Total'] = df['Product Price'] * df['Quantity']

# Find rows where the calculated total does not match the given 'Total Purchase Amount'
inconsistent_rows = df[df['Total Purchase Amount'] != df['Calculated_Total']]

# Calculate the number and percentage of inconsistent rows
num_inconsistent = inconsistent_rows.shape[0]
percentage_inconsistent = (num_inconsistent / df.shape[0]) * 100

num_inconsistent, percentage_inconsistent

"""
From the info we can see that :
# the 2 columns are exactly the same, remove duplicate column
"""

sum(df['Age'] == df['Customer Age'])


"""
number of missing records in each column:
Returns column has 47382 missing records, around 0.19 of the dataset
"""

def generate_na_report(df):

    na_report = df.isna().sum().reset_index()
    na_report.columns = ["Variable", "NA_cnt"]
    na_report["Perc"] = na_report["NA_cnt"] / df.shape[0]
    
    return na_report

generate_na_report(df)


"""
Drop the 'Customer Age' column in place as it was duplicated
Drop the name of the customer since Customer ID is already unique identifier
Drop the rows with missing returns 
"""
df.drop(columns=['Customer Age', 'Customer Name'], inplace=True)
df.dropna(axis=0, inplace=True)


"""
There is no duplicates after dropping columns and rows
"""
sum(df.duplicated())

# Convert 'Returns' column to integer
df['Returns'] = df['Returns'].astype(int)

"""Remove unwanted category that we are not using in our ecommerce company"""
df =  df[df['Product Category'] != 'Books']

df.to_csv('customer_dataset_1.csv')