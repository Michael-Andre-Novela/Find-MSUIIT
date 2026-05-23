import sqlite3
import os


def independent_tables():
        #To ensure that the db folder exists before connecting
        os.makedirs("database", exist_ok=True)

        conn = sqlite3.connect("database/find_iit.db")
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_keys = ON;")

        #Creating the Categories tables

        cursor.execute("""CREATE TABLE IF NOT EXISTS categories(
                       category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       category_name TEXT NOT NULL UNIQUE
                       );
                    """)
        #Creating the Constituents tables

        cursor.execute(""" CREATE TABLE IF NOT EXISTS constituents(
                    constituent_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_number TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    contact_email TEXT NOT NULL,
                    contact_phone TEXT
                     );""")
        conn.commit()
        conn.close()

        
