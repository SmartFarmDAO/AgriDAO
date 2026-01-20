"""
Database views and materialized views for analytics performance optimization.
"""

from sqlalchemy import text
from sqlmodel import Session
from ..database import engine


class DatabaseViews:
    """Manages database views for analytics optimization."""
    
    @staticmethod
    def create_analytics_views():
        """Create database views for analytics performance."""
        
        with Session(engine) as session:
            # Daily order summary view
            session.exec(text("""
                CREATE OR REPLACE VIEW daily_order_summary AS
                SELECT 
                    DATE(created_at) as order_date,
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN payment_status = 'paid' THEN 1 END) as paid_orders,
                    SUM(CASE WHEN payment_status = 'paid' THEN total ELSE 0 END) as daily_gmv,
                    SUM(CASE WHEN payment_status = 'paid' THEN platform_fee ELSE 0 END) as daily_fees,
                    AVG(CASE WHEN payment_status = 'paid' THEN total END) as avg_order_value,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders
                FROM orders
                GROUP BY DATE(created_at)
                ORDER BY order_date DESC;
            """))
            
            # Monthly user metrics view
            session.exec(text("""
                CREATE OR REPLACE VIEW monthly_user_metrics AS
                SELECT 
                    DATE_TRUNC('month', created_at) as month,
                    role,
                    COUNT(*) as new_users,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_users
                FROM users
                GROUP BY DATE_TRUNC('month', created_at), role
                ORDER BY month DESC, role;
            """))
            
            # Product performance view
            session.exec(text("""
                CREATE OR REPLACE VIEW product_performance AS
                SELECT 
                    p.id as product_id,
                    p.name as product_name,
                    p.category,
                    p.farmer_id,
                    COALESCE(SUM(oi.quantity), 0) as total_quantity_sold,
                    COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_revenue,
                    COUNT(DISTINCT oi.order_id) as order_count,
                    p.quantity_available as current_stock,
                    p.price as current_price,
                    p.status
                FROM products p
                LEFT JOIN order_items oi ON p.id = oi.product_id
                LEFT JOIN orders o ON oi.order_id = o.id AND o.payment_status = 'paid'
                GROUP BY p.id, p.name, p.category, p.farmer_id, p.quantity_available, p.price, p.status;
            """))
            
            # Farmer performance view
            session.exec(text("""
                CREATE OR REPLACE VIEW farmer_performance AS
                SELECT 
                    f.id as farmer_id,
                    f.name as farmer_name,
                    f.location,
                    COUNT(DISTINCT p.id) as total_products,
                    COUNT(CASE WHEN p.status = 'active' THEN 1 END) as active_products,
                    COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_revenue,
                    COUNT(DISTINCT oi.order_id) as total_orders,
                    AVG(CASE WHEN or_rev.rating IS NOT NULL THEN or_rev.rating END) as avg_rating,
                    COUNT(or_rev.id) as total_reviews
                FROM farmer f
                LEFT JOIN products p ON f.id = p.farmer_id
                LEFT JOIN order_items oi ON p.id = oi.product_id
                LEFT JOIN orders o ON oi.order_id = o.id AND o.payment_status = 'paid'
                LEFT JOIN order_reviews or_rev ON o.id = or_rev.order_id
                GROUP BY f.id, f.name, f.location;
            """))
            
            # Dispute analytics view
            session.exec(text("""
                CREATE OR REPLACE VIEW dispute_analytics AS
                SELECT 
                    DATE_TRUNC('month', d.created_at) as month,
                    d.dispute_type,
                    d.status,
                    COUNT(*) as dispute_count,
                    AVG(EXTRACT(EPOCH FROM (d.resolved_at - d.created_at))/86400) as avg_resolution_days,
                    COUNT(CASE WHEN d.status = 'resolved' THEN 1 END) as resolved_count
                FROM disputes d
                GROUP BY DATE_TRUNC('month', d.created_at), d.dispute_type, d.status
                ORDER BY month DESC;
            """))
            
            session.commit()
    
    @staticmethod
    def create_materialized_views():
        """Create materialized views for heavy analytics queries."""
        
        with Session(engine) as session:
            # Drop existing materialized views if they exist
            session.exec(text("DROP MATERIALIZED VIEW IF EXISTS mv_monthly_revenue_summary;"))
            session.exec(text("DROP MATERIALIZED VIEW IF EXISTS mv_top_products_summary;"))
            session.exec(text("DROP MATERIALIZED VIEW IF EXISTS mv_user_engagement_summary;"))
            
            # Monthly revenue summary materialized view
            session.exec(text("""
                CREATE MATERIALIZED VIEW mv_monthly_revenue_summary AS
                SELECT 
                    DATE_TRUNC('month', o.created_at) as month,
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN o.payment_status = 'paid' THEN 1 END) as paid_orders,
                    SUM(CASE WHEN o.payment_status = 'paid' THEN o.total ELSE 0 END) as gmv,
                    SUM(CASE WHEN o.payment_status = 'paid' THEN o.platform_fee ELSE 0 END) as platform_fees,
                    SUM(CASE WHEN o.payment_status = 'paid' THEN o.shipping_fee ELSE 0 END) as shipping_fees,
                    AVG(CASE WHEN o.payment_status = 'paid' THEN o.total END) as avg_order_value,
                    COUNT(DISTINCT o.buyer_id) as unique_buyers,
                    COUNT(DISTINCT oi.farmer_id) as active_farmers
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                GROUP BY DATE_TRUNC('month', o.created_at)
                ORDER BY month DESC;
            """))
            
            # Top products summary materialized view
            session.exec(text("""
                CREATE MATERIALIZED VIEW mv_top_products_summary AS
                SELECT 
                    p.id as product_id,
                    p.name as product_name,
                    p.category,
                    p.farmer_id,
                    SUM(oi.quantity) as total_quantity_sold,
                    SUM(oi.quantity * oi.unit_price) as total_revenue,
                    COUNT(DISTINCT oi.order_id) as order_count,
                    COUNT(DISTINCT o.buyer_id) as unique_buyers,
                    AVG(or_rev.rating) as avg_rating,
                    COUNT(or_rev.id) as review_count,
                    MAX(o.created_at) as last_order_date
                FROM products p
                LEFT JOIN order_items oi ON p.id = oi.product_id
                LEFT JOIN orders o ON oi.order_id = o.id AND o.payment_status = 'paid'
                LEFT JOIN order_reviews or_rev ON o.id = or_rev.order_id
                GROUP BY p.id, p.name, p.category, p.farmer_id
                HAVING SUM(oi.quantity) > 0
                ORDER BY total_revenue DESC;
            """))
            
            # User engagement summary materialized view
            session.exec(text("""
                CREATE MATERIALIZED VIEW mv_user_engagement_summary AS
                SELECT 
                    u.id as user_id,
                    u.role,
                    u.created_at as registration_date,
                    COUNT(DISTINCT o.id) as total_orders,
                    SUM(CASE WHEN o.payment_status = 'paid' THEN o.total ELSE 0 END) as total_spent,
                    MAX(o.created_at) as last_order_date,
                    COUNT(DISTINCT c.id) as total_carts,
                    COUNT(DISTINCT or_rev.id) as reviews_given,
                    AVG(or_rev.rating) as avg_rating_given,
                    COUNT(DISTINCT n.id) as notifications_received
                FROM users u
                LEFT JOIN orders o ON u.id = o.buyer_id
                LEFT JOIN carts c ON u.id = c.user_id
                LEFT JOIN order_reviews or_rev ON u.id = or_rev.buyer_id
                LEFT JOIN notifications n ON u.id = n.user_id
                GROUP BY u.id, u.role, u.created_at
                ORDER BY total_spent DESC;
            """))
            
            session.commit()
    
    @staticmethod
    def refresh_materialized_views():
        """Refresh materialized views with latest data."""
        
        with Session(engine) as session:
            session.exec(text("REFRESH MATERIALIZED VIEW mv_monthly_revenue_summary;"))
            session.exec(text("REFRESH MATERIALIZED VIEW mv_top_products_summary;"))
            session.exec(text("REFRESH MATERIALIZED VIEW mv_user_engagement_summary;"))
            session.commit()
    
    @staticmethod
    def create_analytics_indexes():
        """Create indexes for analytics performance."""
        
        with Session(engine) as session:
            # Indexes for common analytics queries
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_orders_payment_status ON orders(payment_status);",
                "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);",
                "CREATE INDEX IF NOT EXISTS idx_orders_buyer_id_created_at ON orders(buyer_id, created_at);",
                "CREATE INDEX IF NOT EXISTS idx_order_items_farmer_id ON order_items(farmer_id);",
                "CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);",
                "CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);",
                "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);",
                "CREATE INDEX IF NOT EXISTS idx_products_farmer_id ON products(farmer_id);",
                "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",
                "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_disputes_created_at ON disputes(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_disputes_status ON disputes(status);",
                "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_inventory_history_created_at ON inventory_history(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_inventory_history_product_id ON inventory_history(product_id);"
            ]
            
            for index_sql in indexes:
                try:
                    session.exec(text(index_sql))
                except Exception as e:
                    print(f"Index creation warning: {e}")
            
            session.commit()
    
    @staticmethod
    def setup_all_views():
        """Set up all views, materialized views, and indexes."""
        
        print("Creating analytics views...")
        DatabaseViews.create_analytics_views()
        
        print("Creating materialized views...")
        DatabaseViews.create_materialized_views()
        
        print("Creating analytics indexes...")
        DatabaseViews.create_analytics_indexes()
        
        print("Analytics database setup complete!")