import os
from sqlalchemy import create_engine, inspect, text

# Use direct connection string or env
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

inspector = inspect(engine)
columns = inspector.get_columns('order') # 'order' is the table name (lowercase in postgres usually, unless quoted)

print("Columns in 'order' table:")
for col in columns:
    print(f"- {col['name']} ({col['type']})")

# Check migration version
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM alembic_version"))
    print("\nCurrent Alembic Version:")
    for row in result:
        print(row)
