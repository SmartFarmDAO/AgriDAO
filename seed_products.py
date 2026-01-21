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
            },
            {
                "name": "Fresh Tomatoes",
                "description": "Vine-ripened tomatoes, perfect for salads and cooking.",
                "category": "Vegetables",
                "price": 35.00,
                "quantity_available": 300,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Golden Bananas",
                "description": "Sweet and ripe bananas from Chittagong hill tracts.",
                "category": "Fruits",
                "price": 45.00,
                "quantity_available": 400,
                "unit": "dozen",
                "image": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Organic Spinach",
                "description": "Fresh green spinach leaves, rich in iron and vitamins.",
                "category": "Vegetables",
                "price": 30.00,
                "quantity_available": 120,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Basmati Rice",
                "description": "Premium aged Basmati rice with authentic aroma and long grains.",
                "category": "Grains",
                "price": 95.00,
                "quantity_available": 800,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Fresh Carrots",
                "description": "Crunchy orange carrots, great for juicing or cooking.",
                "category": "Vegetables",
                "price": 40.00,
                "quantity_available": 250,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Coconuts",
                "description": "Fresh coconuts from coastal regions, perfect for cooking oil and milk.",
                "category": "Fruits",
                "price": 35.00,
                "quantity_available": 500,
                "unit": "piece",
                "image": "https://images.unsplash.com/photo-1589606663923-283bbd309229?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Yellow Mustard Seeds",
                "description": "High quality mustard seeds for oil extraction and cooking.",
                "category": "Grains",
                "price": 85.00,
                "quantity_available": 180,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1599909533730-f9d49c0c9b4f?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Fresh Cauliflower",
                "description": "White and firm cauliflower heads, perfect for curries.",
                "category": "Vegetables",
                "price": 50.00,
                "quantity_available": 150,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1568584711271-e0e4e8d7e8e1?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Guavas",
                "description": "Sweet and aromatic guavas, rich in vitamin C.",
                "category": "Fruits",
                "price": 60.00,
                "quantity_available": 180,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1536511132770-e5058c7e8c46?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Chickpeas (Kabuli Chana)",
                "description": "Premium quality chickpeas, perfect for curries and salads.",
                "category": "Grains",
                "price": 130.00,
                "quantity_available": 200,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Fresh Milk",
                "description": "Pure cow's milk from local dairy farms, pasteurized and fresh.",
                "category": "Dairy & Eggs",
                "price": 75.00,
                "quantity_available": 300,
                "unit": "liter",
                "image": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Pumpkins",
                "description": "Large orange pumpkins, great for curries and desserts.",
                "category": "Vegetables",
                "price": 28.00,
                "quantity_available": 220,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1569976710208-b52636b52c1b?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Papayas",
                "description": "Ripe and sweet papayas, excellent for digestion.",
                "category": "Fruits",
                "price": 55.00,
                "quantity_available": 160,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1517282009859-f000ec3b26fe?auto=format&fit=crop&q=80&w=800"
            },
            {
                "name": "Ginger Root",
                "description": "Fresh ginger roots with strong aroma, perfect for tea and cooking.",
                "category": "Vegetables",
                "price": 150.00,
                "quantity_available": 80,
                "unit": "kg",
                "image": "https://images.unsplash.com/photo-1599909533730-f9d49c0c9b4f?auto=format&fit=crop&q=80&w=800"
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
