"""
Image processing service for handling product image uploads and processing.
"""
import os
import uuid
import hashlib
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
from io import BytesIO

from PIL import Image, ImageOps
from fastapi import HTTPException, UploadFile
import aiofiles

from ..models import ProductImage
from ..database import engine
from sqlmodel import Session


class ImageProcessor:
    """Service for processing and managing product images."""
    
    # Supported image formats
    SUPPORTED_FORMATS = {'JPEG', 'PNG', 'WEBP'}
    
    # Image size configurations
    SIZES = {
        'thumbnail': (150, 150),
        'small': (300, 300),
        'medium': (600, 600),
        'large': (1200, 1200),
        'original': None  # Keep original size
    }
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    def __init__(self, upload_dir: str = "uploads/images"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def validate_image(self, file: UploadFile) -> Dict[str, Any]:
        """Validate uploaded image file."""
        # Check file size
        if file.size and file.size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size too large. Maximum size is {self.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size too large. Maximum size is {self.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Validate image format
        try:
            with Image.open(BytesIO(content)) as img:
                if img.format not in self.SUPPORTED_FORMATS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unsupported image format. Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
                    )
                
                # Check image dimensions (minimum 100x100)
                if img.width < 100 or img.height < 100:
                    raise HTTPException(
                        status_code=400,
                        detail="Image dimensions too small. Minimum size is 100x100 pixels"
                    )
                
                # Check for maximum dimensions (5000x5000)
                if img.width > 5000 or img.height > 5000:
                    raise HTTPException(
                        status_code=400,
                        detail="Image dimensions too large. Maximum size is 5000x5000 pixels"
                    )
                
                return {
                    'format': img.format,
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'size': len(content)
                }
        
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            )
    
    def _generate_filename(self, original_filename: str, size: str = None) -> str:
        """Generate unique filename for image."""
        # Create hash from original filename and timestamp
        hash_input = f"{original_filename}{uuid.uuid4()}"
        file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        
        # Get file extension
        ext = Path(original_filename).suffix.lower()
        if not ext:
            ext = '.jpg'
        
        # Add size suffix if specified
        if size and size != 'original':
            return f"{file_hash}_{size}{ext}"
        else:
            return f"{file_hash}{ext}"
    
    def _resize_image(self, image: Image.Image, size: Tuple[int, int], maintain_aspect: bool = True) -> Image.Image:
        """Resize image to specified dimensions."""
        if maintain_aspect:
            # Use thumbnail method to maintain aspect ratio
            image_copy = image.copy()
            image_copy.thumbnail(size, Image.Resampling.LANCZOS)
            return image_copy
        else:
            # Resize to exact dimensions
            return image.resize(size, Image.Resampling.LANCZOS)
    
    def _optimize_image(self, image: Image.Image, format: str = 'JPEG', quality: int = 85) -> bytes:
        """Optimize image for web delivery."""
        # Convert to RGB if necessary (for JPEG)
        if format == 'JPEG' and image.mode in ('RGBA', 'P'):
            # Create white background for transparency
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Apply auto-orientation
        image = ImageOps.exif_transpose(image)
        
        # Save optimized image
        buffer = BytesIO()
        save_kwargs = {'format': format, 'optimize': True}
        
        if format == 'JPEG':
            save_kwargs['quality'] = quality
            save_kwargs['progressive'] = True
        elif format == 'PNG':
            save_kwargs['compress_level'] = 6
        elif format == 'WEBP':
            save_kwargs['quality'] = quality
            save_kwargs['method'] = 6
        
        image.save(buffer, **save_kwargs)
        return buffer.getvalue()
    
    async def process_image(self, file: UploadFile, generate_sizes: List[str] = None) -> Dict[str, Any]:
        """Process uploaded image and generate different sizes."""
        if generate_sizes is None:
            generate_sizes = ['thumbnail', 'small', 'medium', 'large']
        
        # Validate image
        image_info = await self.validate_image(file)
        
        # Read file content
        content = await file.read()
        
        # Open image
        with Image.open(BytesIO(content)) as img:
            processed_images = {}
            
            # Generate different sizes
            for size_name in generate_sizes:
                if size_name not in self.SIZES:
                    continue
                
                size_config = self.SIZES[size_name]
                
                if size_config is None:  # Original size
                    processed_img = img.copy()
                else:
                    processed_img = self._resize_image(img, size_config)
                
                # Optimize image
                optimized_data = self._optimize_image(
                    processed_img,
                    format='JPEG' if img.format == 'JPEG' else 'PNG'
                )
                
                # Generate filename
                filename = self._generate_filename(file.filename, size_name)
                file_path = self.upload_dir / filename
                
                # Save file
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(optimized_data)
                
                processed_images[size_name] = {
                    'filename': filename,
                    'path': str(file_path),
                    'url': f"/images/{filename}",
                    'width': processed_img.width,
                    'height': processed_img.height,
                    'size': len(optimized_data)
                }
        
        return {
            'original_info': image_info,
            'processed_images': processed_images,
            'primary_url': processed_images.get('medium', processed_images.get('large', {})).get('url')
        }
    
    async def delete_image_files(self, image_urls: List[str]) -> bool:
        """Delete image files from storage."""
        try:
            for url in image_urls:
                # Extract filename from URL
                filename = Path(url).name
                file_path = self.upload_dir / filename
                
                if file_path.exists():
                    file_path.unlink()
            
            return True
        except Exception:
            return False
    
    def get_image_variants(self, base_filename: str) -> List[str]:
        """Get all size variants of an image."""
        base_name = Path(base_filename).stem
        ext = Path(base_filename).suffix
        
        variants = []
        for size_name in self.SIZES.keys():
            if size_name == 'original':
                variant_filename = f"{base_name}{ext}"
            else:
                variant_filename = f"{base_name}_{size_name}{ext}"
            
            variant_path = self.upload_dir / variant_filename
            if variant_path.exists():
                variants.append(f"/images/{variant_filename}")
        
        return variants


class ProductImageService:
    """Service for managing product images in database."""
    
    def __init__(self, session: Session):
        self.session = session
        self.image_processor = ImageProcessor()
    
    async def upload_product_image(
        self,
        product_id: int,
        file: UploadFile,
        alt_text: Optional[str] = None,
        is_primary: bool = False
    ) -> ProductImage:
        """Upload and process a product image."""
        # Process image
        processed_data = await self.image_processor.process_image(file)
        
        # If this is set as primary, unset other primary images
        if is_primary:
            self._unset_primary_images(product_id)
        
        # Create database record
        product_image = ProductImage(
            product_id=product_id,
            image_url=processed_data['primary_url'],
            alt_text=alt_text or f"Product image for product {product_id}",
            is_primary=is_primary,
            width=processed_data['processed_images'].get('medium', {}).get('width'),
            height=processed_data['processed_images'].get('medium', {}).get('height'),
            file_size=processed_data['processed_images'].get('medium', {}).get('size'),
            file_format=processed_data['original_info']['format'].lower()
        )
        
        self.session.add(product_image)
        self.session.commit()
        self.session.refresh(product_image)
        
        return product_image
    
    def _unset_primary_images(self, product_id: int):
        """Unset primary flag for all images of a product."""
        from sqlmodel import select, update
        
        stmt = update(ProductImage).where(
            ProductImage.product_id == product_id
        ).values(is_primary=False)
        
        self.session.exec(stmt)
    
    def get_product_images(self, product_id: int) -> List[ProductImage]:
        """Get all images for a product."""
        from sqlmodel import select
        
        stmt = select(ProductImage).where(
            ProductImage.product_id == product_id
        ).order_by(ProductImage.is_primary.desc(), ProductImage.sort_order.asc())
        
        return self.session.exec(stmt).all()
    
    def get_primary_image(self, product_id: int) -> Optional[ProductImage]:
        """Get the primary image for a product."""
        from sqlmodel import select
        
        stmt = select(ProductImage).where(
            ProductImage.product_id == product_id,
            ProductImage.is_primary == True
        ).limit(1)
        
        return self.session.exec(stmt).first()
    
    async def delete_product_image(self, image_id: int) -> bool:
        """Delete a product image."""
        image = self.session.get(ProductImage, image_id)
        if not image:
            return False
        
        # Get all variants of the image
        variants = self.image_processor.get_image_variants(
            Path(image.image_url).name
        )
        
        # Delete files
        await self.image_processor.delete_image_files(variants)
        
        # Delete database record
        self.session.delete(image)
        self.session.commit()
        
        return True
    
    def update_image_order(self, product_id: int, image_orders: List[Dict[str, int]]) -> bool:
        """Update sort order of product images."""
        try:
            for order_data in image_orders:
                image_id = order_data['image_id']
                sort_order = order_data['sort_order']
                
                image = self.session.get(ProductImage, image_id)
                if image and image.product_id == product_id:
                    image.sort_order = sort_order
            
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False
    
    def set_primary_image(self, product_id: int, image_id: int) -> bool:
        """Set an image as primary for a product."""
        try:
            # Unset all primary images for the product
            self._unset_primary_images(product_id)
            
            # Set the specified image as primary
            image = self.session.get(ProductImage, image_id)
            if image and image.product_id == product_id:
                image.is_primary = True
                self.session.commit()
                return True
            
            return False
        except Exception:
            self.session.rollback()
            return False


def get_image_processor() -> ImageProcessor:
    """Dependency to get image processor."""
    return ImageProcessor()


def get_product_image_service(session: Session = None) -> ProductImageService:
    """Dependency to get product image service."""
    if session is None:
        session = Session(engine)
    return ProductImageService(session)