
import { useState, useMemo, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerTrigger, DrawerFooter, DrawerClose } from "@/components/ui/drawer";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { ArrowLeft, Search, Filter, MapPin, Star, Plus, ShoppingCart, X, Minus, ZoomIn } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { listProducts, createCheckoutSession } from "@/lib/api";
import type { Product } from "@/types";
import { useToast } from "@/components/ui/use-toast";
import { secureStorage } from "@/lib/security";
import { useTranslation } from "@/i18n/config";
import { useCart } from "@/contexts/CartContext";

const PLATFORM_FEE_RATE = Number(import.meta.env.VITE_PLATFORM_FEE_RATE ?? 0.08);

const Marketplace = () => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState("");
  const { cart, addToCart, removeFromCart, updateQuantity, cartTotal, formatPrice } = useCart();
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [viewingImage, setViewingImage] = useState<string | null>(null);
  const [showSignInDialog, setShowSignInDialog] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const isAuthenticated = () => {
    return !!(secureStorage.get<string>("access_token") || localStorage.getItem("access_token"));
  };

  const { data: products, isLoading, isError } = useQuery<Product[]>({
    queryKey: ["products"],
    queryFn: listProducts,
  });

  // Prompt to sign in when leaving page with cart items
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (cart.length > 0 && !isAuthenticated()) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [cart.length]);

  const handleBuyNow = async (product: Product) => {
    if (!isAuthenticated()) {
      setShowSignInDialog(true);
      return;
    }

    setIsCheckingOut(true);
    try {
      const payload = {
        items: [{ product_id: product.id, quantity: 1 }],
        success_url: `${window.location.origin}/orders`,
        cancel_url: window.location.href,
      };
      const data = await createCheckoutSession(payload);
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        toast({ title: "Checkout Error", description: "Could not retrieve checkout URL.", variant: "destructive" });
      }
    } catch (error: any) {
      const msg = String(error?.message ?? "Failed to create checkout session.");
      toast({ title: "Checkout Error", description: msg, variant: "destructive" });
    } finally {
      setIsCheckingOut(false);
    }
  };

  const platformFee = useMemo(() => {
    return Math.round(cartTotal * PLATFORM_FEE_RATE * 100) / 100;
  }, [cartTotal]);

  const grandTotal = useMemo(() => cartTotal + platformFee, [cartTotal, platformFee]);

  const handleCheckout = async () => {
    if (!isAuthenticated()) {
      setShowSignInDialog(true);
      return;
    }

    setIsCheckingOut(true);
    try {
      const payload = {
        items: cart.map(item => ({ product_id: item.product.id, quantity: item.quantity })),
        success_url: `${window.location.origin}/orders`,
        cancel_url: window.location.href,
      };
      const data = await createCheckoutSession(payload);
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        toast({ title: "Checkout Error", description: "Could not retrieve checkout URL.", variant: "destructive" });
      }
    } catch (error: any) {
      console.error("Checkout failed:", error);
      const msg = String(error?.message ?? "Failed to create checkout session.");
      toast({ title: "Checkout Error", description: msg, variant: "destructive" });
    } finally {
      setIsCheckingOut(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Sign In Dialog */}
      <Dialog open={showSignInDialog} onOpenChange={setShowSignInDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('marketplace.signInRequired')}</DialogTitle>
            <DialogDescription>
              {cart.length > 0
                ? t('marketplace.signInToCheckout')
                : t('marketplace.signInToContinue')}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button
              variant="outline"
              onClick={() => setShowSignInDialog(false)}
              className="w-full sm:w-auto"
            >
              {t('marketplace.continueShopping')}
            </Button>
            <Button
              onClick={() => {
                const redirect = encodeURIComponent(window.location.pathname + window.location.search);
                window.location.href = `/auth?redirect=${redirect}`;
              }}
              className="w-full sm:w-auto"
            >
              {t('common.signIn')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Image Viewer Dialog */}
      <Dialog open={!!viewingImage} onOpenChange={() => setViewingImage(null)}>
        <DialogContent className="max-w-4xl">
          <img
            src={viewingImage || ''}
            alt="Product"
            className="w-full h-auto max-h-[80vh] object-contain"
          />
        </DialogContent>
      </Dialog>

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link to="/dashboard">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              {t('common.back')}
            </Button>
          </Link>
          <div className="flex-1">
            <h1 className="text-3xl font-bold">{t('marketplace.title')}</h1>
            <p className="text-muted-foreground">{t('home.subtitle')}</p>
          </div>
          <Drawer>
            <DrawerTrigger asChild>
              <Button variant="outline">
                <ShoppingCart className="h-4 w-4 mr-2" />
                {t('cart.title')} ({cart.reduce((sum, item) => sum + item.quantity, 0)})
              </Button>
            </DrawerTrigger>
            <DrawerContent>
              <DrawerHeader>
                <DrawerTitle>{t('cart.title')}</DrawerTitle>
              </DrawerHeader>
              <div className="px-4 space-y-4">
                {cart.length === 0 ? (
                  <p className="text-muted-foreground text-center py-8">{t('cart.empty')}</p>
                ) : (
                  cart.map(item => (
                    <div key={item.product.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold">{item.product.name}</p>
                        <p className="text-sm text-muted-foreground">৳{formatPrice(item.product.price)}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button size="icon" variant="ghost" onClick={() => updateQuantity(item.product.id, item.quantity - 1)}>
                          <Minus className="h-4 w-4" />
                        </Button>
                        <span>{item.quantity}</span>
                        <Button size="icon" variant="ghost" onClick={() => updateQuantity(item.product.id, item.quantity + 1)}>
                          <Plus className="h-4 w-4" />
                        </Button>
                        <Button size="icon" variant="ghost" onClick={() => removeFromCart(item.product.id)}>
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
              <DrawerFooter>
                <div className="space-y-1 mb-2">
                  <div className="flex justify-between text-sm">
                    <span>{t('cart.subtotal')}</span>
                    <span>৳{formatPrice(cartTotal)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>{t('cart.platformFee')} ({(PLATFORM_FEE_RATE * 100).toFixed(0)}%)</span>
                    <span>৳{formatPrice(platformFee)}</span>
                  </div>
                  <div className="flex justify-between items-center pt-2">
                    <span className="font-bold text-lg">{t('cart.total')}</span>
                    <span className="font-bold text-lg">৳{formatPrice(grandTotal)}</span>
                  </div>
                </div>
                <Button onClick={handleCheckout} disabled={cart.length === 0 || isCheckingOut}>
                  {isCheckingOut ? t('common.loading') : t('common.checkout')}
                </Button>
                <DrawerClose asChild>
                  <Button variant="outline">{t('marketplace.continueShopping')}</Button>
                </DrawerClose>
              </DrawerFooter>
            </DrawerContent>
          </Drawer>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              placeholder={t('marketplace.searchPlaceholder')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            {t('common.filter')}
          </Button>
        </div>

        {/* Marketplace Tabs */}
        <Tabs defaultValue="browse" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="browse">{t('products.title')}</TabsTrigger>
            <TabsTrigger value="mylistings" asChild>
              <Link to="/dashboard">{t('dashboard.title')}</Link>
            </TabsTrigger>
            <TabsTrigger value="orders" asChild>
              <Link to="/orders">{t('orders.title')}</Link>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="browse" className="space-y-6">
            {/* Categories */}
            <div className="flex flex-wrap gap-2 mb-6">
              {["All", "Vegetables", "Fruits", "Grains", "Dairy & Eggs", "Herbs", "Organic"].map((category) => (
                <Badge key={category} variant={category === "All" ? "default" : "secondary"} className="cursor-pointer">
                  {category}
                </Badge>
              ))}
            </div>

            {/* Featured Products */}
            <div>
              <h2 className="text-2xl font-bold mb-4">{t('products.title')}</h2>
              {isLoading && <p className="text-muted-foreground">{t('common.loading')}</p>}
              {isError && <p className="text-red-600">{t('common.error')}</p>}
              {!isLoading && !isError && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {(products ?? [])
                    .filter(p => p.name.toLowerCase().includes(searchQuery.toLowerCase()))
                    .sort((a, b) => {
                      const af = (a.category ?? '').toLowerCase() === 'featured';
                      const bf = (b.category ?? '').toLowerCase() === 'featured';
                      if (af === bf) return 0;
                      return af ? -1 : 1;
                    })
                    .map((product) => {
                      const images = (() => {
                        try {
                          // If images is already an array, return it directly
                          if (Array.isArray(product.images)) {
                            return product.images;
                          }
                          // If images is null, undefined, or empty, return empty array
                          if (!product.images || product.images === '[]') return [];
                          // If it's a string, try to parse it
                          if (typeof product.images === 'string') {
                            try {
                              const parsed = JSON.parse(product.images);
                              return Array.isArray(parsed) ? parsed : [product.images.replace(/"/g, '')];
                            } catch {
                              // If parsing fails, treat as a single image URL
                              return [product.images.replace(/"/g, '')];
                            }
                          }
                          return [];
                        } catch {
                          return [];
                        }
                      })();

                      return (
                        <Card key={product.id} className="hover:shadow-lg transition-shadow">
                          <div className="aspect-video bg-muted rounded-t-lg overflow-hidden relative group">
                            {images.length > 0 ? (
                              <div className="relative w-full h-full">
                                <img
                                  src={images[0]}
                                  alt={product.name}
                                  className="w-full h-full object-cover cursor-pointer"
                                  onClick={() => setViewingImage(images[0])}
                                  onError={(e) => {
                                    e.currentTarget.src = '/placeholder.svg';
                                  }}
                                />
                                {images.length > 1 && (
                                  <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                                    +{images.length - 1} more
                                  </div>
                                )}
                                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                  <ZoomIn className="h-8 w-8 text-white" />
                                </div>
                              </div>
                            ) : (
                              <div className="flex items-center justify-center w-full h-full bg-muted">
                                <span className="text-muted-foreground">No image</span>
                              </div>
                            )}
                          </div>
                          <CardHeader>
                            <div className="flex justify-between items-start">
                              <div>
                                <CardTitle>{product.name}</CardTitle>
                                <CardDescription>{product.category ?? 'Uncategorized'}</CardDescription>
                              </div>
                              <Badge variant="outline">{product.quantity} available</Badge>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              <p className="text-muted-foreground text-sm h-10 overflow-hidden">{product.description}</p>
                              <div className="flex justify-between items-center">
                                <span className="text-2xl font-bold">
                                  ৳{formatPrice(product.price)}
                                </span>
                                <div className="flex items-center gap-1 text-muted-foreground text-sm">
                                  <Star className="h-4 w-4" />
                                  <span>N/A</span>
                                </div>
                              </div>

                              <div className="space-y-2 text-sm text-muted-foreground">
                                <div className="flex items-center gap-2">
                                  <MapPin className="h-4 w-4" />
                                  <span>Farmer ID: {product.farmer_id ?? '—'}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Added: {new Date(product.created_at).toLocaleDateString()}</span>
                                </div>
                              </div>

                              <div className="flex gap-2 pt-2">
                                <Button className="flex-1" onClick={() => addToCart(product)}>
                                  {t('common.addToCart')}
                                </Button>
                                <Button className="flex-1" variant="secondary" onClick={() => handleBuyNow(product)} disabled={isCheckingOut}>
                                  {isCheckingOut ? t('common.loading') : t('common.checkout')}
                                </Button>
                                <Button variant="outline" onClick={() => toast({ title: t('products.seller'), description: "Messaging coming soon." })}>
                                  {t('products.seller')}
                                </Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="mylistings" className="space-y-6">
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                <Plus className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-2">No products listed yet</h3>
              <p className="text-muted-foreground mb-4">Start selling your farm products to the community</p>
              <Link to="/dashboard">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Go to Dashboard
                </Button>
              </Link>
            </div>
          </TabsContent>

          <TabsContent value="orders" className="space-y-6">
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-2">No orders yet</h3>
              <p className="text-muted-foreground mb-4">Your purchase and sales orders will appear here</p>
              <Link to="/orders">
                <Button variant="outline">View My Orders</Button>
              </Link>
            </div>
          </TabsContent>
        </Tabs>

        {/* Marketplace Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-12">
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-primary">
                {products ? new Set(products.map(p => p.farmer_id)).size : 0}
              </div>
              <div className="text-sm text-muted-foreground">Active Farmers</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-primary">
                {products?.length || 0}
              </div>
              <div className="text-sm text-muted-foreground">Products Listed</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-primary">
                ৳{products ? (products.reduce((sum, p) => {
                  const safePrice = typeof p.price === 'number' ? p.price : parseFloat(p.price);
                  const price = isNaN(safePrice) ? 0 : safePrice;
                  return sum + (price * (p.quantity_available || 0));
                }, 0) / 1000).toFixed(1) : 0}K
              </div>
              <div className="text-sm text-muted-foreground">Total Inventory Value</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-primary">
                {products && products.length > 0 ? (products.filter(p => p.quantity_available > 0).length / products.length * 100).toFixed(1) : 0}%
              </div>
              <div className="text-sm text-muted-foreground">In Stock Rate</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Marketplace;