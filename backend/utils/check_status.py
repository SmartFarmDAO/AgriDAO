#!/usr/bin/env python3
"""
Quick diagnostic script to check backend status and user roles.
Usage: python check_status.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.database import engine
    from app.models import User, Farmer
    from sqlmodel import Session, select
    
    print("=" * 70)
    print("Backend Status Check")
    print("=" * 70)
    
    with Session(engine) as session:
        # Check admin user
        print("\n✓ Database connection successful")
        
        print("\n1. Admin User (riajurpbl@gmail.com):")
        admin = session.exec(
            select(User).where(User.email == 'riajurpbl@gmail.com')
        ).first()
        if admin:
            role = admin.role.value if hasattr(admin.role, 'value') else str(admin.role)
            print(f"   ✓ Found - Role: {role}")
        else:
            print("   ✗ NOT FOUND - Need to create admin user!")
        
        # Check buyer/farmer user
        print("\n2. User (riajurpbl+farmer001@gmail.com):")
        user = session.exec(
            select(User).where(User.email == 'riajurpbl+farmer001@gmail.com')
        ).first()
        if user:
            role = user.role.value if hasattr(user.role, 'value') else str(user.role)
            status = user.status.value if hasattr(user.status, 'value') else str(user.status)
            print(f"   ✓ Found")
            print(f"   - Role: {role}")
            print(f"   - Status: {status}")
            
            if role.upper() == "BUYER":
                print(f"   ⚠️  User is BUYER, needs to be changed to FARMER")
            elif role.upper() == "FARMER":
                print(f"   ✓ User is already FARMER")
        else:
            print("   ✗ NOT FOUND")
        
        # Check farmer profile
        print("\n3. Farmer Profile (riajurpbl+farmer001@gmail.com):")
        farmer = session.exec(
            select(Farmer).where(Farmer.email == 'riajurpbl+farmer001@gmail.com')
        ).first()
        if farmer:
            print(f"   ✓ Found - {farmer.name}")
            print(f"   - Location: {farmer.location or 'N/A'}")
            print(f"   - Phone: {farmer.phone or 'N/A'}")
        else:
            print("   ✗ NOT FOUND - User needs to complete farmer onboarding")
        
        # Summary
        print("\n4. Database Summary:")
        total_users = len(session.exec(select(User)).all())
        total_farmers = len(session.exec(select(Farmer)).all())
        print(f"   - Total users: {total_users}")
        print(f"   - Total farmer profiles: {total_farmers}")
    
    print("\n" + "=" * 70)
    print("Status Check Complete")
    print("=" * 70)
    
    # Recommendations
    print("\nRecommendations:")
    if not admin:
        print("  • Run: python create_admin.py")
    if user and role.upper() == "BUYER":
        print("  • Run: python update_user_role.py")
        print("  • Or use admin dashboard to change role")
    if not farmer and user:
        print("  • User should complete farmer onboarding at /onboarding")
    
    print()

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPossible issues:")
    print("  • Backend not running")
    print("  • Database not accessible")
    print("  • Database not initialized")
    print("\nTry:")
    print("  • docker-compose up -d")
    print("  • Check docker-compose logs backend")
    sys.exit(1)
