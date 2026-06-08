import sqlite3
import datetime
import os
import re

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "find_iit.db")

_ID_NUMBER_PATTERN = re.compile(r"^\d{4}-\d{4}$")
_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def get_connection():
	"""Helper function to get a database connection with foreign keys enabled.""" 
	conn = sqlite3.connect(DB_PATH)
	conn.execute("PRAGMA foreign_keys = ON;")
	conn.row_factory = sqlite3.Row
	return conn   
    
# =====================================================================
# 1. CREATE OPERATIONS (Inserting New Data)
# =====================================================================

def add_constituent(id_number, name, contact_email, contact_phone=None):
	if not _ID_NUMBER_PATTERN.match(id_number):
		msg = f"Invalid id_number format: '{id_number}'. Expected YYYY-NNNN."
		print(msg)
		return None

	if not _EMAIL_PATTERN.match(contact_email):
		msg = f"Invalid contact_email format: '{contact_email}'. Expected a valid email address."
		print(msg)
		return None

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

def _insert_item_core(cursor, name, description, item_type, category_id, priority_level, photo_filepath=None):
	"""PRIVATE HELPER: Handles inserting into the main items table and logging."""
	cursor.execute("""
		INSERT INTO items (name, description, type, priority_level, photo_filepath, category_id, status)
		VALUES (?, ?, ?, ?, ?, ?, 'Active')
	""", (name, description, item_type, priority_level, photo_filepath, category_id))
    
	item_id = cursor.lastrowid
    
	# Log the creation
	action_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	cursor.execute("""
		INSERT INTO activity_log (item_id, details, actions, action_date)
		VALUES (?, ?, ?, ?)
	""", (item_id, f"Item officially reported to system.", "Created", action_date))
    
	return item_id

def report_lost_item(name, description, category_id, priority_level, constituent_id, date_lost, location_lost, photo_filepath=None):
	# Validate date format YYYY-MM-DD
	try:
		datetime.datetime.strptime(date_lost, "%Y-%m-%d")
	except Exception:
		msg = f"Invalid date_lost format: '{date_lost}'. Expected YYYY-MM-DD."
		print(msg)
		return False, msg

	with get_connection() as conn:
		cursor = conn.cursor()
		try:
			item_id = _insert_item_core(cursor, name, description, 'Lost', category_id, priority_level, photo_filepath)

			cursor.execute("""
				INSERT INTO lost (item_id, constituent_id, date_lost, location_lost)
				VALUES (?, ?, ?, ?)
			""", (item_id, constituent_id, date_lost, location_lost))

			conn.commit()

			add_activity_log(
					item_id=item_id,
					details=f"Item Registered: {name} [ID: {item_id}]", 
					actions="Created"
				)
			return True, item_id
		
		except sqlite3.Error as e:
			conn.rollback()
			msg = f"Failed to report lost item: {e}"
			print(msg)
			return False, msg

def report_found_item(name, description, category_id, priority_level, constituent_id, date_found, location_found, photo_filepath=None):
	# Validate date format YYYY-MM-DD
	try:
		datetime.datetime.strptime(date_found, "%Y-%m-%d")
	except Exception:
		msg = f"Invalid date_found format: '{date_found}'. Expected YYYY-MM-DD."
		print(msg)
		return False, msg

	with get_connection() as conn:
		cursor = conn.cursor()
		try:
			item_id = _insert_item_core(cursor, name, description, 'Found', category_id, priority_level, photo_filepath)

			cursor.execute("""
				INSERT INTO found (item_id, constituent_id, date_found, location_found)
				VALUES (?, ?, ?, ?)
			""", (item_id, constituent_id, date_found, location_found))

			conn.commit()

			add_activity_log(
					item_id=item_id, 
					details=f"Item Registered: {name} [ID: {item_id}]", 
					actions="Created"
			)
			return True, item_id
		except sqlite3.Error as e:
			conn.rollback()
			msg = f"Failed to report found item: {e}"
			print(msg)
			return False, msg

