import pandas as pd
import sqlite3

"""
since the cleaning code works, 
we will use it to clean by batch and add it to a database
"""
# Reading the first few rows of the CSV file
chunk_size = 10**5  # Adjust the chunk size as needed
database_name = 'Messages.db'
table_name = 'messages'

def clean_chunk(chunk):
    # Drop unnecessary columns
    chunk.drop(labels=['id', 'created_at', 'updated_at', 'category', 
                       'email_provider', 'is_hard_bounced', 'is_soft_bounced'], 
               inplace=True, axis=1)
    
    # Convert 't' and 'f' to boolean values
    def convert_to_bool(value):
        return value == 't'

    boolean_columns = ['is_opened', 'is_clicked', 'is_unsubscribed', 
                       'is_complained', 'is_blocked', 'is_purchased']
    for col in boolean_columns:
        chunk[col] = chunk[col].apply(convert_to_bool)
    
    # Convert date columns to datetime
    datetime_columns = ['date', 'sent_at', 'opened_first_time_at', 
                        'opened_last_time_at', 'clicked_first_time_at', 
                        'clicked_last_time_at', 'unsubscribed_at', 
                        'hard_bounced_at', 'soft_bounced_at', 
                        'complained_at', 'blocked_at', 'purchased_at']
    for col in datetime_columns:
        chunk[col] = pd.to_datetime(chunk[col], errors='coerce')
    
    # List of columns to drop based on the NA missing report while testing cleaning code
    columns_with_many_NA = [
    'purchased_at', 'blocked_at', 'complained_at', 'soft_bounced_at',
    'unsubscribed_at', 'clicked_first_time_at', 'clicked_last_time_at',
    'hard_bounced_at', 'platform', 'opened_first_time_at', 'opened_last_time_at'
    ]

    # Drop the specified columns
    chunk.drop(columns=columns_with_many_NA, inplace=True)
    
    
    return chunk

# Create a new SQLite database and connect to it
conn = sqlite3.connect(database_name)
i = 0
# Process the file in chunks
for chunk in pd.read_csv('Messages_filtered.csv', chunksize=chunk_size, low_memory=False):
    cleaned_chunk = clean_chunk(chunk)
    # Write the cleaned chunk to the SQLite database
    cleaned_chunk.to_sql(table_name, conn, if_exists='append', index=False)

    #track the iterations
    print(i)
    i+=1

# Close the database connection
conn.close()

print("done")


"""
Copied from messages_demo_clean.py
I checked the code to clean the df, it worked, below is the code for your reference 
"""
messages_df = pd.read_csv("Messages_filtered.csv", nrows=1000)  # Read the first 1000 rows

# Make some cleanup (delete unnecessary columns) and processing
messages_df.drop(labels=['id', 'created_at', 'updated_at', 'category','email_provider', 'is_hard_bounced', 'is_soft_bounced'], inplace=True, axis=1)

def convert_to_bool(value):
    if value == 't':
        return True
    else:
        return False

messages_df['is_opened'] = messages_df['is_opened'].apply(convert_to_bool)
messages_df['is_clicked'] = messages_df['is_clicked'].apply(convert_to_bool)
messages_df['is_unsubscribed'] = messages_df['is_unsubscribed'].apply(convert_to_bool)
messages_df['is_complained'] = messages_df['is_complained'].apply(convert_to_bool)
messages_df['is_blocked'] = messages_df['is_blocked'].apply(convert_to_bool)
messages_df['is_purchased'] = messages_df['is_purchased'].apply(convert_to_bool)

messages_df['date'] = pd.to_datetime(messages_df['date'])
messages_df['sent_at'] = pd.to_datetime(messages_df['sent_at'])
messages_df['opened_first_time_at'] = pd.to_datetime(messages_df['opened_first_time_at'])
messages_df['opened_last_time_at'] = pd.to_datetime(messages_df['opened_last_time_at'])
messages_df['clicked_first_time_at'] = pd.to_datetime(messages_df['clicked_first_time_at'])
messages_df['clicked_last_time_at'] = pd.to_datetime(messages_df['clicked_last_time_at'])
messages_df['unsubscribed_at'] = pd.to_datetime(messages_df['unsubscribed_at'])
messages_df['hard_bounced_at'] = pd.to_datetime(messages_df['hard_bounced_at'])
messages_df['soft_bounced_at'] = pd.to_datetime(messages_df['soft_bounced_at'])
messages_df['complained_at'] = pd.to_datetime(messages_df['complained_at'])
messages_df['blocked_at'] = pd.to_datetime(messages_df['blocked_at'])
messages_df['purchased_at'] = pd.to_datetime(messages_df['purchased_at'])

# find columns with missing values
def missing_data(df):
    missing_data = df.isnull().sum()
    return(missing_data[missing_data > 0])

# calculate percentage of missing values
total_rows = len(messages_df)
missing_data = messages_df.isnull().sum()
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
messages_df.drop(columns=missing_report[missing_report['Percentage Missing'] > 50]['Column'], inplace=True)

# leftover columns with missing data
left_missing = messages_df.isnull().sum()
print(left_missing[left_missing > 0])

num_na = messages_df.isnull().sum().sum()
print("Number of missing values:", num_na)

# count the number of duplicate rows
num_duplicates = messages_df.duplicated().sum()
print("Number of duplicate rows:", num_duplicates)

# count the number of duplicate columns
duplicate_columns = messages_df.columns[messages_df.columns.duplicated()].tolist()
num_duplicate_columns = len(duplicate_columns)
print("Number of duplicate columns:", num_duplicate_columns)

print(len(messages_df))
unique_values = messages_df['client_id'].nunique()
print(unique_values)

messages_df.to_csv('clean_messages.csv', index=False)



