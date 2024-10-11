import pandas as pd
import numpy as np

df = pd.read_csv("clean_campaigns.csv")
print(df.columns)

print(df.dtypes)

# Find the number of unique primary keys
unique_primary_keys = df[['campaign_type', 'id']].drop_duplicates()

# Get the number of unique primary key combinations
num_unique_primary_keys = len(unique_primary_keys)
print("Number of unique primary keys:", num_unique_primary_keys)
