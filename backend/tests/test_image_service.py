"""
Unit tests for image service.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from io import BytesIO
from PIL import Image
from fastapi import HTTPException, UploadFile

from app.services.image_service import ImageProcessor, ProductImageService
from app.models import ProductImage


class TestImageProcessor:
    """Test image processor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = ImageProcessor(upload_dir="test_uploads")

    def create_test_image(self, width=800, height=600, format='JPEG'):
        """Create a test image."""
        img = Image.new('RGB', (width, height), color='red')
        buffer = BytesIO()
        img.save(buffer, format=format)
        buffer.seek(0)
        return buffer

    def create_upload_file(self, content, filename="test.jpg", content_type="image/jpeg"):
        """Create a mock UploadFile."""
        file = Mock(spec=UploadFile)
        file.filename = filename
        file.content_type = content_type
        file.size = len(content.getvalue()) if hasattr(content, 'getvalue') else len(content)
        file.read = AsyncMock(return_value=content.getvalue() if hasattr(content, 'getvalue') else content)
        file.seek = AsyncMock()
        return file

    @pytest.mark.asyncio
    async def test_validate_image_success(self):
        """Test successful image validation."""
        image_buffer = self.create_test_image()
        upload_file = self.create_upload_file(image_buffer)
        
        result = await self.processor.validate_image(upload_file)
        
        assert result['format'] == 'JPEG'
        assert result['width'] == 800
        assert result['height'] == 600
        assert result['size'] > 0

    @pytest.mark.asyncio
    async def test_validate_image_too_large_file(self):
        """Test validation with file too large."""
        # Create a large mock file
        large_content = b'x' * (11 * 1024 * 1024)  # 11MB
        upload_file = self.create_upload_file(large_content)
        upload_file.size = len(large_content)
        
        with pytest.raises(HTTPException) as exc_info:
            await self.processor.validate_image(upload_file)
        
        assert exc_info.value.status_code == 400
        assert "File size too large" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_image_unsupported_format(self):
        """Test validation with unsupported format."""
        # Create a BMP image (unsupported)
        img = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        img.save(buffer, format='BMP')
        buffer.seek(0)
        
        upload_file = self.create_upload_file(buffer, "test.bmp")
        
        with pytest.raises(HTTPException) as exc_info:
            await self.processor.validate_image(upload_file)
        
        assert exc_info.value.status_code == 400
        assert "Unsupported image format" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_image_too_small(self):
        """Test validation with image too small."""
        image_buffer = self.create_test_image(width=50, height=50)
        upload_file = self.create_upload_file(image_buffer)
        
        with pytest.raises(HTTPException) as exc_info:
            await self.processor.validate_image(upload_file)
        
        assert exc_info.value.status_code == 400
        assert "Image dimensions too small" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_image_too_large_dimensions(self):
        """Test validation with image dimensions too large."""
        image_buffer = self.create_test_image(width=6000, height=6000)
        upload_file = self.create_upload_file(image_buffer)
        
        with pytest.raises(HTTPException) as exc_info:
            await self.processor.validate_image(upload_file)
        
        assert exc_info.value.status_code == 400
        assert "Image dimensions too large" in str(exc_info.value.detail)

    def test_generate_filename(self):
        """Test filename generation."""
        filename1 = self.processor._generate_filename("test.jpg")
        filename2 = self.processor._generate_filename("test.jpg", "thumbnail")
        
        assert filename1.endswith('.jpg')
        assert filename2.endswith('.jpg')
        assert '_thumbnail' in filename2
        assert filename1 != filename2

    def test_resize_image(self):
        """Test image resizing."""
        img = Image.new('RGB', (800, 600), color='red')
        
        # Test with aspect ratio maintained
        resized = self.processor._resize_image(img, (400, 400), maintain_aspect=True)
        assert resized.width <= 400
        assert resized.height <= 400
        
        # Test exact resize
        resized_exact = self.processor._resize_image(img, (400, 400), maintain_aspect=False)
        assert resized_exact.width == 400
        assert resized_exact.height == 400

    def test_optimize_image(self):
        """Test image optimization."""
        img = Image.new('RGB', (100, 100), color='red')
        
        # Test JPEG optimization
        jpeg_data = self.processor._optimize_image(img, format='JPEG', quality=85)
        assert len(jpeg_data) > 0
        
        # Test PNG optimization
        png_data = self.processor._optimize_image(img, format='PNG')
        assert len(png_data) > 0

    @pytest.mark.asyncio
    async def test_process_image_success(self):
        """Test successful image processing."""
        image_buffer = self.create_test_image()
        upload_file = self.create_upload_file(image_buffer)
        
        with patch('aiofiles.open', create=True) as mock_open:
            mock_file = AsyncMock()
            mock_open.return_value.__aenter__.return_value = mock_file
            
            result = await self.processor.process_image(upload_file, ['thumbnail', 'medium'])
            
            assert 'original_info' in result
            assert 'processed_images' in result
            assert 'primary_url' in result
            assert 'thumbnail' in result['processed_images']
            assert 'medium' in result['processed_images']

    @pytest.mark.asyncio
    async def test_delete_image_files(self):
        """Test image file deletion."""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.unlink') as mock_unlink:
            
            mock_exists.return_value = True
            
            result = await self.processor.delete_image_files(['/images/test.jpg'])
            
            assert result is True
            mock_unlink.assert_called_once()

    def test_get_image_variants(self):
        """Test getting image variants."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            
            variants = self.processor.get_image_variants('test.jpg')
            
            assert len(variants) > 0
            assert any('thumbnail' in variant for variant in variants)


class TestProductImageService:
    """Test product image service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.service = ProductImageService(self.mock_session)

    def create_test_image_buffer(self):
        """Create a test image buffer."""
        img = Image.new('RGB', (800, 600), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        return buffer

    def create_upload_file(self, content, filename="test.jpg"):
        """Create a mock UploadFile."""
        file = Mock(spec=UploadFile)
        file.filename = filename
        file.read = AsyncMock(return_value=content.getvalue())
        file.seek = AsyncMock()
        return file

    @pytest.mark.asyncio
    async def test_upload_product_image_success(self):
        """Test successful product image upload."""
        image_buffer = self.create_test_image_buffer()
        upload_file = self.create_upload_file(image_buffer)
        
        # Mock image processing
        with patch.object(self.service.image_processor, 'process_image') as mock_process:
            mock_process.return_value = {
                'primary_url': '/images/test_medium.jpg',
                'processed_images': {
                    'medium': {
                        'width': 600,
                        'height': 450,
                        'size': 50000
                    }
                },
                'original_info': {
                    'format': 'JPEG'
                }
            }
            
            result = await self.service.upload_product_image(
                product_id=1,
                file=upload_file,
                alt_text="Test image",
                is_primary=True
            )
            
            # Verify session operations
            self.mock_session.add.assert_called_once()
            self.mock_session.commit.assert_called()
            
            # Verify the added image has correct properties
            added_image = self.mock_session.add.call_args[0][0]
            assert added_image.product_id == 1
            assert added_image.alt_text == "Test image"
            assert added_image.is_primary is True

    @pytest.mark.asyncio
    async def test_upload_product_image_set_primary(self):
        """Test uploading image and setting as primary."""
        image_buffer = self.create_test_image_buffer()
        upload_file = self.create_upload_file(image_buffer)
        
        with patch.object(self.service.image_processor, 'process_image') as mock_process, \
             patch.object(self.service, '_unset_primary_images') as mock_unset:
            
            mock_process.return_value = {
                'primary_url': '/images/test_medium.jpg',
                'processed_images': {'medium': {'width': 600, 'height': 450, 'size': 50000}},
                'original_info': {'format': 'JPEG'}
            }
            
            await self.service.upload_product_image(
                product_id=1,
                file=upload_file,
                is_primary=True
            )
            
            # Verify that other primary images were unset
            mock_unset.assert_called_once_with(1)

    def test_get_product_images(self):
        """Test getting product images."""
        mock_images = [
            ProductImage(id=1, product_id=1, is_primary=True, sort_order=0),
            ProductImage(id=2, product_id=1, is_primary=False, sort_order=1)
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_images
        self.mock_session.exec.return_value = mock_result
        
        result = self.service.get_product_images(product_id=1)
        
        assert len(result) == 2
        self.mock_session.exec.assert_called_once()

    def test_get_primary_image(self):
        """Test getting primary image."""
        mock_image = ProductImage(id=1, product_id=1, is_primary=True)
        
        mock_result = Mock()
        mock_result.first.return_value = mock_image
        self.mock_session.exec.return_value = mock_result
        
        result = self.service.get_primary_image(product_id=1)
        
        assert result == mock_image
        self.mock_session.exec.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_product_image_success(self):
        """Test successful product image deletion."""
        mock_image = ProductImage(
            id=1,
            product_id=1,
            image_url="/images/test_medium.jpg"
        )
        
        self.mock_session.get.return_value = mock_image
        
        with patch.object(self.service.image_processor, 'get_image_variants') as mock_variants, \
             patch.object(self.service.image_processor, 'delete_image_files') as mock_delete:
            
            mock_variants.return_value = ['/images/test_medium.jpg', '/images/test_thumbnail.jpg']
            mock_delete.return_value = True
            
            result = await self.service.delete_product_image(1)
            
            assert result is True
            self.mock_session.delete.assert_called_once_with(mock_image)
            self.mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_product_image_not_found(self):
        """Test deleting non-existent product image."""
        self.mock_session.get.return_value = None
        
        result = await self.service.delete_product_image(999)
        
        assert result is False
        self.mock_session.delete.assert_not_called()

    def test_update_image_order_success(self):
        """Test successful image order update."""
        mock_images = [
            ProductImage(id=1, product_id=1, sort_order=0),
            ProductImage(id=2, product_id=1, sort_order=1)
        ]
        
        self.mock_session.get.side_effect = mock_images
        
        order_data = [
            {'image_id': 1, 'sort_order': 1},
            {'image_id': 2, 'sort_order': 0}
        ]
        
        result = self.service.update_image_order(product_id=1, image_orders=order_data)
        
        assert result is True
        assert mock_images[0].sort_order == 1
        assert mock_images[1].sort_order == 0
        self.mock_session.commit.assert_called_once()

    def test_set_primary_image_success(self):
        """Test successful primary image setting."""
        mock_image = ProductImage(id=1, product_id=1, is_primary=False)
        self.mock_session.get.return_value = mock_image
        
        with patch.object(self.service, '_unset_primary_images') as mock_unset:
            result = self.service.set_primary_image(product_id=1, image_id=1)
            
            assert result is True
            assert mock_image.is_primary is True
            mock_unset.assert_called_once_with(1)
            self.mock_session.commit.assert_called_once()

    def test_set_primary_image_not_found(self):
        """Test setting primary image for non-existent image."""
        self.mock_session.get.return_value = None
        
        result = self.service.set_primary_image(product_id=1, image_id=999)
        
        assert result is False