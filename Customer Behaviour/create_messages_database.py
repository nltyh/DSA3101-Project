import sqlite3

# Database name
database_name = 'Messages.db'

# Connect to the database (it will be created if it doesn't exist)
conn = sqlite3.connect(database_name)
cursor = conn.cursor()

# Create the 'messages' table with the specified schema
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    message_id TEXT PRIMARY KEY,
    campaign_id INTEGER,
    message_type TEXT,
    client_id INTEGER,
    channel TEXT,
    stream TEXT,
    date DATETIME,
    sent_at DATETIME,
    is_opened BOOLEAN,
    is_clicked BOOLEAN,
    is_unsubscribed BOOLEAN,
    is_complained BOOLEAN,
    is_blocked BOOLEAN,
    is_purchased BOOLEAN
);
''')

# Commit changes and close the connection
conn.commit()
conn.close()