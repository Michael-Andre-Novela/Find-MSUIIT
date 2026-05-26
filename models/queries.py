import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "find_iit.db")

def get_connection():
	"""Helper function to get a database connection with foreign keys enabled."""
	conn = sqlite3.connect(DB_PATH)
	conn.execute("PRAGMA foreign_keys = ON;")
	# Return rows as dictionaries for easier data handling in Python
	conn.row_factory = sqlite3.Row 
	return conn

# =====================================================================
# 1. CREATE OPERATIONS (Inserting New Data)
# =====================================================================

def add_constituent(id_number, name, contact_email, contact_phone=None):
	with get_connection() as conn:
		cursor = conn.cursor()
		try:
			cursor.execute("""
				INSERT INTO constituents (id_number, name, contact_email, contact_phone)
				VALUES (?, ?, ?, ?)
			""", (id_number, name, contact_email, contact_phone))
			conn.commit()
			return cursor.lastrowid
		except sqlite3.IntegrityError:
			print(f"Error: Constituent with ID {id_number} already exists.")
			return None

def _insert_item_core(cursor, name, description, item_type, category_id, priority_level, photo_id=None):
	"""PRIVATE HELPER: Handles inserting into the main items table and logging."""
	cursor.execute("""
		INSERT INTO items (name, description, type, priority_level, photo_id, category_id, status)
		VALUES (?, ?, ?, ?, ?, ?, 'Active')
	""", (name, description, item_type, priority_level, photo_id, category_id))
    
	item_id = cursor.lastrowid
    
	# Log the creation
	action_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	cursor.execute("""
		INSERT INTO activity_log (item_id, details, actions, action_date)
		VALUES (?, ?, ?, ?)
	""", (item_id, f"Item officially reported to system.", "Created", action_date))
    
	return item_id

def report_lost_item(name, description, category_id, priority_level, constituent_id, date_lost, location_lost, photo_id=None):
	with get_connection() as conn:
		cursor = conn.cursor()
		try:
			item_id = _insert_item_core(cursor, name, description, 'Lost', category_id, priority_level, photo_id)
            
			cursor.execute("""
				INSERT INTO lost (item_id, constituent_id, date_lost, location_lost)
				VALUES (?, ?, ?, ?)
			""", (item_id, constituent_id, date_lost, location_lost))
            
			conn.commit()
			return item_id
		except sqlite3.Error as e:
			conn.rollback()
			print(f"Failed to report lost item: {e}")
			return None

def report_found_item(name, description, category_id, priority_level, constituent_id, date_found, location_found, photo_id=None):
	with get_connection() as conn:
		cursor = conn.cursor()
		try:
			item_id = _insert_item_core(cursor, name, description, 'Found', category_id, priority_level, photo_id)
            
			cursor.execute("""
				INSERT INTO found (item_id, constituent_id, date_found, location_found)
				VALUES (?, ?, ?, ?)
			""", (item_id, constituent_id, date_found, location_found))
            
			conn.commit()
			return item_id
		except sqlite3.Error as e:
			conn.rollback()
			print(f"Failed to report found item: {e}")
			return None

def create_claim_request(item_id, constituent_id, claim_date):
	with get_connection() as conn:
		cursor = conn.cursor()
		try:
			cursor.execute("""
				INSERT INTO claim (item_id, constituent_id, claim_date, claim_status)
				VALUES (?, ?, ?, 'Pending')
			""", (item_id, constituent_id, claim_date))

			cursor.execute("UPDATE items SET status = 'Pending Claim' WHERE item_id = ?", (item_id,))

			action_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			cursor.execute("""
				INSERT INTO activity_log (item_id, details, actions, action_date)
				VALUES (?, ?, ?, ?)
			""", (item_id, f"Constituent ID {constituent_id} requested a claim.", "Claim Requested", action_date))

			conn.commit()
			return True
		except sqlite3.Error as e:
			conn.rollback()
			print(f"Failed to create claim request: {e}")
			return False

# =====================================================================
# 2. READ OPERATIONS (Fetching Data)
# =====================================================================

