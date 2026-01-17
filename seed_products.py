import os
import random
from sqlalchemy import create_engine
from sqlmodel import Session, select
from app.models import Product, Farmer, User, UserRole

# Connect to DB
# Standard Docker internal URL if running inside container, or override via env
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not set")
    exit(1)

engine = create_engine(db_url)

def seed_products():
    with Session(engine) as session:
        # 1. Find or create a Farmer user/profile to associate products with
        # Try to find an existing farmer
        farmer_user = session.exec(select(User).where(User.role == UserRole.FARMER)).first()
        
        if not farmer_user:
            print("No farmer user found. Creating one...")
            farmer_user = User(
                name="Demo Farmer",
                email="farmer@demo.com",
                role=UserRole.FARMER,
                status="active"
            )
            session.add(farmer_user)
            session.commit()
            session.refresh(farmer_user)

        # Ensure Farmer profile exists
        farmer_profile = session.exec(select(Farmer).where(Farmer.id == farmer_user.id)).first() # Assuming 1:1 match on ID or similar logic
        # Ideally, look up farmer profile by email or user relationship. 
        # For simplicity in this seed script, if no farmer table entry exists for this user, create one.
        # Note: Your schema might link Farmer to User differently. 
        # Let's check the model: Product has farmer_id. Farmer has id. 
        # It's likely loose coupling or shared ID. Let's create a Farmer record.
        
        if not farmer_profile:
             # create independent farmer record if not linked by FK in schema constraints
             farmer_profile = Farmer(
                 name=farmer_user.name,
                 email=farmer_user.email,
                 location="Bogra, Bangladesh"
             )
             session.add(farmer_profile)
             session.commit()
             session.refresh(farmer_profile)

        print(f"Seeding products for Farmer ID: {farmer_profile.id}")

        products_data = [
            {
                "name": "Organic Potatoes",
                "description": "Freshly harvested organic potatoes from Bogra. Excellent for mashing or frying.",
                "category": "Vegetables",
                "price": 25.00,
                "quantity_available": 500,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Premium Rice (Miniket)",
                "description": "High quality Miniket rice, polished and sorted. Perfect for everyday meals.",
                "category": "Grains",
                "price": 65.00,
                "quantity_available": 1000,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Fresh Mangoes (Himsagar)",
                "description": "Sweet and juicy Himsagar mangoes directly from Rajshahi orchards.",
                "category": "Fruits",
                "price": 120.00,
                "quantity_available": 200,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1553279768-865429fa0078?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Red Lentils (Deshi Masoor)",
                "description": "Authentic Deshi Masoor Dal, rich in protein and flavor.",
                "category": "Grains",
                "price": 110.00,
                "quantity_available": 150,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1515543904379-3d757afe726e?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Green Chilies",
                "description": "Spicy fresh green chilies to add heat to your curries.",
                "category": "Vegetables",
                "price": 80.00,
                "quantity_available": 50,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1563861034-78af94d47d63?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Farm Fresh Eggs",
                "description": "Organic free-range eggs, rich in nutrients.",
                "category": "Dairy & Eggs",
                "price": 140.00,
                "quantity_available": 100,
                "unit": "dozen",
                "image": "https://images.unsplash.com/photo-1582722878654-02fd235dd3de?auto=format&fit=crop&q=80&w=800"
            }
        ]

        count = 0
        for p_data in products_data:
            # Check if exists
            existing = session.exec(select(Product).where(Product.name == p_data["name"])).first()
            if not existing:
                new_product = Product(
                    name=p_data["name"],
                    description=p_data["description"],
                    category=p_data["category"],
                    price=p_data["price"],
                    quantity_available=p_data["quantity_available"],
                    unit=p_data["unit"],
                    farmer_id=farmer_profile.id,
                    images=[p_data["image"]], # List of strings
                    min_order_quantity=1
                )
                session.add(new_product)
                count += 1
        
        session.commit()
        print(f"Successfully added {count} new products.")

if __name__ == "__main__":
    seed_products()
