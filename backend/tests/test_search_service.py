"""
Unit tests for search service.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from decimal import Decimal

from app.models import Product, ProductStatus
from app.services.search_service import SearchService
from app.services.product_validation import ProductSearchRequest


class TestSearchService:
    """Test search service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.service = SearchService(self.mock_session)

    def create_mock_product(self, **kwargs):
        """Create a mock product with default values."""
        defaults = {
            'id': 1,
            'name': 'Test Product',
            'description': 'A test product',
            'category': 'vegetables',
            'price': Decimal('10.99'),
            'quantity_available': 100,
            'unit': 'kg',
            'farmer_id': 1,
            'status': ProductStatus.ACTIVE,
            'images': [],
            'tags': ['organic', 'local'],
            'sku': 'TEST-001',
            'weight': Decimal('1.0'),
            'dimensions': None,
            'min_order_quantity': 1,
            'max_order_quantity': None,
            'harvest_date': None,
            'expiry_date': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        defaults.update(kwargs)
        return Product(**defaults)

    def test_search_products_basic(self):
        """Test basic product search."""
        mock_products = [
            self.create_mock_product(id=1, name="Tomatoes"),
            self.create_mock_product(id=2, name="Carrots")
        ]
        
        # Mock query execution
        mock_result = Mock()
        mock_result.all.return_value = mock_products
        
        # Mock count query
        self.mock_session.exec.side_effect = [5, mock_result]  # count, then products
        
        search_params = ProductSearchRequest(
            query="vegetables",
            limit=10,
            offset=0
        )
        
        with patch('app.services.search_service.select') as mock_select, \
             patch('app.services.search_service.func') as mock_func:
            
            result = self.service.search_products(search_params)
        
        assert len(result["products"]) == 2
        assert result["total_count"] == 5
        assert result["has_more"] is True
        assert "filters_applied" in result

    def test_search_products_with_filters(self):
        """Test product search with multiple filters."""
        mock_products = [
            self.create_mock_product(
                id=1,
                name="Organic Tomatoes",
                category="vegetables",
                price=Decimal("15.99"),
                unit="kg"
            )
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_products
        self.mock_session.exec.side_effect = [1, mock_result]
        
        search_params = ProductSearchRequest(
            category="vegetables",
            min_price=Decimal("10.00"),
            max_price=Decimal("20.00"),
            unit="kg",
            in_stock_only=True
        )
        
        with patch('app.services.search_service.select') as mock_select, \
             patch('app.services.search_service.func') as mock_func:
            
            result = self.service.search_products(search_params)
        
        assert len(result["products"]) == 1
        assert result["filters_applied"]["category"] == "vegetables"
        assert result["filters_applied"]["price_range"]["min"] == Decimal("10.00")

    def test_build_search_conditions(self):
        """Test building search conditions from query text."""
        conditions = self.service._build_search_conditions("organic tomatoes")
        
        # Should create conditions for each term
        assert len(conditions) == 2  # Two terms: "organic" and "tomatoes"

    def test_apply_sorting_ascending(self):
        """Test applying ascending sort."""
        mock_query = Mock()
        
        search_params = ProductSearchRequest(
            sort_by="price",
            sort_order="asc"
        )
        
        with patch.object(Product, 'price') as mock_price_attr, \
             patch.object(Product, 'id') as mock_id_attr:
            
            result = self.service._apply_sorting(mock_query, search_params)
            
            # Should call order_by twice (price asc, then id asc)
            assert mock_query.order_by.call_count == 2

    def test_apply_sorting_descending(self):
        """Test applying descending sort."""
        mock_query = Mock()
        
        search_params = ProductSearchRequest(
            sort_by="created_at",
            sort_order="desc"
        )
        
        with patch.object(Product, 'created_at') as mock_created_attr, \
             patch.object(Product, 'id') as mock_id_attr:
            
            result = self.service._apply_sorting(mock_query, search_params)
            
            assert mock_query.order_by.call_count == 2

    def test_enrich_product_results_basic(self):
        """Test basic product result enrichment."""
        products = [
            self.create_mock_product(
                id=1,
                name="Fresh Tomatoes",
                quantity_available=50,
                expiry_date=datetime.utcnow() + timedelta(days=5)
            )
        ]
        
        enriched = self.service._enrich_product_results(products)
        
        assert len(enriched) == 1
        result = enriched[0]
        
        assert result["id"] == 1
        assert result["name"] == "Fresh Tomatoes"
        assert result["is_available"] is True
        assert result["stock_level"] == "high"  # 50 > 20
        assert result["days_until_expiry"] == 5

    def test_enrich_product_results_with_search_query(self):
        """Test product result enrichment with search relevance."""
        products = [
            self.create_mock_product(
                id=1,
                name="Organic Tomatoes",
                description="Fresh organic tomatoes"
            ),
            self.create_mock_product(
                id=2,
                name="Regular Carrots",
                description="Standard carrots"
            )
        ]
        
        enriched = self.service._enrich_product_results(products, "tomatoes")
        
        # Should be sorted by relevance (tomatoes first)
        assert enriched[0]["name"] == "Organic Tomatoes"
        assert enriched[0]["relevance_score"] > enriched[1]["relevance_score"]

    def test_get_stock_level(self):
        """Test stock level calculation."""
        assert self.service._get_stock_level(0) == "out_of_stock"
        assert self.service._get_stock_level(3) == "low"
        assert self.service._get_stock_level(15) == "medium"
        assert self.service._get_stock_level(50) == "high"

    def test_calculate_days_until_expiry(self):
        """Test days until expiry calculation."""
        # No expiry date
        assert self.service._calculate_days_until_expiry(None) is None
        
        # Already expired
        past_date = datetime.utcnow() - timedelta(days=1)
        assert self.service._calculate_days_until_expiry(past_date) == 0
        
        # Future expiry (allow for timing precision)
        future_date = datetime.utcnow() + timedelta(days=5)
        days_remaining = self.service._calculate_days_until_expiry(future_date)
        assert days_remaining in [4, 5]  # Allow for timing precision

    def test_calculate_relevance_score(self):
        """Test search relevance score calculation."""
        product = self.create_mock_product(
            name="Organic Tomatoes",
            description="Fresh organic tomatoes from local farm",
            category="vegetables",
            tags=["organic", "local", "fresh"],
            quantity_available=10
        )
        
        # Test exact name match
        score1 = self.service._calculate_relevance_score(product, "Organic Tomatoes")
        assert score1 > 0
        
        # Test partial name match
        score2 = self.service._calculate_relevance_score(product, "tomatoes")
        assert score2 > 0
        
        # Test no match
        score3 = self.service._calculate_relevance_score(product, "bananas")
        assert score3 >= 0  # Might get boost for being available

    def test_get_applied_filters(self):
        """Test getting applied filters summary."""
        search_params = ProductSearchRequest(
            query="organic",
            category="vegetables",
            min_price=Decimal("5.00"),
            max_price=Decimal("15.00"),
            tags=["organic", "local"],
            unit="kg"
        )
        
        filters = self.service._get_applied_filters(search_params)
        
        assert filters["search_query"] == "organic"
        assert filters["category"] == "vegetables"
        assert filters["price_range"]["min"] == Decimal("5.00")
        assert filters["price_range"]["max"] == Decimal("15.00")
        assert filters["tags"] == ["organic", "local"]
        assert filters["unit"] == "kg"

    def test_get_search_facets(self):
        """Test getting search facets."""
        # Mock category results
        category_results = [("vegetables", 10), ("fruits", 5)]
        unit_results = [("kg", 8), ("piece", 7)]
        price_stats = Mock()
        price_stats.min_price = Decimal("5.00")
        price_stats.max_price = Decimal("25.00")
        price_stats.avg_price = Decimal("15.00")
        
        mock_results = [
            Mock(all=Mock(return_value=category_results)),
            Mock(all=Mock(return_value=unit_results)),
            Mock(first=Mock(return_value=price_stats))
        ]
        
        # Mock count queries for price ranges
        count_results = [2, 3, 4, 3, 3]  # 5 price range buckets
        mock_results.extend([Mock(one=Mock(return_value=count)) for count in count_results])
        
        self.mock_session.exec.side_effect = mock_results
        
        search_params = ProductSearchRequest()
        
        with patch('app.services.search_service.select') as mock_select, \
             patch('app.services.search_service.func') as mock_func:
            
            facets = self.service._get_search_facets(search_params)
        
        assert len(facets["categories"]) == 2
        assert facets["categories"][0]["value"] == "vegetables"
        assert facets["categories"][0]["count"] == 10
        
        assert len(facets["units"]) == 2
        assert facets["price_stats"]["min"] == 5.00
        assert facets["price_stats"]["max"] == 25.00

    def test_get_search_suggestions(self):
        """Test getting search suggestions."""
        mock_names = ["Organic Tomatoes", "Cherry Tomatoes"]
        mock_categories = ["vegetables"]
        
        mock_results = [
            Mock(all=Mock(return_value=mock_names)),
            Mock(all=Mock(return_value=mock_categories))
        ]
        
        self.mock_session.exec.side_effect = mock_results
        
        with patch('app.services.search_service.select') as mock_select:
            suggestions = self.service.get_search_suggestions("tom", limit=5)
        
        assert len(suggestions) == 3  # 2 names + 1 category
        assert "Organic Tomatoes" in suggestions

    def test_get_search_suggestions_short_query(self):
        """Test search suggestions with short query."""
        suggestions = self.service.get_search_suggestions("a", limit=5)
        assert suggestions == []  # Too short

    def test_get_popular_searches(self):
        """Test getting popular searches."""
        mock_results = [("vegetables", 15), ("fruits", 10)]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_results
        self.mock_session.exec.return_value = mock_result
        
        with patch('app.services.search_service.select') as mock_select, \
             patch('app.services.search_service.func') as mock_func:
            
            popular = self.service.get_popular_searches(limit=5)
        
        assert len(popular) == 2
        assert popular[0]["term"] == "vegetables"
        assert popular[0]["type"] == "category"
        assert popular[0]["product_count"] == 15

    def test_get_trending_products(self):
        """Test getting trending products."""
        mock_products = [
            self.create_mock_product(
                id=1,
                name="New Product",
                created_at=datetime.utcnow() - timedelta(days=2)
            )
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_products
        self.mock_session.exec.return_value = mock_result
        
        with patch('app.services.search_service.select') as mock_select:
            trending = self.service.get_trending_products(limit=5)
        
        assert len(trending) == 1
        assert trending[0].name == "New Product"