def get_all_categories():
	with get_connection() as conn:
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM categories ORDER BY category_name")
		return [dict(row) for row in cursor.fetchall()]

def get_constituent_by_school_id(id_number):
	with get_connection() as conn:
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM constituents WHERE id_number = ?", (id_number,))
		row = cursor.fetchone()
		return dict(row) if row else None

def get_active_dashboard_items():
	with get_connection() as conn:
		cursor = conn.cursor()
		cursor.execute("""
			SELECT i.item_id, i.name, i.type, i.priority_level, c.category_name 
			FROM items i
			LEFT JOIN categories c ON i.category_id = c.category_id
			WHERE i.status = 'Active'
			ORDER BY i.item_id DESC
		""")
		return [dict(row) for row in cursor.fetchall()]

def get_item_details(item_id, item_type):
	"""Fetches comprehensive details, joining the correct bridge table based on type."""
	with get_connection() as conn:
		cursor = conn.cursor()
        
		if item_type == 'Lost':
			query = """
				SELECT i.*, c.category_name, l.date_lost as event_date, l.location_lost as event_location,
					   con.name as constituent_name, con.id_number as constituent_id_number
				FROM items i
				LEFT JOIN categories c ON i.category_id = c.category_id
				LEFT JOIN lost l ON i.item_id = l.item_id
				LEFT JOIN constituents con ON l.constituent_id = con.constituent_id
				WHERE i.item_id = ?
			"""
		else:
			query = """
				SELECT i.*, c.category_name, f.date_found as event_date, f.location_found as event_location,
					   con.name as constituent_name, con.id_number as constituent_id_number
				FROM items i
				LEFT JOIN categories c ON i.category_id = c.category_id
				LEFT JOIN found f ON i.item_id = f.item_id
				LEFT JOIN constituents con ON f.constituent_id = con.constituent_id
				WHERE i.item_id = ?
			"""
            
		cursor.execute(query, (item_id,))
		row = cursor.fetchone()
		return dict(row) if row else None

def get_pending_claims():
	with get_connection() as conn:
		cursor = conn.cursor()
		cursor.execute("""
			SELECT cl.claim_date, i.item_id, i.name as item_name, con.name as claimant_name, con.id_number
			FROM claim cl
			JOIN items i ON cl.item_id = i.item_id
			JOIN constituents con ON cl.constituent_id = con.constituent_id
			WHERE cl.claim_status = 'Pending'
		""")
		return [dict(row) for row in cursor.fetchall()]

# =====================================================================
# 3. UPDATE OPERATIONS (Modifying Data)
# =====================================================================

def update_item_status(item_id, current_status):
	with get_connection() as conn:
		cursor = conn.cursor()
		try:
			cursor.execute("UPDATE items SET status = ? WHERE item_id = ?", (current_status, item_id))
            
			action_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			cursor.execute("""
				INSERT INTO activity_log (item_id, details, actions, action_date)
				VALUES (?, ?, ?, ?)
			""", (item_id, f"Admin updated status.", f"Status -> {current_status}", action_date))
            
			conn.commit()
			return True
		except sqlite3.Error as e:
			conn.rollback()
			print(f"Status update failed: {e}")
			return False

def resolve_claim_request(item_id, constituent_id, administrative_action):
	"""administrative_action should be 'Approved' or 'Rejected'"""
	with get_connection() as conn:
		cursor = conn.cursor()
		try:
			# Update claim status
			cursor.execute("""
				UPDATE claim SET claim_status = ? 
				WHERE item_id = ? AND constituent_id = ?
			""", (administrative_action, item_id, constituent_id))

			# Determine new item status based on the action
			new_item_status = 'Claimed' if administrative_action == 'Approved' else 'Active'
			cursor.execute("UPDATE items SET status = ? WHERE item_id = ?", (new_item_status, item_id))

			# Log the resolution
			action_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			cursor.execute("""
				INSERT INTO activity_log (item_id, details, actions, action_date)
				VALUES (?, ?, ?, ?)
			""", (item_id, f"Claim by constituent {constituent_id} was {administrative_action}.", f"Claim {administrative_action}", action_date))

			conn.commit()
			return True
		except sqlite3.Error as e:
			conn.rollback()
			print(f"Claim resolution failed: {e}")
			return False