def create_claim_request(item_id, constituent_id, claim_date):
	"""Create a claim request with validation.

	Performs these checks before inserting:
	- item exists
	- item.status is 'Active'
	- no existing claim for the item

	Returns the `item_id` on success, or `None` on validation or DB failure.
	"""
	# Validate claim_date format YYYY-MM-DD before DB operations
	try:
		datetime.datetime.strptime(claim_date, "%Y-%m-%d")
	except Exception:
		msg = f"Invalid claim_date format: '{claim_date}'. Expected YYYY-MM-DD."
		print(msg)
		return False, msg

	with get_connection() as conn:
		cursor = conn.cursor()
		try:
			# Verify item exists and is claimable
			cursor.execute("SELECT type, status FROM items WHERE item_id = ?", (item_id,))
			row = cursor.fetchone()
			if not row:
				msg = f"Failed to create claim request: item {item_id} not found."
				print(msg)
				return False, msg
			# Only items with status 'Active' are claimable
			if row["status"] != "Active":
				msg = f"Failed to create claim request: item {item_id} not claimable (status={row['status']})."
				print(msg)
				return False, msg

			# Prevent duplicate claims (item_id is PK in claim)
			cursor.execute("SELECT claim_status FROM claim WHERE item_id = ?", (item_id,))
			if cursor.fetchone():
				msg = f"Failed to create claim request: claim already exists for item {item_id}."
				print(msg)
				return False, msg

			# Insert the claim
			cursor.execute("""
				INSERT INTO claim (item_id, constituent_id, claim_date, claim_status)
				VALUES (?, ?, ?, 'Pending')
			""", (item_id, constituent_id, claim_date))

			# Log the request
			action_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
			cursor.execute("""
				INSERT INTO activity_log (item_id, details, actions, action_date)
				VALUES (?, ?, ?, ?)
			""", (item_id, f"Constituent ID {constituent_id} requested a claim.", "Claim Requested", action_date))

			conn.commit()
			return True, item_id
		except sqlite3.IntegrityError as e:
			conn.rollback()
			msg = f"Failed to create claim request (integrity): {e}"
			print(msg)
			return False, msg
		except sqlite3.Error as e:
			conn.rollback()
			msg = f"Failed to create claim request: {e}"
			print(msg)
			return False, msg

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
        
		# Be explicit about the type; if caller passes an unexpected value,
		# attempt to detect the stored type from the items table first.
		if item_type not in ('Lost', 'Found'):
			cursor.execute("SELECT type FROM items WHERE item_id = ?", (item_id,))
			row_type = cursor.fetchone()
			item_type = row_type["type"] if row_type else item_type

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
	
def get_all_activity_logs():
    """Fetches full log histories providing both standard column names and mapped presenter keys."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                log_id,
                item_id,
                action_date, 
                action_date as timestamp, 
                actions, 
                actions as type, 
                details, 
                details as message 
            FROM activity_log 
            ORDER BY log_id DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

# =====================================================================
# 3. UPDATE OPERATIONS (Modifying Data)
# =====================================================================

def update_item_status(item_id, current_status):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            # 1. Validate requested status transitions
            allowed_statuses = ('Active', 'Claimed', 'Archived')
            if current_status not in allowed_statuses:
                msg = f"Status update failed: '{current_status}' is not a valid status."
                print(msg)
                return False, msg

            # 2. If setting to 'Claimed', ensure there is an approved claim for this item
            if current_status == 'Claimed':
                cursor.execute("SELECT 1 FROM claim WHERE item_id = ? AND claim_status = 'Approved'", (item_id,))
                if not cursor.fetchone():
                    msg = f"Status update failed: no approved claim exists for item {item_id}."
                    print(msg)
                    return False, msg

            # 3. Perform the update operation
            cursor.execute("UPDATE items SET status = ? WHERE item_id = ?", (current_status, item_id))
            
            # 4. Write to activity log (using our unified database helper column naming format)
            action_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("""
                INSERT INTO activity_log (item_id, details, actions, action_date)
                VALUES (?, ?, ?, ?)
            """, (item_id, f"Item ID {item_id} status updated to '{current_status}'", f"Status -> {current_status}", action_date))

            # 5. Commit everything together safely inside a single transaction save block
            conn.commit()
            
            msg = f"Item {item_id} successfully marked as {current_status}."
            print(msg)
            return True, msg

        except sqlite3.Error as e:
            conn.rollback()
            msg = f"Status update failed: {e}"
            print(msg)
            return False, msg
		
def resolve_claim_request(item_id, constituent_id, administrative_action):
	"""administrative_action should be 'Approved' or 'Rejected'"""
	if administrative_action not in ("Approved", "Rejected"):
		msg = f"Invalid administrative_action: {administrative_action}"
		print(msg)
		return False, msg

	with get_connection() as conn:
		cursor = conn.cursor()
		try:
			# Update claim status only for the matching claimant
			cursor.execute("""
				UPDATE claim SET claim_status = ? 
				WHERE item_id = ? AND constituent_id = ?
			""", (administrative_action, item_id, constituent_id))

			# Ensure a row was actually updated
			if cursor.rowcount == 0:
				conn.rollback()
				msg = f"Claim resolution failed: no matching claim for item {item_id} and constituent {constituent_id}."
				print(msg)
				return False, msg

			# Determine new item status based on the action
			new_item_status = 'Claimed' if administrative_action == 'Approved' else 'Active'
			cursor.execute("UPDATE items SET status = ? WHERE item_id = ?", (new_item_status, item_id))

			# Log the resolution
			action_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
			cursor.execute("""
				INSERT INTO activity_log (item_id, details, actions, action_date)
				VALUES (?, ?, ?, ?)
			""", (item_id, f"Claim by constituent {constituent_id} was {administrative_action}.", f"Claim {administrative_action}", action_date))

			conn.commit()
			return True, None
		except sqlite3.Error as e:
			conn.rollback()
			msg = f"Claim resolution failed: {e}"
			print(msg)
			return False, msg

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
        
		# Count Pending Claim Requests
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
def add_activity_log(item_id: int, details: str, actions: str) -> bool:
    """Helper function to cleanly insert tracking events into the activity log."""
    action_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO activity_log (item_id, details, actions, action_date)
                VALUES (?, ?, ?, ?)
            """, (item_id, details, actions, action_date))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database logging error: {e}")
            return False
		
