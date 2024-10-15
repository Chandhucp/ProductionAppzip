import sqlite3

def create_table():
    conn = sqlite3.connect('production.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS production_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    received_time_est TEXT,
                    received_time_ist TEXT,
                    pims_id INTEGER,
                    completed_time_est TEXT,
                    completed_time_ist TEXT,
                    completed_by TEXT
                )''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table()
    print("Database and table created successfully.")
