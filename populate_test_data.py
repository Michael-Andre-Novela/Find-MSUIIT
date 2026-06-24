
"""
Comprehensive test data population script.
Populates the database with 30+ items, constituents, and claims for testing.
"""

from models import queries, connection
import datetime

def populate_test_data():
    """Populate database with 30+ test items."""
    
    # Initialize DB
    print("Initializing database...")
    connection.initialize_db()
    print("✓ Database initialized\n")

    # ===== REGISTER CONSTITUENTS =====
    print("Registering 15 constituents...")
    constituents = []
    constituent_data = [
        ("2026-0001", "Alice Johnson", "alice.johnson@g.msuiit.edu.ph", "09171111111"),
        ("2026-0002", "Benjamin Cruz", "benjamin.cruz@g.msuiit.edu.ph", "09172222222"),
        ("2026-0003", "Carmen Reyes", "carmen.reyes@g.msuiit.edu.ph", "09173333333"),
        ("2026-0004", "Diego Santos", "diego.santos@g.msuiit.edu.ph", "09174444444"),
        ("2026-0005", "Eva Lim", "eva.lim@g.msuiit.edu.ph", "09175555555"),
        ("2026-0006", "Fernando Lopez", "fernando.lopez@g.msuiit.edu.ph", "09176666666"),
        ("2026-0007", "Grace Fernandez", "grace.fernandez@g.msuiit.edu.ph", "09177777777"),
        ("2026-0008", "Henry Aquino", "henry.aquino@g.msuiit.edu.ph", "09178888888"),
        ("2026-0009", "Isabella Tan", "isabella.tan@g.msuiit.edu.ph", "09179999999"),
        ("2026-0010", "James Rodriguez", "james.rodriguez@g.msuiit.edu.ph", "09170000000"),
        ("2026-0011", "Karen Gomez", "karen.gomez@g.msuiit.edu.ph", "09171010101"),
        ("2026-0012", "Luis Martinez", "luis.martinez@g.msuiit.edu.ph", "09172020202"),
        ("2026-0013", "Maria Gonzales", "maria.gonzales@g.msuiit.edu.ph", "09173030303"),
        ("2026-0014", "Nicolas Perez", "nicolas.perez@g.msuiit.edu.ph", "09174040404"),
        ("2026-0015", "Olivia Santos", "olivia.santos@g.msuiit.edu.ph", "09175050505"),
    ]

    for id_num, name, email, phone in constituent_data:
        c_id = queries.add_constituent(id_num, name, email, phone)
        constituents.append(c_id)
        print(f"  ✓ {name} ({id_num})")

    print(f"✓ {len(constituents)} constituents registered\n")

    # ===== TEST ITEMS DATA =====
    print("Registering 35 items (mix of Lost & Found)...")
    
    items_data = [
        # LOST ITEMS (18 items)
        ("Black Leather Wallet", "Brown leather with campus ID inside", "Lost", "High", 4, "2026-06-10", "Main Library, 2nd Floor"),
        ("Samsung Galaxy S22", "Silver color, cracked screen protector", "Lost", "Critical", 1, "2026-06-11", "Engineering Building, Lobby"),
        ("Student ID Card", "Clear sleeve, name: Maria Gonzales", "Lost", "High", 3, "2026-06-12", "Cafeteria"),
        ("Blue Umbrella", "Foldable with wooden handle", "Lost", "Low", 7, "2026-06-13", "Sports Complex"),
        ("Gold Necklace", "Cross pendant with pearls", "Lost", "High", 6, "2026-06-14", "Admin Building"),
        ("AirPods Pro", "White, left ear missing", "Lost", "Critical", 1, "2026-06-15", "Dormitory A"),
        ("Red Backpack", "Nike brand with laptop compartment", "Lost", "Medium", 4, "2026-06-16", "Library Parking"),
        ("Car Keys", "Blue keychain with house key", "Lost", "Critical", 3, "2026-06-17", "Canteen"),
        ("Eyeglasses", "Black frame, prescription lenses", "Lost", "High", 6, "2026-06-18", "Biology Lab"),
        ("Watch", "Casio digital, black band", "Lost", "Medium", 6, "2026-06-19", "Gymnasium"),
        ("Notebook", "Blue cover, all lecture notes inside", "Lost", "High", 5, "2026-06-20", "Classroom Building"),
        ("Headphones", "Beats Solo 3, black", "Lost", "Medium", 1, "2026-06-21", "Auditorium"),
        ("Jacket", "Brown leather, MSU-IIT logo", "Lost", "Low", 6, "2026-06-22", "Main Gate"),
        ("Phone Charger", "USB-C, 65W fast charger", "Lost", "Low", 1, "2026-06-23", "Computer Lab"),
        ("Wallet with Cash", "Containing 5000 pesos", "Lost", "Critical", 4, "2026-06-24", "Registrar Office"),
        ("Textbook", "Organic Chemistry, 3rd Edition", "Lost", "Medium", 5, "2026-06-25", "Science Building"),
        ("Laptop", "Dell XPS 15, silver", "Lost", "Critical", 1, "2026-06-26", "Library Study Area"),
        ("Shoes", "Nike Air Jordan, size 10", "Lost", "Low", 6, "2026-06-27", "Locker Room"),

        # FOUND ITEMS (17 items)
        ("Silver Pen", "Mont Blanc ballpoint pen", "Found", "Low", 3, "2026-06-10", "Library Entrance"),
        ("Coffee Mug", "White with university logo", "Found", "Low", 7, "2026-06-11", "Faculty Room"),
        ("Jacket", "Blue denim, no label", "Found", "Low", 6, "2026-06-12", "Lost & Found Office"),
        ("USB Flash Drive", "8GB Kingston, black", "Found", "High", 1, "2026-06-13", "Computer Lab Door"),
        ("Sunglasses", "Ray-Ban aviators", "Found", "Medium", 6, "2026-06-14", "Outdoor Benches"),
        ("Handkerchief", "Embroidered, pink", "Found", "Low", 6, "2026-06-15", "Cafeteria Table"),
        ("Earbuds", "Apple brand, white", "Found", "Medium", 1, "2026-06-16", "Hallway"),
        ("Water Bottle", "Hydro Flask, blue", "Found", "Low", 7, "2026-06-17", "Sports Field"),
        ("Notebook", "Small journal, leather cover", "Found", "Medium", 5, "2026-06-18", "Bench near Library"),
        ("Keys", "Bundle of 6 keys with keychain", "Found", "High", 3, "2026-06-19", "Admin Parking"),
        ("Phone Case", "iPhone 14 Pro case, black", "Found", "Low", 1, "2026-06-20", "Stairwell"),
        ("Bag", "Black messenger bag", "Found", "High", 4, "2026-06-21", "Main Entrance"),
        ("Scarf", "Red and white plaid", "Found", "Low", 6, "2026-06-22", "Classroom"),
        ("Charger", "Lightning cable, white", "Found", "Low", 1, "2026-06-23", "Charging Station"),
        ("Belt", "Brown leather with silver buckle", "Found", "Low", 6, "2026-06-24", "Rest Area"),
        ("Book", "Programming in Python", "Found", "Medium", 5, "2026-06-25", "Reading Area"),
        ("Badge Holder", "Campus ID holder with lanyard", "Found", "Medium", 3, "2026-06-26", "Reception Area"),
    ]

    lost_count = 0
    found_count = 0
    claims_filed = 0

    for name, desc, item_type, priority, category_id, date, location in items_data:
        reporter_idx = hash((name + date)) % len(constituents)
        reporter_id = constituents[reporter_idx]

        if item_type == "Lost":
            success, item_id = queries.report_lost_item(
                name=name,
                description=desc,
                category_id=category_id,
                priority_level=priority,
                constituent_id=reporter_id,
                date_lost=date,
                location_lost=location,
                photo_filepath=None 
            )
            if success:
                lost_count += 1
                print(f"  ✓ LOST: {name} (ID: {item_id})")

                # 50% chance of filing a claim on lost items
                if hash(name) % 2 == 0 and claims_filed < 8:
                    claimant_idx = (reporter_idx + 1 + claims_filed) % len(constituents)
                    claimant_id = constituents[claimant_idx]
                    claim_date = (
                        datetime.datetime.strptime(date, "%Y-%m-%d") +
                        datetime.timedelta(days=1)
                    ).strftime("%Y-%m-%d")
                    
                    c_success, c_msg = queries.create_claim_request(
                        item_id=item_id,
                        constituent_id=claimant_id,
                        claim_date=claim_date
                    )
                    if c_success:
                        claims_filed += 1
                        print(f"      → Claim filed by constituent {claimant_id}")

        else:  # Found
            success, item_id = queries.report_found_item(
                name=name,
                description=desc,
                category_id=category_id,
                priority_level=priority,
                constituent_id=reporter_id,
                date_found=date,
                location_found=location,
                photo_filepath=None 
            )
            if success:
                found_count += 1
                print(f"  ✓ FOUND: {name} (ID: {item_id})")

                # 40% chance of filing a claim on found items
                if hash(name) % 3 == 0 and claims_filed < 12:
                    claimant_idx = (reporter_idx + 2 + claims_filed) % len(constituents)
                    claimant_id = constituents[claimant_idx]
                    claim_date = (
                        datetime.datetime.strptime(date, "%Y-%m-%d") +
                        datetime.timedelta(days=2)
                    ).strftime("%Y-%m-%d")
                    
                    c_success, c_msg = queries.create_claim_request(
                        item_id=item_id,
                        constituent_id=claimant_id,
                        claim_date=claim_date
                    )
                    if c_success:
                        claims_filed += 1
                        print(f"      → Claim filed by constituent {claimant_id}")

    print(f"\n✓ {lost_count} lost items registered")
    print(f"✓ {found_count} found items registered")
    print(f"✓ {claims_filed} claims filed\n")

    # ===== SUMMARY =====
    print("=" * 60)
    print("DATABASE POPULATION COMPLETE")
    print("=" * 60)
    print(f"Total Constituents: {len(constituents)}")
    print(f"Total Items: {lost_count + found_count}")
    print(f"  - Lost Items: {lost_count}")
    print(f"  - Found Items: {found_count}")
    print(f"Total Claims: {claims_filed}")
    print("=" * 60)
    print("\nYou can now launch the app: python main.py")


if __name__ == "__main__":
    try:
        populate_test_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()