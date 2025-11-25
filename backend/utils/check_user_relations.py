#!/usr/bin/env python3
"""Check user relations in database"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine

def check_table_exists(conn, table_name):
    """Check if a table exists"""
    result = conn.execute(text(f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = '{table_name}'
        )
    """))
    return result.fetchone()[0]

with engine.connect() as conn:
    # Get all users
    users = conn.execute(text('SELECT id, name, email, role FROM "user"')).fetchall()
    
    print('\n' + '=' * 80)
    print('USER RELATIONS CHECK')
    print('=' * 80)
    
    for user in users:
        user_id, name, email, role = user
        print(f'\nUser ID {user_id}: {name} ({email}) - {role}')
        print('-' * 80)
        
        # Check orders
        if check_table_exists(conn, 'order'):
            order_count = conn.execute(text(f'SELECT COUNT(*) FROM "order" WHERE buyer_id = {user_id}')).fetchone()[0]
            print(f'  Orders: {order_count}')
        
        # Check sessions
        if check_table_exists(conn, 'usersession'):
            session_count = conn.execute(text(f'SELECT COUNT(*) FROM usersession WHERE user_id = {user_id}')).fetchone()[0]
            print(f'  Sessions: {session_count}')
        
        # Check carts
        if check_table_exists(conn, 'cart'):
            cart_count = conn.execute(text(f'SELECT COUNT(*) FROM cart WHERE user_id = {user_id}')).fetchone()[0]
            print(f'  Carts: {cart_count}')
        
        # Check notifications
        if check_table_exists(conn, 'notification'):
            notif_count = conn.execute(text(f'SELECT COUNT(*) FROM notification WHERE user_id = {user_id}')).fetchone()[0]
            print(f'  Notifications: {notif_count}')
        
        # Check if farmer
        if role == 'FARMER':
            if check_table_exists(conn, 'farmer'):
                farmer = conn.execute(text(f'SELECT id FROM farmer WHERE email = \'{email}\'')).fetchone()
                if farmer:
                    farmer_id = farmer[0]
                    print(f'  Farmer ID: {farmer_id}')
                    
                    # Check products
                    if check_table_exists(conn, 'product'):
                        product_count = conn.execute(text(f'SELECT COUNT(*) FROM product WHERE farmer_id = {farmer_id}')).fetchone()[0]
                        print(f'  Products: {product_count}')
    
    print('\n' + '=' * 80)
