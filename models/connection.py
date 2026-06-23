import sqlite3
import os
from datetime import datetime

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
	    status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Claimed', 'Archived')),
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
	    claim_status TEXT NOT NULL DEFAULT 'Pending' CHECK(claim_status IN ('Pending', 'Approved', 'Rejected')),
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

	def ensure_constituent(id_number, name, contact_email, contact_phone=None):
		cursor.execute("SELECT constituent_id FROM constituents WHERE id_number = ? OR name = ?", (id_number, name))
		row = cursor.fetchone()
		if row:
			cursor.execute("""
				UPDATE constituents
				SET id_number = ?, name = ?, contact_email = ?, contact_phone = ?
				WHERE constituent_id = ?
			""", (id_number, name, contact_email, contact_phone, row[0]))
			return row[0]

		cursor.execute("""
			INSERT INTO constituents (id_number, name, contact_email, contact_phone)
			VALUES (?, ?, ?, ?)
		""", (id_number, name, contact_email, contact_phone))
		return cursor.lastrowid

	def ensure_item(name, description, item_type, status, priority_level, category_id, photo_filepath=None):
		cursor.execute("SELECT item_id FROM items WHERE name = ?", (name,))
		row = cursor.fetchone()
		if row:
			return row[0]

		cursor.execute("""
			INSERT INTO items (name, description, type, status, priority_level, photo_filepath, category_id)
			VALUES (?, ?, ?, ?, ?, ?, ?)
		""", (name, description, item_type, status, priority_level, photo_filepath, category_id))
		return cursor.lastrowid

	def ensure_created_log(item_id, details):
		cursor.execute(
			"SELECT 1 FROM activity_log WHERE item_id = ? AND actions = 'Created' AND details = ?",
			(item_id, details)
		)
		if cursor.fetchone():
			return
		cursor.execute("""
			INSERT INTO activity_log (item_id, details, actions, action_date)
			VALUES (?, ?, 'Created', ?)
		""", (item_id, details, datetime.now().strftime("%Y-%m-%d %H:%M")))

	def ensure_claim(item_id, constituent_id, claim_date, claim_status):
		cursor.execute("SELECT 1 FROM claim WHERE item_id = ?", (item_id,))
		if cursor.fetchone():
			return
		cursor.execute("""
			INSERT INTO claim (item_id, constituent_id, claim_date, claim_status)
			VALUES (?, ?, ?, ?)
		""", (item_id, constituent_id, claim_date, claim_status))

	def seed_mock_data():
		cursor.execute("SELECT category_id, category_name FROM categories")
		category_map = {row[1]: row[0] for row in cursor.fetchall()}

		alice_id = ensure_constituent("2026-0001", "Alice Cruz", "alice.cruz@msuiit.edu.ph", "0917000001")
		ben_id = ensure_constituent("2026-0002", "Ben Dela Cruz", "ben.delacruz@msuiit.edu.ph", "0917000002")
		carla_id = ensure_constituent("2026-0003", "Carla Reyes", "carla.reyes@msuiit.edu.ph", "0917000003")
		diego_id = ensure_constituent("2026-0004", "Diego Santos", "diego.santos@msuiit.edu.ph", "0917000004")
		eva_id = ensure_constituent("2026-0005", "Eva Lim", "eva.lim@msuiit.edu.ph", "0917000005")

		seed_date = "2026-06-07"

		seed_items = [
			{
				"name": "Mock - Black Calculator",
				"description": "Black scientific calculator with a worn keypad.",
				"type": "Lost",
				"status": "Active",
				"priority_level": "High",
				"category": "Electronics",
				"constituent_id": alice_id,
				"event_date": "2026-06-01",
				"location_column": "location_lost",
				"location": "Engineering Building - Room 210",
				"claim": None,
			},
			{
				"name": "Mock - Blue Umbrella",
				"description": "Foldable blue umbrella left in the library lobby.",
				"type": "Found",
				"status": "Active",
				"priority_level": "Medium",
				"category": "Personal Items (Tumblers, Umbrellas)",
				"constituent_id": ben_id,
				"event_date": "2026-06-02",
				"location_column": "location_found",
				"location": "Library Lobby",
				"claim": {"constituent_id": carla_id, "status": "Pending"},
			},
			{
				"name": "Mock - Student ID Card",
				"description": "Student ID card in a clear sleeve.",
				"type": "Lost",
				"status": "Claimed",
				"priority_level": "Low",
				"category": "Documents & Cards",
				"constituent_id": diego_id,
				"event_date": "2026-06-03",
				"location_column": "location_lost",
				"location": "Cafeteria",
				"claim": {"constituent_id": ben_id, "status": "Approved"},
			},
			{
				"name": "Mock - Brown Wallet",
				"description": "Brown leather wallet with a campus card holder.",
				"type": "Found",
				"status": "Archived",
				"priority_level": "Low",
				"category": "Wallets & Bags",
				"constituent_id": eva_id,
				"event_date": "2026-06-04",
				"location_column": "location_found",
				"location": "Parking Area A",
				"claim": None,
			},
		]

		for seed in seed_items:
			item_id = ensure_item(
				name=seed["name"],
				description=seed["description"],
				item_type=seed["type"],
				status=seed["status"],
				priority_level=seed["priority_level"],
				category_id=category_map[seed["category"]],
			)

			bridge_table = "lost" if seed["type"] == "Lost" else "found"
			date_value = "date_lost" if seed["type"] == "Lost" else "date_found"
			location_value = seed["location_column"]

			cursor.execute(f"SELECT 1 FROM {bridge_table} WHERE item_id = ?", (item_id,))
			if cursor.fetchone() is None:
				cursor.execute(
					f"""
					INSERT INTO {bridge_table} (item_id, constituent_id, {date_value}, {location_value})
					VALUES (?, ?, ?, ?)
					""",
					(item_id, seed["constituent_id"], seed["event_date"], seed["location"]),
				)

			ensure_created_log(item_id, f"Mock data seeded for {seed['name']}.")

			if seed["claim"]:
				ensure_claim(item_id, seed["claim"]["constituent_id"], seed_date, seed["claim"]["status"])

			if seed["status"] != "Active":
				cursor.execute("SELECT 1 FROM activity_log WHERE item_id = ? AND actions = ?", (item_id, f"Status -> {seed['status']}"))
				if cursor.fetchone() is None:
					cursor.execute("""
						INSERT INTO activity_log (item_id, details, actions, action_date)
						VALUES (?, ?, ?, ?)
					""", (item_id, f"Mock item status initialized to {seed['status']}.", f"Status -> {seed['status']}", datetime.now().strftime("%Y-%m-%d %H:%M")))

	seed_mock_data()
	conn.commit()
	conn.close()


if __name__=='__main__':
      initialize_db()
