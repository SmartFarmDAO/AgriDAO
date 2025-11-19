import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerTrigger, DrawerFooter, DrawerClose } from "@/components/ui/drawer";
import { ArrowLeft, Search, Filter, MapPin, Star, Plus, ShoppingCart, X, Minus } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { listProducts, createCheckoutSession } from "@/lib/api";
import type { Product } from "@/types";
import { useToast } from "@/components/ui/use-toast";

type CartItem = { product: Product; quantity: number };

const PLATFORM_FEE_RATE = Number(import.meta.env.VITE_PLATFORM_FEE_RATE ?? 0.08);

const Marketplace = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [cart, setCart] = useState<CartItem[]>([]);
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  const { data: products, isLoading, isError } = useQuery<Product[]>({
    queryKey: ["products"],
    queryFn: listProducts,
  });

  // Initialize cart from localStorage once products are available
  useEffect(() => {
    try {
      const raw = localStorage.getItem("cart_items");
      if (raw && products && products.length > 0) {
        const parsed: { product_id: number; quantity: number }[] = JSON.parse(raw);
        const items: CartItem[] = parsed
          .map(ci => {
            const prod = products.find(p => p.id === ci.product_id);
            return prod ? { product: prod, quantity: ci.quantity } : null;
          })
          .filter(Boolean) as CartItem[];
        if (items.length) setCart(items);
      }
    } catch (e) {
      console.warn("Failed to load cart from storage", e);
    }
  }, [products]);

  // Persist cart to localStorage whenever it changes
  useEffect(() => {
    try {
      const minimal = cart.map(ci => ({
        product_id: ci.product.id,
        quantity: ci.quantity,
        name: ci.product.name,
        price: ci.product.price,
      }));
      localStorage.setItem("cart_items", JSON.stringify(minimal));
      // notify listeners (e.g., header) in same tab
      window.dispatchEvent(new CustomEvent("cart_updated"));
    } catch (e) {
      console.warn("Failed to persist cart", e);
    }
  }, [cart]);

  const addToCart = (product: Product) => {
    setCart((prevCart) => {
      const existingItem = prevCart.find((item) => item.product.id === product.id);
      if (existingItem) {
        return prevCart.map((item) =>
          item.product.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      return [...prevCart, { product, quantity: 1 }];
    });
    toast({ title: "Added to cart", description: `${product.name} has been added to your cart.` });
  };

  const handleBuyNow = async (product: Product) => {
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
      if (msg.includes("401")) {
        toast({ title: "Sign in required", description: "Please sign in to continue.", variant: "destructive" });
        const redirect = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/auth?redirect=${redirect}`;
      } else {
        toast({ title: "Checkout Error", description: msg, variant: "destructive" });
      }
    } finally {
      setIsCheckingOut(false);
    }
  };

  const updateCartQuantity = (productId: number, quantity: number) => {
    setCart((prevCart) =>
      prevCart
        .map((item) => (item.product.id === productId ? { ...item, quantity } : item))
        .filter((item) => item.quantity > 0)
    );
  };

  const removeFromCart = (productId: number) => {
    setCart((prevCart) => prevCart.filter((item) => item.product.id !== productId));
  };

  const cartTotal = useMemo(() => {
    return cart.reduce((total, item) => total + item.product.price * item.quantity, 0);
  }, [cart]);

  const platformFee = useMemo(() => {
    return Math.round(cartTotal * PLATFORM_FEE_RATE * 100) / 100;
  }, [cartTotal]);

  const grandTotal = useMemo(() => cartTotal + platformFee, [cartTotal, platformFee]);

  const handleCheckout = async () => {
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
      if (msg.includes("401")) {
        toast({ title: "Sign in required", description: "Please sign in to checkout.", variant: "destructive" });
        // Preserve current page for return after auth if desired
        const redirect = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/auth?redirect=${redirect}`;
      } else {
        toast({ title: "Checkout Error", description: msg, variant: "destructive" });
      }
    } finally {
      setIsCheckingOut(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link to="/dashboard">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
          <div className="flex-1">
            <h1 className="text-3xl font-bold">AgriMarketplace</h1>
            <p className="text-muted-foreground">Direct connection between farmers and buyers</p>
          </div>
          <Drawer>
            <DrawerTrigger asChild>
              <Button variant="outline">
                <ShoppingCart className="h-4 w-4 mr-2" />
                Cart ({cart.reduce((sum, item) => sum + item.quantity, 0)})
              </Button>
            </DrawerTrigger>
            <DrawerContent>
              <DrawerHeader>
                <DrawerTitle>Your Cart</DrawerTitle>
              </DrawerHeader>
              <div className="px-4 space-y-4">
                {cart.length === 0 ? (
                  <p className="text-muted-foreground text-center py-8">Your cart is empty.</p>
                ) : (
                  cart.map(item => (
                    <div key={item.product.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold">{item.product.name}</p>
                        <p className="text-sm text-muted-foreground">${item.product.price.toFixed(2)}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button size="icon" variant="ghost" onClick={() => updateCartQuantity(item.product.id, item.quantity - 1)}>
                          <Minus className="h-4 w-4" />
                        </Button>
                        <span>{item.quantity}</span>
                        <Button size="icon" variant="ghost" onClick={() => updateCartQuantity(item.product.id, item.quantity + 1)}>
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
                    <span>Subtotal</span>
                    <span>${cartTotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Platform fee ({(PLATFORM_FEE_RATE * 100).toFixed(0)}%)</span>
                    <span>${platformFee.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center pt-2">
                    <span className="font-bold text-lg">Total</span>
                    <span className="font-bold text-lg">${grandTotal.toFixed(2)}</span>
                  </div>
                </div>
                <Button onClick={handleCheckout} disabled={cart.length === 0 || isCheckingOut}>
                  {isCheckingOut ? "Processing..." : "Checkout"}
                </Button>
                <DrawerClose asChild>
                  <Button variant="outline">Continue Shopping</Button>
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
              placeholder="Search products, farmers, or locations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
        </div>

        {/* Marketplace Tabs */}
        <Tabs defaultValue="browse" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="browse">Browse Products</TabsTrigger>
            <TabsTrigger value="mylistings" asChild>
              <Link to="/dashboard">My Listings</Link>
            </TabsTrigger>
            <TabsTrigger value="orders" asChild>
              <Link to="/orders">Orders</Link>
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
              <h2 className="text-2xl font-bold mb-4">Products</h2>
              {isLoading && <p className="text-muted-foreground">Loading products...</p>}
              {isError && <p className="text-red-600">Failed to load products.</p>}
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
                    .map((product) => (
                    <Card key={product.id} className="hover:shadow-lg transition-shadow">
                      <div className="aspect-video bg-muted rounded-t-lg flex items-center justify-center">
                        <img src="/placeholder.svg" alt={product.name} className="w-full h-full object-cover rounded-t-lg" />
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
                              ${typeof product.price === 'number' ? product.price.toFixed(2) : parseFloat(product.price).toFixed(2)}
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
                            <Button className="flex-1" onClick={() => addToCart(product)} disabled={Number(product.quantity ?? 0) <= 0}>
                              Add to Cart
                            </Button>
                            <Button className="flex-1" variant="secondary" onClick={() => handleBuyNow(product)} disabled={Number(product.quantity ?? 0) <= 0 || isCheckingOut}>
                              {isCheckingOut ? "Processing..." : "Buy Now"}
                            </Button>
                            <Button variant="outline" onClick={() => toast({ title: "Contact seller", description: "Messaging coming soon." })}>Contact</Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
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
              <div className="text-2xl font-bold text-primary">1,247</div>
              <div className="text-sm text-muted-foreground">Active Farmers</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-primary">3,892</div>
              <div className="text-sm text-muted-foreground">Products Listed</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-primary">$2.1M</div>
              <div className="text-sm text-muted-foreground">Total Sales</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-primary">98.2%</div>
              <div className="text-sm text-muted-foreground">Satisfaction Rate</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Marketplace;