# =====================================================================
# 4. DELETE OPERATIONS (Removing Data)
# =====================================================================

def remove_item_record(item_id):
	"""Completely removes an item and all associated records (Cascade Delete)."""
	with get_connection() as conn:
		cursor = conn.cursor()
		try:
			cursor.execute("DELETE FROM items WHERE item_id = ?", (item_id,))
			conn.commit()
			return True
		except sqlite3.Error as e:
			print(f"Failed to remove item: {e}")
			return False

# =====================================================================
# 5. ADVANCED SEARCH & FILTERING OPERATIONS
# =====================================================================

def search_active_items(search_query=None, category_id=None, item_type=None):
	"""Dynamic search function based on provided parameters."""
	with get_connection() as conn:
		cursor = conn.cursor()
        
		query = """
			SELECT i.item_id, i.name, i.type, i.priority_level, c.category_name 
			FROM items i
			LEFT JOIN categories c ON i.category_id = c.category_id
			WHERE i.status = 'Active'
		"""
		params = []

		if search_query:
			query += " AND (i.name LIKE ? OR i.description LIKE ?)"
			params.extend([f'%{search_query}%', f'%{search_query}%'])
            
		if category_id:
			query += " AND i.category_id = ?"
			params.append(category_id)
            
		if item_type:
			query += " AND i.type = ?"
			params.append(item_type)
            
		query += " ORDER BY i.item_id DESC"
        
		cursor.execute(query, params)
		return [dict(row) for row in cursor.fetchall()]

# =====================================================================
# 6. AGGREGATIONS & ANALYTICS OPERATIONS
# =====================================================================

def get_dashboard_statistics():
	"""Returns a dictionary of core metrics for the admin dashboard."""
	stats = {
		"active_lost": 0,
		"active_found": 0,
		"pending_claims": 0,
		"total_claimed": 0
	}
    
	with get_connection() as conn:
		cursor = conn.cursor()
        
		# Count Active Lost
		cursor.execute("SELECT COUNT(*) FROM items WHERE type='Lost' AND status='Active'")
		stats["active_lost"] = cursor.fetchone()[0]
        
		# Count Active Found
		cursor.execute("SELECT COUNT(*) FROM items WHERE type='Found' AND status='Active'")
		stats["active_found"] = cursor.fetchone()[0]
        
		# Count Pending Claims
		cursor.execute("SELECT COUNT(*) FROM claim WHERE claim_status='Pending'")
		stats["pending_claims"] = cursor.fetchone()[0]
        
		# Count Total Claimed (Resolved Items)
		cursor.execute("SELECT COUNT(*) FROM items WHERE status='Claimed'")
		stats["total_claimed"] = cursor.fetchone()[0]
        
	return stats

def get_frequent_lost_locations(limit=5):
	"""Finds the most common locations where items are reported lost."""
	with get_connection() as conn:
		cursor = conn.cursor()
		cursor.execute("""
			SELECT location_lost as location, COUNT(*) as incident_count 
			FROM lost 
			GROUP BY location_lost 
			ORDER BY incident_count DESC 
			LIMIT ?
		""", (limit,))
		return [dict(row) for row in cursor.fetchall()]

# =====================================================================
# 7. SYSTEM UTILITIES & MAINTENANCE
# =====================================================================

def verify_database_integrity():
	"""Runs an internal SQLite check to ensure database file isn't corrupted."""
	with get_connection() as conn:
		cursor = conn.cursor()
		cursor.execute("PRAGMA integrity_check;")
		result = cursor.fetchone()
		return result[0] == "ok"

def optimize_database():
	"""Rebuilds the database file, reclaiming unused space."""
	with get_connection() as conn:
		try:
			conn.execute("VACUUM;")
			return True
		except sqlite3.Error as e:
			print(f"Failed to optimize database: {e}")
			return False
