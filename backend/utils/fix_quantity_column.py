#!/usr/bin/env python3
"""Fix the quantity column to be nullable"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine

print("=" * 70)
print("Fixing Product Quantity Column")
print("=" * 70)

with engine.connect() as conn:
    # Make quantity column nullable
    print("\nMaking 'quantity' column nullable...")
    conn.execute(text("""
        ALTER TABLE product 
        ALTER COLUMN quantity DROP NOT NULL
    """))
    conn.commit()
    print("✓ Column is now nullable")
    
    # Set default value for existing NULL values
    print("\nSetting default value for NULL quantity values...")
    conn.execute(text("""
        UPDATE product 
        SET quantity = '1 piece' 
        WHERE quantity IS NULL
    """))
    conn.commit()
    print("✓ Default values set")
    
    # Verify
    result = conn.execute(text("""
        SELECT column_name, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'product' AND column_name = 'quantity'
    """))
    
    row = result.fetchone()
    print(f"\nVerification: quantity column is_nullable = {row[1]}")
    
print("\n" + "=" * 70)
print("Fix Complete!")
print("=" * 70)
