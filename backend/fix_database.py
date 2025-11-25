#!/usr/bin/env python3
"""
Script to fix database schema issues.
Usage: python fix_database.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine


def check_and_fix_product_table():
    """Check and fix product table schema."""
    print("=" * 70)
    print("Checking Product Table Schema")
    print("=" * 70)
    
    # Define all columns that should exist
    required_columns = {
        'quantity_available': "ALTER TABLE product ADD COLUMN IF NOT EXISTS quantity_available INTEGER DEFAULT 0",
        'status': "ALTER TABLE product ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active'",
        'unit': "ALTER TABLE product ADD COLUMN IF NOT EXISTS unit VARCHAR(50) DEFAULT 'piece'",
        'images': "ALTER TABLE product ADD COLUMN IF NOT EXISTS images JSON",
        'product_metadata': "ALTER TABLE product ADD COLUMN IF NOT EXISTS product_metadata JSON",
        'sku': "ALTER TABLE product ADD COLUMN IF NOT EXISTS sku VARCHAR(100) UNIQUE",
        'weight': "ALTER TABLE product ADD COLUMN IF NOT EXISTS weight DECIMAL(8,2)",
        'dimensions': "ALTER TABLE product ADD COLUMN IF NOT EXISTS dimensions JSON",
        'tags': "ALTER TABLE product ADD COLUMN IF NOT EXISTS tags JSON",
        'min_order_quantity': "ALTER TABLE product ADD COLUMN IF NOT EXISTS min_order_quantity INTEGER DEFAULT 1",
        'max_order_quantity': "ALTER TABLE product ADD COLUMN IF NOT EXISTS max_order_quantity INTEGER",
        'harvest_date': "ALTER TABLE product ADD COLUMN IF NOT EXISTS harvest_date TIMESTAMP",
        'expiry_date': "ALTER TABLE product ADD COLUMN IF NOT EXISTS expiry_date TIMESTAMP",
        'updated_at': "ALTER TABLE product ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    
    with engine.connect() as conn:
        # Get existing columns
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'product'
        """))
        existing_columns = {row[0] for row in result}
        
        # Check and add missing columns
        missing_columns = []
        for col_name, alter_sql in required_columns.items():
            if col_name not in existing_columns:
                missing_columns.append(col_name)
                print(f"\n✗ Column '{col_name}' is MISSING")
                print(f"  Adding column...")
                
                try:
                    conn.execute(text(alter_sql))
                    conn.commit()
                    print(f"  ✓ Column '{col_name}' added successfully")
                except Exception as e:
                    print(f"  ✗ Error adding column '{col_name}': {e}")
                    return False
            else:
                print(f"✓ Column '{col_name}' exists")
        
        if not missing_columns:
            print("\n✓ All required columns exist")
        
        # Check all product columns
        print("\nCurrent Product Table Columns:")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'product'
            ORDER BY ordinal_position
        """))
        
        for row in result:
            nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
            print(f"  - {row[0]:30s} {row[1]:20s} {nullable}")
    
    return True


def check_foreign_keys():
    """Check foreign key constraints."""
    print("\n" + "=" * 70)
    print("Checking Foreign Key Constraints")
    print("=" * 70)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                tc.table_name, 
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name IN ('usersession', 'cart', 'notification', 'order', 'orderreview')
            ORDER BY tc.table_name
        """))
        
        print("\nForeign Keys Referencing 'user' table:")
        for row in result:
            if row[2] == 'user':
                print(f"  {row[0]}.{row[1]} → {row[2]}.{row[3]}")


def test_product_query():
    """Test if product query works."""
    print("\n" + "=" * 70)
    print("Testing Product Query")
    print("=" * 70)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM product"))
            count = result.fetchone()[0]
            print(f"\n✓ Product query successful")
            print(f"  Total products: {count}")
            
            # Test full query
            result = conn.execute(text("""
                SELECT id, name, price, quantity_available, status 
                FROM product 
                LIMIT 5
            """))
            
            print("\nSample Products:")
            for row in result:
                print(f"  ID: {row[0]}, Name: {row[1]}, Qty: {row[3]}, Status: {row[4]}")
            
            return True
    except Exception as e:
        print(f"\n✗ Product query failed: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Database Schema Fix Script")
    print("=" * 70)
    
    # Fix product table
    if check_and_fix_product_table():
        print("\n✓ Product table schema is correct")
    else:
        print("\n✗ Failed to fix product table")
        sys.exit(1)
    
    # Check foreign keys
    check_foreign_keys()
    
    # Test product query
    if test_product_query():
        print("\n✓ All checks passed")
    else:
        print("\n✗ Some checks failed")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("Database Fix Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Restart backend: docker-compose restart backend")
    print("2. Test product listing in admin dashboard")
    print("3. Test user deletion")
    print()
