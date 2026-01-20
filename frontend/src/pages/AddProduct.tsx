import React, { useState, useRef, useEffect } from "react";
import type { DragEvent as ReactDragEvent, ChangeEvent as ReactChangeEvent, MouseEvent as ReactMouseEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useToast } from "@/components/ui/use-toast";
import { secureStorage } from "@/lib/security";
import { ArrowLeft, Loader2, Upload, X, Crop } from "lucide-react";

const AddProduct = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { id } = useParams();
  const isEditMode = !!id;
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const MAX_IMAGES = 6;
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'Vegetables',
    price: '',
    quantity_available: '',
    unit: 'kg',
    min_order_quantity: '1',
  });

  // Load product data in edit mode
  useEffect(() => {
    if (isEditMode) {
      const loadProduct = async () => {
        try {
          const token = secureStorage.get<string>("access_token");
          const response = await fetch(`/api/marketplace/products/${id}`, {
            headers: { 'Authorization': `Bearer ${token}` },
          });
          if (response.ok) {
            const product = await response.json();
            setFormData({
              name: product.name || '',
              description: product.description || '',
              category: product.category || 'Vegetables',
              price: product.price?.toString() || '',
              quantity_available: product.quantity_available?.toString() || '',
              unit: product.unit || 'kg',
              min_order_quantity: product.min_order_quantity?.toString() || '1',
            });
            if (product.images) {
              try {
                const parsed = JSON.parse(product.images);
                const imageArray = Array.isArray(parsed) ? parsed : [product.images.replace(/"/g, '')];
                setImages(imageArray.map((url: string) => ({ file: null as any, preview: url })));
              } catch {
                const imageUrl = product.images.replace(/"/g, '');
                setImages([{ file: null as any, preview: imageUrl }]);
              }
            }
          }
        } catch (error) {
          toast({
            title: "Error",
            description: "Failed to load product",
            variant: "destructive",
          });
        }
      };
      loadProduct();
    }
  }, [id, isEditMode, toast]);
  
  const [images, setImages] = useState<{ file: File; preview: string }[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Cropping state
  const [showCropper, setShowCropper] = useState(false);
  const [rawImage, setRawImage] = useState<string>('');
  const [cropArea, setCropArea] = useState({ x: 50, y: 50, width: 400, height: 300 });
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [imageDimensions, setImageDimensions] = useState({
    naturalWidth: 0,
    naturalHeight: 0,
    displayWidth: 0,
    displayHeight: 0,
  });

  const handleDrag = (e: ReactDragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: ReactDragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files) as File[];
    const imageFiles = files.filter(file => (file.type || "").startsWith('image/'));
    addImages(imageFiles);
  };

  const handleImageSelect = (e: ReactChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files) as File[];
      addImages(files);
    }
  };

  const addImages = (files: File[]) => {
    if (images.length >= MAX_IMAGES) {
      toast({
        title: "Maximum images reached",
        description: `You can upload up to ${MAX_IMAGES} images`,
        variant: "destructive",
      });
      return;
    }

    const file = files[0]; // Process one at a time
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: `${file.name} exceeds 5MB`,
        variant: "destructive",
      });
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      setRawImage(reader.result as string);
      setShowCropper(true);
    };
    reader.readAsDataURL(file);
  };

  const cropImage = async () => {
    if (!rawImage) return;

    // Fixed standard size: 800x600 pixels
    const STANDARD_WIDTH = 800;
    const STANDARD_HEIGHT = 600;

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = STANDARD_WIDTH;
    canvas.height = STANDARD_HEIGHT;
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';

    try {
      // Create bitmap to respect EXIF orientation when supported
      const dataUrlResponse = await fetch(rawImage);
      const blob = await dataUrlResponse.blob();
      let naturalWidth = 0;
      let naturalHeight = 0;

      let source: CanvasImageSource;
      if ('createImageBitmap' in window) {
        const bitmap = await createImageBitmap(blob, { imageOrientation: 'from-image' as any });
        source = bitmap;
        naturalWidth = bitmap.width;
        naturalHeight = bitmap.height;
      } else {
        const img = await new Promise<HTMLImageElement>((resolve, reject) => {
          const i = new Image();
          i.onload = () => resolve(i);
          i.onerror = reject;
          i.src = rawImage;
        });
        source = img;
        naturalWidth = img.naturalWidth || img.width;
        naturalHeight = img.naturalHeight || img.height;
      }

      // Map crop area from displayed image coordinates to natural image coordinates
      const displayWidth = imageDimensions.displayWidth || naturalWidth;
      const displayHeight = imageDimensions.displayHeight || naturalHeight;
      const scaleX = naturalWidth / displayWidth;
      const scaleY = naturalHeight / displayHeight;

      const sourceX = cropArea.x * scaleX;
      const sourceY = cropArea.y * scaleY;
      const sourceWidth = cropArea.width * scaleX;
      const sourceHeight = cropArea.height * scaleY;

      ctx.drawImage(
        source,
        sourceX,
        sourceY,
        sourceWidth,
        sourceHeight,
        0,
        0,
        STANDARD_WIDTH,
        STANDARD_HEIGHT
      );

      const blobOut = await new Promise<Blob | null>((resolve) =>
        canvas.toBlob((b) => resolve(b), 'image/jpeg', 0.9)
      );
      if (blobOut) {
        const croppedFile = new File([blobOut], `product-${Date.now()}.jpg`, { type: 'image/jpeg' });
        const preview = canvas.toDataURL('image/jpeg', 0.9);
        setImages(prev => [...prev, { file: croppedFile, preview }]);
        setShowCropper(false);
        setRawImage('');
        toast({ title: 'Image added', description: `Image resized to ${STANDARD_WIDTH}x${STANDARD_HEIGHT}px` });
      }
    } catch (err) {
      toast({ title: 'Image crop failed', description: 'Please try another image.', variant: 'destructive' });
    }
  };

  const handleMouseMove = (e: ReactMouseEvent<HTMLDivElement>) => {
    if (!isDragging && !isResizing) return;
    
    const container = e.currentTarget.querySelector('img');
    if (!container) return;
    
    const rect = container.getBoundingClientRect();
    
    if (isDragging) {
      const newX = e.clientX - rect.left - dragStart.x;
      const newY = e.clientY - rect.top - dragStart.y;
      
      setCropArea(prev => ({
        ...prev,
        x: Math.max(0, Math.min(newX, rect.width - prev.width)),
        y: Math.max(0, Math.min(newY, rect.height - prev.height)),
      }));
    } else if (isResizing) {
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      
      // Calculate new width maintaining 4:3 ratio
      let newWidth = Math.max(100, mouseX - cropArea.x);
      let newHeight = newWidth * 0.75; // 4:3 ratio
      
      // Constrain to image bounds
      if (cropArea.x + newWidth > rect.width) {
        newWidth = rect.width - cropArea.x;
        newHeight = newWidth * 0.75;
      }
      if (cropArea.y + newHeight > rect.height) {
        newHeight = rect.height - cropArea.y;
        newWidth = newHeight * 1.333; // 4:3 ratio
      }
      
      setCropArea(prev => ({
        ...prev,
        width: newWidth,
        height: newHeight,
      }));
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setIsResizing(false);
  };

  const removeImage = (index: number) => {
    setImages(prev => prev.filter((_, i) => i !== index));
  };

  const moveImage = (from: number, to: number) => {
    setImages(prev => {
      const newImages = [...prev];
      const [moved] = newImages.splice(from, 1);
      newImages.splice(to, 0, moved);
      return newImages;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.price || !formData.quantity_available) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      const token = secureStorage.get<string>("access_token");
      if (!token) {
        throw new Error("Not authenticated");
      }

      const productData: any = {
        ...formData,
        price: parseFloat(formData.price),
        quantity_available: parseInt(formData.quantity_available),
        min_order_quantity: parseInt(formData.min_order_quantity),
        quantity: `${formData.quantity_available} ${formData.unit}`,
      };

      // Upload all images
      const uploadedUrls: string[] = [];
      for (const image of images) {
        if (image.file) {
          const imageFormData = new FormData();
          imageFormData.append('file', image.file);
          
          const uploadResponse = await fetch('/api/marketplace/upload', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
            body: imageFormData,
          });

          if (uploadResponse.ok) {
            const { file_url } = await uploadResponse.json();
            uploadedUrls.push(file_url);
          }
        } else {
          // Keep existing image URL
          uploadedUrls.push(image.preview);
        }
      }

      // Store images as JSON array
      if (uploadedUrls.length > 0) {
        productData.images = JSON.stringify(uploadedUrls);
      }

      // Create or update product
      const url = isEditMode ? `/api/marketplace/products/${id}` : '/api/marketplace/products';
      const method = isEditMode ? 'PUT' : 'POST';
      
      // Get CSRF token
      const csrfResponse = await fetch('/api/auth/csrf-token');
      const { csrf_token } = await csrfResponse.json();
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'X-CSRF-Token': csrf_token,
        },
        body: JSON.stringify(productData),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error || `Failed to ${isEditMode ? 'update' : 'create'} product`);
      }

      toast({
        title: "Success!",
        description: isEditMode ? "Product updated successfully" : "Product listed successfully",
      });

      // Invalidate products query to refresh dashboard
      queryClient.invalidateQueries({ queryKey: ['farmer-products'] });

      navigate('/dashboard');
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to add product",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      {/* Image Cropper Dialog */}
      <Dialog open={showCropper} onOpenChange={setShowCropper}>
        <DialogContent className="max-w-3xl" onMouseMove={handleMouseMove} onMouseUp={handleMouseUp}>
          <DialogHeader>
            <DialogTitle>Crop Image to 800x600 (4:3 Ratio)</DialogTitle>
            <DialogDescription>
              Drag the crop area to select the portion you want to use
            </DialogDescription>
          </DialogHeader>
          <div className="relative bg-muted rounded-lg overflow-hidden select-none" style={{ maxHeight: '500px' }}>
            <img 
              src={rawImage} 
              alt="Original" 
              className="w-full h-auto pointer-events-none"
              style={{ maxHeight: '500px', objectFit: 'contain' }}
              draggable={false}
              onLoad={(e) => {
                const imgEl = e.currentTarget;
                const displayWidth = imgEl.clientWidth;
                const displayHeight = imgEl.clientHeight;

                const naturalWidth = imgEl.naturalWidth;
                const naturalHeight = imgEl.naturalHeight;

                setImageDimensions({
                  naturalWidth,
                  naturalHeight,
                  displayWidth,
                  displayHeight,
                });

                const targetRatio = 4 / 3;
                let cropWidth = displayWidth * 0.8;
                let cropHeight = cropWidth / targetRatio;

                if (cropHeight > displayHeight * 0.8) {
                  cropHeight = displayHeight * 0.8;
                  cropWidth = cropHeight * targetRatio;
                }

                const cropX = (displayWidth - cropWidth) / 2;
                const cropY = (displayHeight - cropHeight) / 2;

                setCropArea({
                  x: cropX,
                  y: cropY,
                  width: cropWidth,
                  height: cropHeight,
                });
              }}
            />
            <div
              className="absolute border-4 border-primary bg-primary/10 cursor-move"
              style={{
                left: `${cropArea.x}px`,
                top: `${cropArea.y}px`,
                width: `${cropArea.width}px`,
                height: `${cropArea.height}px`,
              }}
              onMouseDown={(e) => {
                e.preventDefault();
                setIsDragging(true);
                const rect = e.currentTarget.getBoundingClientRect();
                setDragStart({ 
                  x: e.clientX - rect.left, 
                  y: e.clientY - rect.top 
                });
              }}
            >
              <div className="absolute inset-0 flex items-center justify-center text-white font-semibold text-sm bg-black/20 pointer-events-none">
                <Crop className="h-6 w-6 mr-2" />
                Drag to move • Resize from corners
              </div>
              
              {/* Resize handles */}
              <div 
                className="absolute -bottom-2 -right-2 w-6 h-6 bg-primary rounded-full cursor-se-resize border-2 border-white shadow-lg"
                onMouseDown={(e) => {
                  e.stopPropagation();
                  e.preventDefault();
                  setIsResizing(true);
                }}
              />
              <div 
                className="absolute -top-2 -right-2 w-6 h-6 bg-primary rounded-full cursor-ne-resize border-2 border-white shadow-lg"
                onMouseDown={(e) => {
                  e.stopPropagation();
                  e.preventDefault();
                  setIsResizing(true);
                }}
              />
              <div 
                className="absolute -bottom-2 -left-2 w-6 h-6 bg-primary rounded-full cursor-sw-resize border-2 border-white shadow-lg"
                onMouseDown={(e) => {
                  e.stopPropagation();
                  e.preventDefault();
                  setIsResizing(true);
                }}
              />
              <div 
                className="absolute -top-2 -left-2 w-6 h-6 bg-primary rounded-full cursor-nw-resize border-2 border-white shadow-lg"
                onMouseDown={(e) => {
                  e.stopPropagation();
                  e.preventDefault();
                  setIsResizing(true);
                }}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCropper(false)}>
              Cancel
            </Button>
            <Button onClick={cropImage}>
              <Crop className="h-4 w-4 mr-2" />
              Crop & Add Image
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <div className="min-h-screen bg-background">
      <div className="border-b">
        <div className="container max-w-6xl mx-auto px-4 py-4">
          <Button variant="ghost" onClick={() => navigate('/dashboard')} className="mb-2">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
          <h1 className="text-2xl font-bold">{isEditMode ? 'Edit Product' : 'Add a Product'}</h1>
          <p className="text-sm text-muted-foreground">Required fields are marked with *</p>
        </div>
      </div>

      <div className="container max-w-6xl mx-auto px-4 py-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Product Images */}
          <Card>
            <CardHeader>
              <CardTitle>Product Images</CardTitle>
              <CardDescription>
                Add up to 6 images. First image will be the main product image.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {images.map((img, index) => (
                  <div key={index} className="relative group aspect-square border-2 rounded-lg overflow-hidden">
                    <img src={img.preview} alt={`Product ${index + 1}`} className="w-full h-full object-cover" />
                    {index === 0 && (
                      <div className="absolute top-2 left-2 bg-primary text-primary-foreground text-xs px-2 py-1 rounded">
                        Main
                      </div>
                    )}
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                      {index > 0 && (
                        <Button
                          type="button"
                          size="sm"
                          variant="secondary"
                          onClick={() => moveImage(index, 0)}
                        >
                          Set as Main
                        </Button>
                      )}
                      <Button
                        type="button"
                        size="icon"
                        variant="destructive"
                        onClick={() => removeImage(index)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
                
                {images.length < MAX_IMAGES && (
                  <div
                    className={`aspect-square border-2 border-dashed rounded-lg flex flex-col items-center justify-center cursor-pointer transition-colors ${
                      dragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50'
                    }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById('image-upload')?.click()}
                  >
                    <Upload className="h-8 w-8 text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground text-center px-4">
                      Drag and drop or click to upload
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      JPG, PNG up to 5MB
                    </p>
                  </div>
                )}
              </div>
              <Input
                id="image-upload"
                type="file"
                accept="image/*"
                multiple
                className="hidden"
                onChange={handleImageSelect}
              />
            </CardContent>
          </Card>

          {/* Product Information */}
          <Card>
            <CardHeader>
              <CardTitle>Product Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="name">Product Name *</Label>
                <Input
                  id="name"
                  placeholder="e.g., Fresh Organic Tomatoes"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Product Description *</Label>
                <Textarea
                  id="description"
                  placeholder="Describe your product in detail..."
                  rows={5}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Include key features, growing methods, and any certifications
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="category">Category *</Label>
                  <Select
                    value={formData.category}
                    onValueChange={(value) => setFormData({ ...formData, category: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Vegetables">Vegetables</SelectItem>
                      <SelectItem value="Fruits">Fruits</SelectItem>
                      <SelectItem value="Grains">Grains</SelectItem>
                      <SelectItem value="Dairy & Eggs">Dairy & Eggs</SelectItem>
                      <SelectItem value="Meat & Poultry">Meat & Poultry</SelectItem>
                      <SelectItem value="Herbs & Spices">Herbs & Spices</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Pricing & Inventory */}
          <Card>
            <CardHeader>
              <CardTitle>Pricing & Inventory</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="price">Price per Unit *</Label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">৳</span>
                    <Input
                      id="price"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      className="pl-7"
                      value={formData.price}
                      onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="quantity">Available Quantity *</Label>
                  <Input
                    id="quantity"
                    type="number"
                    placeholder="100"
                    value={formData.quantity_available}
                    onChange={(e) => setFormData({ ...formData, quantity_available: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="unit">Unit *</Label>
                  <Select
                    value={formData.unit}
                    onValueChange={(value) => setFormData({ ...formData, unit: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="kg">Kilograms (kg)</SelectItem>
                      <SelectItem value="lb">Pounds (lb)</SelectItem>
                      <SelectItem value="g">Grams (g)</SelectItem>
                      <SelectItem value="oz">Ounces (oz)</SelectItem>
                      <SelectItem value="piece">Pieces</SelectItem>
                      <SelectItem value="bunch">Bunches</SelectItem>
                      <SelectItem value="dozen">Dozen</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="min_order">Minimum Order Quantity</Label>
                <Input
                  id="min_order"
                  type="number"
                  placeholder="1"
                  value={formData.min_order_quantity}
                  onChange={(e) => setFormData({ ...formData, min_order_quantity: e.target.value })}
                />
                <p className="text-xs text-muted-foreground">
                  Minimum quantity buyers must purchase
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Submit */}
          <div className="flex items-center justify-between pt-6 border-t">
            <Button type="button" variant="outline" onClick={() => navigate('/dashboard')}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting} size="lg">
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  {isEditMode ? 'Updating...' : 'Publishing...'}
                </>
              ) : (
                isEditMode ? 'Update Product' : 'Publish Product'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
    </>
  );
};

export default AddProduct;
