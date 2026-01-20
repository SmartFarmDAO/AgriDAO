#!/usr/bin/env python3
"""
Script to create an admin user in the database.
Usage: python create_admin.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine
from app.models import User, UserRole, UserStatus
from sqlmodel import Session, select


def create_admin_user(email: str, name: str):
    """Create an admin user with the given email and name."""
    with Session(engine) as session:
        # Check if user already exists
        existing_user = session.exec(
            select(User).where(User.email == email)
        ).first()
        
        if existing_user:
            print(f"User with email {email} already exists (ID: {existing_user.id})")
            print(f"Current role: {existing_user.role}")
            
            # Update to admin if not already
            if existing_user.role != UserRole.ADMIN:
                existing_user.role = UserRole.ADMIN
                existing_user.status = UserStatus.ACTIVE
                session.add(existing_user)
                session.commit()
                print(f"✓ Updated user {email} to ADMIN role")
            else:
                print(f"✓ User {email} is already an ADMIN")
            
            return existing_user
        
        # Create new admin user
        admin = User(
            name=name,
            email=email,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            email_verified=True
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)
        
        print(f"✓ Created new admin user:")
        print(f"  ID: {admin.id}")
        print(f"  Email: {admin.email}")
        print(f"  Name: {admin.name}")
        print(f"  Role: {admin.role}")
        
        return admin


def list_all_users():
    """List all users in the database."""
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        
        if not users:
            print("No users found in database")
            return
        
        print(f"\nTotal users: {len(users)}")
        print("\nID | Email | Name | Role | Status")
        print("-" * 70)
        
        for user in users:
            role = user.role.value if hasattr(user.role, 'value') else str(user.role)
            status = user.status.value if hasattr(user.status, 'value') else str(user.status)
            print(f"{user.id:3d} | {user.email:30s} | {user.name:20s} | {role:10s} | {status}")


if __name__ == "__main__":
    print("=" * 70)
    print("Admin User Management Script")
    print("=" * 70)
    
    # List existing users
    print("\nCurrent users in database:")
    list_all_users()
    
    # Prompt for admin creation
    print("\n" + "=" * 70)
    create = input("\nDo you want to create/update an admin user? (y/n): ").strip().lower()
    
    if create == 'y':
        email = input("Enter admin email: ").strip()
        name = input("Enter admin name: ").strip()
        
        if email and name:
            print()
            create_admin_user(email, name)
            print("\n" + "=" * 70)
            print("Updated user list:")
            list_all_users()
        else:
            print("Error: Email and name are required")
    else:
        print("No changes made")
    
    print("\n" + "=" * 70)
    print("Done!")
