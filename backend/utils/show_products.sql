-- Show all products
SELECT id, name, category, price, quantity, farmer_id, created_at 
FROM product 
ORDER BY created_at DESC;

-- Count total products
SELECT COUNT(*) as total_products FROM product;

-- Products by category
SELECT category, COUNT(*) as count 
FROM product 
WHERE category IS NOT NULL 
GROUP BY category 
ORDER BY count DESC;

-- Show product with farmer info
SELECT p.id, p.name, p.category, p.price, p.quantity, f.name as farmer_name, f.email as farmer_email
FROM product p
LEFT JOIN farmer f ON p.farmer_id = f.id
ORDER BY p.created_at DESC;
