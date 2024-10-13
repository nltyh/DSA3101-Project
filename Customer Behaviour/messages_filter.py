import pandas as pd

# Reading the clean campaigns CSV file into memory
campaign = pd.read_csv("clean_campaigns.csv")

# Extracting unique campaign_ids from the campaigns DataFrame
campaign_ids = set(campaign['id'].unique())  # Convert to set for faster lookups

# Define the output file path
output_file = "Messages_filtered.csv"

#reset i and remove the rows to skip, if you are starting from the start
# Initialize the output CSV by writing the header (first chunk)
chunksize = 10**4  # Adjust chunk size as needed
i = 44537
# Set the number of rows to skip cus i paused halfway
rows_to_skip = 44536 * 10**4
for chunk in pd.read_csv("messages.csv", chunksize=chunksize, skiprows=range(1, rows_to_skip + 1)):
    
    print(i)
    i+=1
    # Filtering the chunk to only include rows where campaign_id is in campaign_ids
    filtered_chunk = chunk[chunk['campaign_id'].isin(campaign_ids)]
    
    # Append each filtered chunk to the CSV file
    if len(filtered_chunk) > 0:
        filtered_chunk.to_csv(output_file, mode='a', header=False)
    else: continue


"""
Check how many unique campaign ids are there in messages csv

"""
# Initialize an empty set to store unique campaign_ids
unique_campaign_ids = set()

# Define the chunk size
chunksize = 10**5  # Adjust the chunk size based on your memory constraints

# Process the file in chunks
for chunk in pd.read_csv('Messages_filtered.csv', chunksize=chunksize, usecols=['campaign_id']):
    # Update the set with unique campaign_ids from each chunk
    unique_campaign_ids.update(chunk['campaign_id'].unique())

# Check the number of unique campaign_ids
print(f"Number of unique campaign_ids: {len(unique_campaign_ids)}")

unique_campaign_ids