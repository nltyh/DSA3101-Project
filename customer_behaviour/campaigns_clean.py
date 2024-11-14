import pandas as pd
import numpy as np
import sqlite3
import gdown
import os

# import file from Google Drive 
file_id = '1mSKamoYumc4Rq5wuCW-NrOd6sFXa8-Wg'
url = f'https://drive.google.com/uc?id={file_id}'
output = 'campaigns.csv'  # Name to save the file
gdown.download(url, output, quiet=False)
df = pd.read_csv(output)

# find columns with missing values
def missing_data(df):
    missing_data = df.isnull().sum()
    return(missing_data[missing_data > 0])

# calculate percentage of missing values
total_rows = len(df)
missing_data = df.isnull().sum()
percentage_missing = (missing_data / total_rows) * 100

# missing report
def missing_report(missing_data, percentage_missing):
    report_df = pd.DataFrame({
        'Column': missing_data.index,
        'Missing Values': missing_data.values,
        'Percentage Missing': percentage_missing.values
    }).sort_values(by='Percentage Missing', ascending=False)

    return report_df

missing_report = missing_report(missing_data, percentage_missing)
print(missing_report)

# drop columns with more than 50% missing values
df.drop(columns=missing_report[missing_report['Percentage Missing'] > 50]['Column'], inplace=True)

# replace missing values in 'topic' with the most frequent value 
df['topic'] = df['topic'].fillna(df['topic'].mode()[0])
# replace missing 'total_count' values in bulk campaigns with mean 
bulk_mean = df.loc[df['campaign_type'] == 'bulk', 'total_count'].mean()
df.loc[df['campaign_type'] == 'bulk', 'total_count'] = df.loc[df['campaign_type'] == 'bulk', 'total_count'].fillna(bulk_mean)
# replace missing 'total_count' values in non-bulk campaigns with 0
df.loc[df['campaign_type'] != 'bulk', 'total_count'] = df.loc[df['campaign_type'] != 'bulk', 'total_count'].fillna(1)
# replace missing values in 'subject_length' with the median
df['subject_length'] = df['subject_length'].fillna(df['subject_length'].median())

# replace binary columns with most frequent value
binary_columns = [
    'subject_with_personalization',
    'subject_with_deadline',
    'subject_with_emoji',
    'subject_with_bonuses',
    'subject_with_discount',
    'subject_with_saleout'
]
for col in binary_columns:
    df[col] = df[col].fillna(df[col].mode()[0])  # most frequent value 

# drop unnecessary columns 
df.drop(columns=['started_at', 'finished_at', 'warmup_mode'], inplace=True)

# check any more missing values
num_na = df.isnull().sum().sum()
print("Number of missing values:", num_na)

# count the number of duplicate rows
num_duplicates = df.duplicated().sum()
print("Number of duplicate rows:", num_duplicates)

# count the number of duplicate columns
duplicate_columns = df.columns[df.columns.duplicated()].tolist()
num_duplicate_columns = len(duplicate_columns)
print("Number of duplicate columns:", num_duplicate_columns)

# find the number of unique primary keys
unique_primary_keys = df[['campaign_type', 'id']].drop_duplicates()
selected_primary_keys = unique_primary_keys.sample(n=118, random_state=1)  # random_state for reproducibility
df = df.merge(selected_primary_keys, on=['campaign_type', 'id'], how='inner')

# print remaining unique channels 
unique_channels = df['channel'].unique()
print(unique_channels)

# cleaned df saved to new csv used in filtering messages.csv
df.to_csv('clean_campaigns.csv', index=False)


# extract 89 unique 'id' out from Messages.db from Google Drive
file_id = '1XBSeL6yuW_IOgRnm2FNr0B9FSVxj0Llv'
url = f'https://drive.google.com/uc?id={file_id}'
output = 'Messages.db'
gdown.download(url, output, quiet=False)
conn = sqlite3.connect(output) 
query = "SELECT DISTINCT campaign_id FROM messages" 
unique_campaign_ids = pd.read_sql_query(query, conn)
conn.close()


# Filter 'id's in the clean campaigns DataFrame
filtered_campaigns = df[df['id'].isin(unique_campaign_ids['campaign_id'])]
filtered_campaigns.to_csv('filtered_clean_campaigns.csv', index=False)

# load files from Google Drive
file_id_campaigns = '1qQO32GRJKi9dvFA-Wy8li2Fbz2vNJ5r0'  # Extracted from the provided link
campaigns_url = f'https://drive.google.com/uc?id={file_id_campaigns}'
campaigns_output = 'filtered_clean_campaigns.csv'
gdown.download(campaigns_url, campaigns_output, quiet=False)

file_id_products = '1ATwj5A6yDHafhI7Az1DKgwX1UsDkuuAn'  # Extracted from the provided link
products_url = f'https://drive.google.com/uc?id={file_id_products}'
products_output = 'Products Table.csv'
gdown.download(products_url, products_output, quiet=False)

campaigns_df = pd.read_csv(campaigns_output)
products_df = pd.read_csv(products_output)

np.random.seed(42)

unique_campaigns = campaigns_df['id'].nunique()
# randomly sample 89 unique product IDs with their prices
sampled_products = products_df[['ProductID', 'Price']].sample(n=unique_campaigns, replace=False, random_state=42)

# reset the indexes of sampled products and campaigns_df to align them
sampled_products = sampled_products.sample(frac=1).reset_index(drop=True)  # shuffle randomly
campaigns_df = campaigns_df.reset_index(drop=True)
campaigns_df['product_id'] = sampled_products['ProductID']
campaigns_df['product_price'] = sampled_products['Price']

# generate synthetic data for products cost 
# assume product prices are marked up between 30% to 50% 

markup_range = (0.30, 0.50) 

def calculate_product_cost(row):
    sold_price = row['product_price']
    markup_percentage = np.random.uniform(markup_range[0], markup_range[1])
    cost_price = sold_price * (1-markup_percentage)
    return round(cost_price,2)

campaigns_df['product_cost'] = campaigns_df.apply(calculate_product_cost, axis = 1)

conversion_ranges = {
    'email': (25, 35),
    'sms': (11, 20),
    'mobile_push': (28, 28),  # fixed value
    'multichannel': (38.5, 38.5)  # fixed value
}

def random_conversion_rate(channel):
    low, high = conversion_ranges[channel]
    if low == high:
        return low  # fixed value case
    return round(np.random.uniform(low, high),2)  # random within range

campaigns_df['percentage_purchased'] = campaigns_df['channel'].apply(random_conversion_rate)
campaigns_df.to_csv('final_campaigns.csv', index=False)

