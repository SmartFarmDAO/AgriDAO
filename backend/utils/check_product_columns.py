#!/usr/bin/env python3
"""Check product table columns"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'product' 
        ORDER BY ordinal_position
    """))
    
    print("Product table columns:")
    print("-" * 70)
    for row in result:
        nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
        print(f"{row[0]:30s} {row[1]:20s} {nullable}")
