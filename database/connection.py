import sqlite3
import os


def initialize_db():
        #To ensure that the db folder exists before connecting
        os.makedirs("database", exist_ok=True)

        conn = sqlite3.connect("database/find_iit.db")
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_keys = ON;")

#INDEPENDENT TABLES

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
        
# SEMI-DEPENDENT TABLE

        #Creating the items table

        cursor.execute(""" CREATE TABLE IF NOT EXISTS items(
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL CHECK(type IN ('Lost', 'Found')),
                    status TEXT NOT NULL DEFAULT 'Active',
                    priority_level TEXT DEFAULT 'Low',
                    photo_id TEXT,
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
                     );""")

# FULLY DEPENDENT TABLES

        # Dependent Bridge Entity: Lost Table
        cursor.execute(""" CREATE TABLE IF NOT EXISTS lost(
                    item_id INTEGER NOT NULL,
                    constituent_id INTEGER NOT NULL,
                    date_lost TEXT NOT NULL,
                    location_lost TEXT NOT NULL,
                    PRIMARY KEY (item_id, constituent_id),
                    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
                    FOREIGN KEY (constituent_id) REFERENCES constituents(constituent_id) ON DELETE RESTRICT
                     );""")

        # Dependent Bridge Entity: Found Table
        cursor.execute(""" CREATE TABLE IF NOT EXISTS found(
                    item_id INTEGER NOT NULL,
                    constituent_id INTEGER NOT NULL,
                    date_found TEXT NOT NULL,
                    location_found TEXT NOT NULL,
                    PRIMARY KEY (item_id, constituent_id),
                    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
                    FOREIGN KEY (constituent_id) REFERENCES constituents(constituent_id) ON DELETE RESTRICT
                     );""")

        # Dependent Bridge Entity: Claim Table
        cursor.execute(""" CREATE TABLE IF NOT EXISTS claim(
                    item_id INTEGER NOT NULL,
                    constituent_id INTEGER NOT NULL,
                    claim_date TEXT NOT NULL,
                    claim_status TEXT NOT NULL DEFAULT 'Pending',
                    PRIMARY KEY (item_id, constituent_id),
                    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
                    FOREIGN KEY (constituent_id) REFERENCES constituents(constituent_id) ON DELETE RESTRICT
                     );""")
        
#SEED DATA FOR POPULATING THE CATEGORIES TABLE

        default_categories = [
            ('Electronics',),
            ('Documents & Cards',),
            ('Keys & Keychains',),
            ('Wallets & Bags',),
            ('Books & Stationery',),
            ('Clothing & Accessories',),
            ('Personal Items (Tumblers, Umbrellas)',)
        ]

        cursor.executemany("""INSERT OR IGNORE INTO categories (category_name) VALUES (?);""", 
                           default_categories)
        conn.commit()
        conn.close()


if __name__=='__main__':
      initialize_db()