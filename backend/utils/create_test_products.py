#!/usr/bin/env python3
"""
Create test products for marketplace testing
"""
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine
from app.models import Product, ProductStatus

def create_test_products():
    """Create sample products for testing"""
    print("=" * 70)
    print("Creating Test Products")
    print("=" * 70)
    
    with engine.connect() as conn:
        # Check if we have farmers
        result = conn.execute(text("SELECT id, name, email FROM farmer LIMIT 5"))
        farmers = result.fetchall()
        
        if not farmers:
            print("\n✗ No farmers found in database")
            print("  Please create a farmer first through the onboarding process")
            return False
        
        print(f"\nFound {len(farmers)} farmer(s):")
        for farmer in farmers:
            print(f"  - ID: {farmer[0]}, Name: {farmer[1]}, Email: {farmer[2]}")
        
        # Use first farmer
        farmer_id = farmers[0][0]
        print(f"\nUsing Farmer ID: {farmer_id}")
        
        # Sample products
        test_products = [
            {
                "name": "Fresh Organic Tomatoes",
                "description": "Locally grown organic tomatoes, perfect for salads and cooking. Harvested fresh daily.",
                "category": "Vegetables",
                "price": Decimal("120.00"),
                "quantity": "5 kg",
                "quantity_available": 50,
                "unit": "kg",
                "farmer_id": farmer_id,
                "status": "active",
                "min_order_quantity": 1,
                "tags": '["organic", "fresh", "local"]'
            },
            {
                "name": "Premium Basmati Rice",
                "description": "High-quality aged basmati rice with excellent aroma and taste. Perfect for biryani.",
                "category": "Grains",
                "price": Decimal("85.00"),
                "quantity": "1 kg",
                "quantity_available": 100,
                "unit": "kg",
                "farmer_id": farmer_id,
                "status": "active",
                "min_order_quantity": 1,
                "tags": '["premium", "aged", "aromatic"]'
            },
            {
                "name": "Farm Fresh Eggs",
                "description": "Free-range chicken eggs from healthy hens. Rich in nutrients and taste.",
                "category": "Dairy & Eggs",
                "price": Decimal("180.00"),
                "quantity": "12 pieces",
                "quantity_available": 30,
                "unit": "dozen",
                "farmer_id": farmer_id,
                "status": "active",
                "min_order_quantity": 1,
                "tags": '["free-range", "fresh", "organic"]'
            },
            {
                "name": "Sweet Mangoes",
                "description": "Juicy and sweet mangoes from our orchard. Perfect for eating fresh or making juice.",
                "category": "Fruits",
                "price": Decimal("150.00"),
                "quantity": "1 kg",
                "quantity_available": 40,
                "unit": "kg",
                "farmer_id": farmer_id,
                "status": "active",
                "min_order_quantity": 1,
                "tags": '["sweet", "fresh", "seasonal"]'
            },
            {
                "name": "Fresh Spinach",
                "description": "Organic spinach leaves, rich in iron and vitamins. Great for cooking or salads.",
                "category": "Vegetables",
                "price": Decimal("60.00"),
                "quantity": "500 g",
                "quantity_available": 25,
                "unit": "g",
                "farmer_id": farmer_id,
                "status": "active",
                "min_order_quantity": 1,
                "tags": '["organic", "leafy", "healthy"]'
            }
        ]
        
        print(f"\nCreating {len(test_products)} test products...")
        
        for i, product in enumerate(test_products, 1):
            try:
                # Check if product already exists
                check = conn.execute(text(f"""
                    SELECT id FROM product 
                    WHERE name = '{product['name']}' AND farmer_id = {farmer_id}
                """))
                
                if check.fetchone():
                    print(f"  {i}. ✓ '{product['name']}' already exists")
                    continue
                
                # Insert product
                conn.execute(text(f"""
                    INSERT INTO product (
                        name, description, category, price, quantity, 
                        quantity_available, unit, farmer_id, status, 
                        min_order_quantity, tags, created_at, updated_at
                    ) VALUES (
                        '{product['name']}',
                        '{product['description']}',
                        '{product['category']}',
                        {product['price']},
                        '{product['quantity']}',
                        {product['quantity_available']},
                        '{product['unit']}',
                        {product['farmer_id']},
                        '{product['status']}',
                        {product['min_order_quantity']},
                        '{product['tags']}'::json,
                        NOW(),
                        NOW()
                    )
                """))
                conn.commit()
                print(f"  {i}. ✓ Created '{product['name']}'")
                
            except Exception as e:
                print(f"  {i}. ✗ Failed to create '{product['name']}': {e}")
                return False
        
        # Verify products
        result = conn.execute(text("SELECT COUNT(*) FROM product"))
        count = result.fetchone()[0]
        
        print(f"\n✓ Total products in database: {count}")
        
        # Show sample products
        print("\nSample products:")
        result = conn.execute(text("""
            SELECT id, name, price, quantity_available, status 
            FROM product 
            LIMIT 5
        """))
        
        for row in result:
            print(f"  - ID: {row[0]}, Name: {row[1]}, Price: ৳{row[2]}, Qty: {row[3]}, Status: {row[4]}")
    
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Test Products Creation Script")
    print("=" * 70)
    
    if create_test_products():
        print("\n" + "=" * 70)
        print("Test Products Created Successfully!")
        print("=" * 70)
        print("\nYou can now:")
        print("1. Visit http://localhost:5173/marketplace")
        print("2. Browse the test products")
        print("3. Test add to cart and checkout features")
        print()
    else:
        print("\n✗ Failed to create test products")
        sys.exit(1)
