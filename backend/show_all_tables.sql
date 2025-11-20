-- List all tables
\dt

-- Show all users
SELECT id, email, name, role, email_verified, status FROM "user";

-- Show all farmers
SELECT id, name, email, location FROM farmer;

-- Show all products
SELECT COUNT(*) as total_products FROM product;

-- Show all orders
SELECT COUNT(*) as total_orders FROM "order";

-- Show all funding requests
SELECT COUNT(*) as total_funding_requests FROM fundingrequest;

-- Show all proposals
SELECT COUNT(*) as total_proposals FROM proposal;
