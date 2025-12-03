#!/usr/bin/env python3
"""Fix product status values to uppercase"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    # Update lowercase status values to uppercase
    result = conn.execute(text("""
        UPDATE product 
        SET status = UPPER(status) 
        WHERE status IN ('active', 'inactive', 'out_of_stock', 'draft')
    """))
    conn.commit()
    
    print(f"Updated {result.rowcount} product status values to uppercase")
    
    # Show current statuses
    result = conn.execute(text("SELECT DISTINCT status FROM product"))
    print("\nCurrent status values:")
    for row in result:
        print(f"  - {row[0]}")
