import pandas as pd
import numpy as np

df = pd.read_csv('clean_messages.csv')
print(df.columns)
print(df.dtypes)

# Find the number of unique primary keys based on a single column (e.g., 'campaign_id')
num_unique_primary_keys = df['message_id'].nunique()

print("Number of unique primary keys:", num_unique_primary_keys)
