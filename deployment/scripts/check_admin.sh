#!/bin/bash

echo "==================================="
echo "AgriDAO Admin User Check"
echo "==================================="
echo ""

# Check all users
echo "All users in database:"
docker-compose exec db psql -U postgres -d agridb -c "SELECT id, email, name, role, status FROM \"user\" ORDER BY id;"

echo ""
echo "==================================="
echo "Admin users only:"
docker-compose exec db psql -U postgres -d agridb -c "SELECT id, email, name, role, status FROM \"user\" WHERE role = 'ADMIN' ORDER BY id;"

echo ""
echo "==================================="
echo "To create/update admin user, run:"
echo "  cd backend && python create_admin.py"
echo "==================================="
