import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "find_iit.db")

def initialize_db():
	#To ensure that the db folder exists before connecting
	os.makedirs(DB_DIR, exist_ok=True)

	conn = sqlite3.connect(DB_PATH)
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
	    status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Claimed')),
	    priority_level TEXT DEFAULT 'Low' CHECK(priority_level IN ('Low', 'Medium', 'High')),
	    photo_filepath TEXT,
		    category_id INTEGER,
		    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
		     );""")
        
# FULLY DEPENDENT TABLES

	# Dependent Bridge Entity: Lost Table
	cursor.execute(""" CREATE TABLE IF NOT EXISTS lost(
	    item_id INTEGER PRIMARY KEY,
		    constituent_id INTEGER NOT NULL,
	    date_lost TEXT NOT NULL CHECK(date_lost GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
		    location_lost TEXT NOT NULL,
		    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
		    FOREIGN KEY (constituent_id) REFERENCES constituents(constituent_id) ON DELETE RESTRICT
		     );""")

	# Dependent Bridge Entity: Found Table
	cursor.execute(""" CREATE TABLE IF NOT EXISTS found(
	    item_id INTEGER PRIMARY KEY,
		    constituent_id INTEGER NOT NULL,
	    date_found TEXT NOT NULL CHECK(date_found GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
		    location_found TEXT NOT NULL,
		    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
		    FOREIGN KEY (constituent_id) REFERENCES constituents(constituent_id) ON DELETE RESTRICT
		     );""")

	# Dependent Bridge Entity: Claim Table
	cursor.execute(""" CREATE TABLE IF NOT EXISTS claim(
	    item_id INTEGER PRIMARY KEY,
		    constituent_id INTEGER NOT NULL,
	    claim_date TEXT NOT NULL CHECK(claim_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
	    claim_status TEXT NOT NULL DEFAULT 'Pending' CHECK(claim_status IN ('Pending', 'Approved')),
		    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
		    FOREIGN KEY (constituent_id) REFERENCES constituents(constituent_id) ON DELETE RESTRICT
		     );""")
        
	# Creating the Activity_Log table
	cursor.execute(""" CREATE TABLE IF NOT EXISTS activity_log(
		    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
		    item_id INTEGER NOT NULL,
		    details TEXT NOT NULL,
		    actions TEXT NOT NULL,
	    action_date TEXT NOT NULL CHECK(action_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]'),
		    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
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
