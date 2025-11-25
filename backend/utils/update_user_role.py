#!/usr/bin/env python3
"""
Script to update a user's role and check their farmer profile.
Usage: python update_user_role.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine
from app.models import User, UserRole, Farmer
from sqlmodel import Session, select


def check_user_and_farmer(email: str):
    """Check user and farmer profile for given email."""
    with Session(engine) as session:
        # Find user
        user = session.exec(
            select(User).where(User.email == email)
        ).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return None, None
        
        print(f"\n✓ User found:")
        print(f"  ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.name}")
        print(f"  Role: {user.role}")
        print(f"  Status: {user.status}")
        
        # Find farmer profile
        farmer = session.exec(
            select(Farmer).where(Farmer.email == email)
        ).first()
        
        if farmer:
            print(f"\n✓ Farmer profile found:")
            print(f"  ID: {farmer.id}")
            print(f"  Name: {farmer.name}")
            print(f"  Phone: {farmer.phone}")
            print(f"  Location: {farmer.location}")
        else:
            print(f"\n❌ No farmer profile found for {email}")
        
        return user, farmer


def update_user_to_farmer(email: str):
    """Update user role to FARMER."""
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == email)
        ).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return False
        
        old_role = user.role
        user.role = UserRole.FARMER
        session.add(user)
        session.commit()
        session.refresh(user)
        
        print(f"\n✓ Updated user role:")
        print(f"  Email: {user.email}")
        print(f"  Old role: {old_role}")
        print(f"  New role: {user.role}")
        
        return True


def list_all_farmers():
    """List all farmer profiles."""
    with Session(engine) as session:
        farmers = session.exec(select(Farmer)).all()
        
        if not farmers:
            print("\nNo farmer profiles found")
            return
        
        print(f"\nTotal farmer profiles: {len(farmers)}")
        print("\nID | Email | Name | Phone | Location")
        print("-" * 80)
        
        for farmer in farmers:
            email = farmer.email or "N/A"
            name = farmer.name or "N/A"
            phone = farmer.phone or "N/A"
            location = farmer.location or "N/A"
            print(f"{farmer.id:3d} | {email:30s} | {name:20s} | {phone:15s} | {location}")


if __name__ == "__main__":
    print("=" * 80)
    print("User Role Update Script")
    print("=" * 80)
    
    # Check specific user
    email = "riajurpbl+farmer001@gmail.com"
    print(f"\nChecking user: {email}")
    user, farmer = check_user_and_farmer(email)
    
    if user:
        current_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        if current_role.upper() != "FARMER":
            print(f"\n⚠️  User role is {current_role}, not FARMER")
            update = input("\nDo you want to update this user to FARMER role? (y/n): ").strip().lower()
            
            if update == 'y':
                if update_user_to_farmer(email):
                    print("\n✓ User role updated successfully!")
                    print("\n⚠️  User needs to logout and login again to see the change")
                else:
                    print("\n❌ Failed to update user role")
            else:
                print("\nNo changes made")
        else:
            print(f"\n✓ User already has FARMER role")
        
        if not farmer:
            print("\n⚠️  User has no farmer profile!")
            print("   The user needs to complete the farmer onboarding form at /onboarding")
    
    # List all farmers
    print("\n" + "=" * 80)
    print("All Farmer Profiles:")
    list_all_farmers()
    
    print("\n" + "=" * 80)
    print("Done!")
    print("\nNext steps:")
    print("1. If role was updated, user must logout and login again")
    print("2. If no farmer profile exists, user should complete /onboarding form")
    print("3. Check that user can access farmer features in dashboard")
