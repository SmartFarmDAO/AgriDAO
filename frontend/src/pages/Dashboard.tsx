import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { Sprout, Package, ShoppingCart, DollarSign, Plus, Edit, Trash2, Shield, Users, Settings } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useToast } from "@/components/ui/use-toast";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const isFarmer = user?.role?.toUpperCase() === 'FARMER';
  const isBuyer = user?.role?.toUpperCase() === 'BUYER';
  const isAdmin = user?.role?.toUpperCase() === 'ADMIN';

  // Fetch farmer's products
  const { data: products, refetch: refetchProducts } = useQuery({
    queryKey: ['farmer-products', user?.email],
    queryFn: async () => {
      console.log('Fetching products for:', user?.email, 'Role:', user?.role);
      
      if (!isFarmer && !isAdmin) {
        console.log('Not farmer or admin, returning empty');
        return [];
      }
      
      const response = await fetch('/api/marketplace/products', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      if (!response.ok) {
        console.log('Products fetch failed');
        return [];
      }
      const allProducts = await response.json();
      console.log('All products:', allProducts);
      
      // For admins, show all products
      if (isAdmin) {
        console.log('Admin user, showing all products');
        return allProducts;
      }
      
      // For farmers, get their farmer record and filter products
      const farmersResponse = await fetch('/api/farmers/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!farmersResponse.ok) {
        console.log('Farmers fetch failed');
        return [];
      }
      const allFarmers = await farmersResponse.json();
      console.log('All farmers:', allFarmers);
      
      const myFarmer = allFarmers.find((f: any) => f.email === user?.email);
      console.log('My farmer record:', myFarmer);
      
      if (!myFarmer) {
        console.log('No farmer record found for:', user?.email);
        return [];
      }
      
      const myProducts = allProducts.filter((p: any) => p.farmer_id === myFarmer.id);
      console.log('My products:', myProducts);
      
      return myProducts;
    },
    enabled: (isFarmer || isAdmin) && !!user?.email,
  });

  const handleDeleteProduct = async (productId: number) => {
    if (!confirm('Are you sure you want to delete this product?')) return;
    
    try {
      const response = await fetch(`/api/marketplace/products/${productId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) throw new Error('Failed to delete product');
      
      toast({
        title: "Success",
        description: "Product deleted successfully",
      });
      
      refetchProducts();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete product",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.email}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => navigate('/profile')}>
            View Profile
          </Button>
          <Button onClick={() => logout()} variant="outline">
            Sign Out
          </Button>
        </div>
      </div>

      {/* Admin Quick Access Panel */}
      {isAdmin && (
        <Card className="border-purple-200 bg-purple-50">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Shield className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <CardTitle>Administrator Access</CardTitle>
                <CardDescription>
                  Manage platform users, products, and settings
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
              <Button onClick={() => navigate('/admin')} className="w-full justify-start gap-2">
                <Settings className="h-4 w-4" />
                Admin Dashboard
              </Button>
              <Button onClick={() => navigate('/users')} variant="outline" className="w-full justify-start gap-2">
                <Users className="h-4 w-4" />
                User Management
              </Button>
              <Button onClick={() => navigate('/marketplace')} variant="outline" className="w-full justify-start gap-2">
                <Package className="h-4 w-4" />
                Browse Marketplace
              </Button>
              <Button onClick={() => navigate('/orders')} variant="outline" className="w-full justify-start gap-2">
                <ShoppingCart className="h-4 w-4" />
                Order Management
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Become a Farmer CTA for Buyers */}
      {isBuyer && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Sprout className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <CardTitle>Become a Farmer</CardTitle>
                <CardDescription>
                  Start selling your products on our marketplace
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Join thousands of farmers selling directly to consumers. List your products, manage orders, and grow your business.
            </p>
            <Button onClick={() => navigate('/onboarding')} className="w-full sm:w-auto">
              Register as Farmer
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Farmer Dashboard */}
      {(isFarmer || isAdmin) && (
        <>
          {/* Quick Stats */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Products</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{products?.length || 0}</div>
                <p className="text-xs text-muted-foreground">
                  Active listings
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Sales</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">$0.00</div>
                <p className="text-xs text-muted-foreground">
                  This month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pending Orders</CardTitle>
                <ShoppingCart className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0</div>
                <p className="text-xs text-muted-foreground">
                  Awaiting fulfillment
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">$0.00</div>
                <p className="text-xs text-muted-foreground">
                  All time
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Manage your farm and products</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-3">
              <Button onClick={() => navigate('/products/new')} className="gap-2">
                <Plus className="h-4 w-4" />
                Add New Product
              </Button>
              <Button variant="outline" onClick={() => navigate('/orders')}>
                View Orders
              </Button>
              <Button variant="outline" onClick={() => navigate('/marketplace')}>
                Browse Marketplace
              </Button>
            </CardContent>
          </Card>

          {/* My Products */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>My Products</CardTitle>
                  <CardDescription>Manage your product listings</CardDescription>
                </div>
                <Button onClick={() => navigate('/products/new')} size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Product
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {!products || products.length === 0 ? (
                <div className="text-center py-12">
                  <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No products yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Start by adding your first product to the marketplace
                  </p>
                  <Button onClick={() => navigate('/products/new')}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Your First Product
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {products.map((product: any) => (
                    <div
                      key={product.id}
                      className="flex items-center gap-4 p-4 border rounded-lg hover:bg-accent"
                    >
                      {product.images && product.images.trim() && (
                        <img 
                          src={product.images.replace(/"/g, '')} 
                          alt={product.name}
                          className="w-20 h-20 object-cover rounded"
                          onError={(e) => {
                            console.error('Image failed to load:', product.images);
                            e.currentTarget.style.display = 'none';
                          }}
                        />
                      )}
                      <div className="flex-1">
                        <h4 className="font-semibold">{product.name}</h4>
                        <p className="text-sm text-muted-foreground">{product.category}</p>
                        <div className="flex items-center gap-4 mt-2 text-sm">
                          <span className="font-medium">
                            ${typeof product.price === 'number' ? product.price.toFixed(2) : parseFloat(product.price).toFixed(2)}
                          </span>
                          <span className="text-muted-foreground">
                            {product.quantity_available || 0} {product.unit || 'units'} available
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            product.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                          }`}>
                            {product.status || 'Active'}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/products/${product.id}/edit`)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteProduct(product.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Buyer Dashboard */}
      {isBuyer && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Recent Orders</CardTitle>
              <CardDescription>Your recent purchases</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">No orders yet</p>
              <Button className="mt-4 w-full" onClick={() => navigate('/marketplace')}>
                Browse Marketplace
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Favorites</CardTitle>
              <CardDescription>Your saved products</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">No favorites yet</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Links</CardTitle>
              <CardDescription>Navigate quickly</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" className="w-full" onClick={() => navigate('/marketplace')}>
                Browse Products
              </Button>
              <Button variant="outline" className="w-full" onClick={() => navigate('/orders')}>
                My Orders
              </Button>
              <Button variant="outline" className="w-full" onClick={() => navigate('/profile')}>
                Edit Profile
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
