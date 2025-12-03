import os
import sys
from sqlmodel import Session, select, func

# Ensure 'app' package is importable when running this script directly
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.database import engine, init_db
from app.models import Product, User


def run():
    init_db()
    with Session(engine) as session:
        # Create a buyer user if not exists
        buyer = session.exec(select(User).where(User.role == 'buyer')).first()
        if not buyer:
            buyer = User(role='buyer', name='Test Buyer', email='buyer@example.com')
            session.add(buyer)
            session.commit()
            session.refresh(buyer)

        # Seed products if none
        existing_product = session.exec(select(Product)).first()
        if not existing_product:
            products = [
                Product(name='Organic Tomatoes', description='Fresh and organic', category='Vegetables', price=4.5, quantity='500 kg'),
                Product(name='Premium Rice', description='Aromatic jasmine', category='Grains', price=2.2, quantity='2000 kg'),
                Product(name='Free-Range Eggs', description='Dozen pack', category='Dairy & Eggs', price=0.8, quantity='100 dozen'),
            ]
            for p in products:
                session.add(p)
            session.commit()


if __name__ == '__main__':
    run()


