import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('gmail_accounts.db')
cursor = conn.cursor()

now = datetime.now()
verification_time = now + timedelta(days=3)

# Update records with null verification_time
cursor.execute("UPDATE accounts SET verification_time = ? WHERE verification_time IS NULL", (verification_time,))
conn.commit()
conn.close()