import pandas as pd
import numpy as np

df = pd.read_csv('campaigns.csv')

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

# leftover columns with missing data
left_missing = df.isnull().sum()
print(left_missing[left_missing > 0])

# start replacing missing data 

# replace missing values in 'topic' with the most frequent value 
df['topic'] = df['topic'].fillna(df['topic'].mode()[0])

# replace missing 'total_count' values in bulk campaigns with mean 
bulk_mean = df.loc[df['campaign_type'] == 'bulk', 'total_count'].mean()
df.loc[df['campaign_type'] == 'bulk', 'total_count'] = df.loc[df['campaign_type'] == 'bulk', 'total_count'].fillna(bulk_mean)
# replace missing 'total_count' values in non-bulk campaigns with 0
df.loc[df['campaign_type'] != 'bulk', 'total_count'] = df.loc[df['campaign_type'] != 'bulk', 'total_count'].fillna(0)

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
    df[col] = df[col].fillna(df[col].mode()[0])  # mode()[0] gives the most frequent value

# drop started_at, finished_at and warmup_mode columns 
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

### add this part into doc 

# Find the number of unique primary keys
unique_primary_keys = df[['campaign_type', 'id']].drop_duplicates()
selected_primary_keys = unique_primary_keys.sample(n=118, random_state=1)  # random_state for reproducibility

# Merge the selected primary keys back to the original DataFrame to filter rows
df = df.merge(selected_primary_keys, on=['campaign_type', 'id'], how='inner')

# cleaned df saved to new csv
df.to_csv('clean_campaigns.csv', index=False)




