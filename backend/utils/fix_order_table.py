#!/usr/bin/env python3
"""
Script to fix order table schema issues.
Usage: python fix_order_table.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine


def check_and_fix_order_table():
    """Check and fix order table schema."""
    print("=" * 70)
    print("Checking Order Table Schema")
    print("=" * 70)
    
    # Define all columns that should exist
    required_columns = {
        'shipping_fee': "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS shipping_fee DECIMAL(10,2) DEFAULT 0.00",
        'tax_amount': "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS tax_amount DECIMAL(10,2) DEFAULT 0.00",
        'shipping_address': "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS shipping_address JSON",
        'tracking_number': "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS tracking_number VARCHAR(100)",
        'notes': "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS notes VARCHAR(1000)",
        'stripe_checkout_session_id': "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS stripe_checkout_session_id VARCHAR(255)",
        'stripe_payment_intent_id': "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS stripe_payment_intent_id VARCHAR(255)",
        'estimated_delivery_date': "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS estimated_delivery_date TIMESTAMP",
        'delivered_at': "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP",
        'cancelled_at': "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMP",
        'cancellation_reason': "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS cancellation_reason VARCHAR(500)",
        'updated_at': "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    
    with engine.connect() as conn:
        # Get existing columns
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'order'
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
        
        # Check all order columns
        print("\nCurrent Order Table Columns:")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'order'
            ORDER BY ordinal_position
        """))
        
        for row in result:
            nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
            print(f"  - {row[0]:30s} {row[1]:20s} {nullable}")
    
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Order Table Schema Fix Script")
    print("=" * 70)
    
    if check_and_fix_order_table():
        print("\n✓ Order table schema is correct")
        print("\n" + "=" * 70)
        print("Database Fix Complete!")
        print("=" * 70)
    else:
        print("\n✗ Failed to fix order table")
        sys.exit(1)
