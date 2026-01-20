import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { Sprout, Package, ShoppingCart, DollarSign, Plus, Edit, Trash2, Shield, Users, Settings, Ban, Search, AlertTriangle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useToast } from "@/components/ui/use-toast";
import { secureStorage } from "@/lib/security";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { listAllUsers, updateUserRole, suspendUser, deleteUserById } from "@/lib/api";
import { useTranslation } from "@/i18n/config";

export default function Dashboard() {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [deleteProductId, setDeleteProductId] = useState<number | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState('all');

  const isFarmer = user?.role?.toUpperCase() === 'FARMER';
  const isBuyer = user?.role?.toUpperCase() === 'BUYER';
  const isAdmin = user?.role?.toUpperCase() === 'ADMIN';
  const isMentor = user?.role?.toUpperCase() === 'MENTOR';
  const isTrader = user?.role?.toUpperCase() === 'TRADER';
  const isPolicyMaker = user?.role?.toUpperCase() === 'POLICY_MAKER';

  // Fetch users for admin
  const { data: users, refetch: refetchUsers, isLoading: loadingUsers, error: usersError } = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => {
      if (!isAdmin) return [];
      try {
        console.log('Fetching users as admin...');
        const result = await listAllUsers();
        console.log('Users fetched successfully:', result);
        return result;
      } catch (err: any) {
        console.error('Error fetching users:', err);
        console.error('Error response:', err.response);
        toast({
          title: "Error Loading Users",
          description: err.response?.data?.detail || err.message || "Failed to load users",
          variant: "destructive",
        });
        throw err;
      }
    },
    enabled: isAdmin,
    retry: 1,
  });

  // Fetch farmer's products
  const { data: products, refetch: refetchProducts } = useQuery({
    queryKey: ['farmer-products', user?.email],
    queryFn: async () => {
      console.log('Fetching products for:', user?.email, 'Role:', user?.role);

      if (!isFarmer && !isAdmin) {
        console.log('Not farmer or admin, returning empty');
        return [];
      }

      const accessToken = secureStorage.get<string>('access_token');
      const response = await fetch('/api/marketplace/products', {
        headers: accessToken ? { 'Authorization': `Bearer ${accessToken}` } : undefined,
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
        headers: accessToken ? { 'Authorization': `Bearer ${accessToken}` } : undefined,
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

  const handleToggleStatus = async (productId: number, currentStatus: string) => {
    try {
      const token = secureStorage.get<string>('access_token');
      console.log('Token retrieved:', token ? 'exists' : 'missing');
      if (!token) {
        toast({
          title: "Error",
          description: "Please sign in to update products",
          variant: "destructive",
        });
        return;
      }

      const newStatus = currentStatus === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
      console.log('Updating product', productId, 'to', newStatus);

      const response = await fetch(`/api/marketplace/products/${productId}/status?status=${newStatus}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to update product status');
      }

      toast({
        title: "Success",
        description: `Product ${newStatus === 'ACTIVE' ? 'activated' : 'deactivated'} successfully`,
      });

      refetchProducts();
    } catch (error) {
      console.error('Status update error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update product status",
        variant: "destructive",
      });
    }
  };

  const handleDeleteProduct = async (productId: number) => {
    try {
      const token = secureStorage.get<string>('access_token');
      if (!token) {
        toast({
          title: "Error",
          description: "Please sign in to delete products",
          variant: "destructive",
        });
        return;
      }

      // Get CSRF token
      const csrfResponse = await fetch('/api/auth/csrf-token', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : undefined,
      });
      const { csrf_token } = await csrfResponse.json();

      const response = await fetch(`/api/marketplace/products/${productId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-CSRF-Token': csrf_token,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to delete product');
      }

      toast({
        title: "Success",
        description: "Product deleted successfully",
      });

      refetchProducts();
    } catch (error) {
      console.error('Delete error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to delete product",
        variant: "destructive",
      });
    } finally {
      setDeleteProductId(null);
    }
  };

  const handleUpdateUserRole = async (userId: number, newRole: string) => {
    try {
      await updateUserRole(userId, newRole);
      toast({
        title: "Success",
        description: "User role updated successfully",
      });
      refetchUsers();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update user role",
        variant: "destructive",
      });
    }
  };

  const handleSuspendUser = async (userId: number) => {
    if (!confirm('Are you sure you want to suspend this user?')) return;

    try {
      await suspendUser(userId);
      toast({
        title: "Success",
        description: "User suspended successfully",
      });
      refetchUsers();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to suspend user",
        variant: "destructive",
      });
    }
  };

  const handleDeleteUser = async () => {
    if (!userToDelete) return;

    try {
      await deleteUserById(userToDelete.id);
      toast({
        title: "User Deleted",
        description: `${userToDelete.email} has been permanently deleted`,
      });
      refetchUsers();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to delete user",
        variant: "destructive",
      });
    } finally {
      setDeleteDialogOpen(false);
      setUserToDelete(null);
    }
  };

  const filteredUsers = users?.filter((u: any) => {
    const matchesSearch = u.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = selectedRole === 'all' || u.role?.toLowerCase() === selectedRole.toLowerCase();
    return matchesSearch && matchesRole;
  }) || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('dashboard.title')}</h1>
          <p className="text-muted-foreground">
            {t('common.welcome')}, {user?.email}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => navigate('/profile')}>
            {t('profile.title')}
          </Button>
          <Button onClick={() => logout()} variant="outline">
            {t('common.logout')}
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
                {t('admin.title')}
              </Button>
              <Button onClick={() => navigate('/users')} variant="outline" className="w-full justify-start gap-2">
                <Users className="h-4 w-4" />
                {t('admin.userManagement')}
              </Button>
              <Button onClick={() => navigate('/marketplace')} variant="outline" className="w-full justify-start gap-2">
                <Package className="h-4 w-4" />
                {t('marketplace.title')}
              </Button>
              <Button onClick={() => navigate('/orders')} variant="outline" className="w-full justify-start gap-2">
                <ShoppingCart className="h-4 w-4" />
                {t('orders.title')}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Admin User List */}
      {isAdmin && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>User Management</CardTitle>
                <CardDescription>View and manage all platform users</CardDescription>
              </div>
              <Badge variant="secondary">{filteredUsers.length} users</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 mb-6">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by email or name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={selectedRole} onValueChange={setSelectedRole}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Roles</SelectItem>
                  <SelectItem value="buyer">Buyers</SelectItem>
                  <SelectItem value="farmer">Farmers</SelectItem>
                  <SelectItem value="mentor">Mentors</SelectItem>
                  <SelectItem value="trader">Traders</SelectItem>
                  <SelectItem value="policy_maker">Policy Makers</SelectItem>
                  <SelectItem value="admin">Admins</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {loadingUsers ? (
              <div className="text-center py-8 text-muted-foreground">Loading users...</div>
            ) : usersError ? (
              <div className="text-center py-8">
                <div className="text-red-600 font-medium mb-2">Failed to load users</div>
                <p className="text-sm text-muted-foreground mb-4">
                  {usersError instanceof Error ? usersError.message : 'An error occurred'}
                </p>
                <Button onClick={() => refetchUsers()} variant="outline">
                  Retry
                </Button>
              </div>
            ) : (
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-muted/50">
                      <TableHead className="w-16">ID</TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUsers.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                          No users found
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredUsers.map((userItem: any) => (
                        <TableRow key={userItem.id} className="hover:bg-muted/30">
                          <TableCell className="font-mono text-sm text-muted-foreground">{userItem.id}</TableCell>
                          <TableCell>
                            <div>
                              <div className="font-medium">{userItem.email}</div>
                              {userItem.name && <div className="text-sm text-muted-foreground">{userItem.name}</div>}
                            </div>
                          </TableCell>
                          <TableCell>
                            <Select
                              value={userItem.role}
                              onValueChange={(value) => handleUpdateUserRole(userItem.id, value)}
                              disabled={userItem.id === user?.id}
                            >
                              <SelectTrigger className="w-32">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="BUYER">
                                  <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-blue-500" />
                                    Buyer
                                  </div>
                                </SelectItem>
                                <SelectItem value="FARMER">
                                  <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-green-500" />
                                    Farmer
                                  </div>
                                </SelectItem>
                                <SelectItem value="MENTOR">
                                  <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-yellow-500" />
                                    Mentor
                                  </div>
                                </SelectItem>
                                <SelectItem value="TRADER">
                                  <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-orange-500" />
                                    Trader
                                  </div>
                                </SelectItem>
                                <SelectItem value="POLICY_MAKER">
                                  <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-teal-500" />
                                    Policy Maker
                                  </div>
                                </SelectItem>
                                <SelectItem value="ADMIN">
                                  <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-purple-500" />
                                    Admin
                                  </div>
                                </SelectItem>
                              </SelectContent>
                            </Select>
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={userItem.status === 'ACTIVE' ? 'default' : 'destructive'}
                              className="font-medium"
                            >
                              {userItem.status || 'ACTIVE'}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex justify-end gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleSuspendUser(userItem.id)}
                                disabled={userItem.id === user?.id}
                                title="Suspend user"
                              >
                                <Ban className="h-4 w-4 mr-1" />
                                Suspend
                              </Button>
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => {
                                  setUserToDelete(userItem);
                                  setDeleteDialogOpen(true);
                                }}
                                disabled={userItem.id === user?.id}
                                title="Delete user permanently"
                              >
                                <Trash2 className="h-4 w-4 mr-1" />
                                Delete
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            )}
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
                <div className="text-2xl font-bold">৳0.00</div>
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
                <div className="text-2xl font-bold">৳0.00</div>
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
                  {products.map((product: any) => {
                    const images = (() => {
                      try {
                        if (!product.images) return [];
                        if (Array.isArray(product.images)) return product.images;
                        if (typeof product.images === 'string') {
                          if (product.images.startsWith('[') && product.images.endsWith(']')) {
                            const parsed = JSON.parse(product.images);
                            return Array.isArray(parsed) ? parsed : [product.images.replace(/"/g, '')];
                          }
                          return [product.images.replace(/"/g, '').replace(/[\[\]]/g, '')];
                        }
                        return [];
                      } catch (e) {
                        console.error("Error parsing images:", e);
                        return [];
                      }
                    })();

                    return (
                      <div
                        key={product.id}
                        className="flex items-center gap-4 p-4 border rounded-lg hover:bg-accent"
                      >
                        {images.length > 0 && (
                          <div className="relative">
                            <img
                              src={images[0]}
                              alt={product.name}
                              className="w-20 h-20 object-cover rounded"
                              onError={(e) => {
                                e.currentTarget.style.display = 'none';
                              }}
                            />
                            {images.length > 1 && (
                              <div className="absolute -bottom-1 -right-1 bg-primary text-primary-foreground text-xs px-1.5 py-0.5 rounded-full">
                                +{images.length - 1}
                              </div>
                            )}
                          </div>
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
                            <span className={`px-2 py-1 rounded-full text-xs ${product.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                              }`}>
                              {product.status || 'Active'}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant={product.status === 'ACTIVE' ? 'default' : 'secondary'}
                            size="sm"
                            onClick={() => handleToggleStatus(product.id, product.status)}
                          >
                            {product.status === 'ACTIVE' ? 'Active' : 'Inactive'}
                          </Button>
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
                            onClick={() => setDeleteProductId(product.id)}
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
                      </div>
                    );
                  })}
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

      {/* Delete Product Confirmation Dialog */}
      <AlertDialog open={deleteProductId !== null} onOpenChange={() => setDeleteProductId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Product</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this product? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteProductId && handleDeleteProduct(deleteProductId)}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete User Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete User Permanently?</AlertDialogTitle>
            <AlertDialogDescription className="space-y-3">
              <p>
                You are about to permanently delete <strong>{userToDelete?.email}</strong>.
              </p>
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 space-y-2">
                <p className="font-medium text-red-900 text-sm">This action cannot be undone. This will:</p>
                <ul className="text-sm text-red-800 space-y-1 ml-4 list-disc">
                  <li>Permanently delete the user account</li>
                  <li>Remove all associated data</li>
                  <li>Delete their products and listings</li>
                  <li>Cancel any pending orders</li>
                </ul>
              </div>
              <p className="text-sm">
                Consider using <strong>Suspend</strong> instead if you want to temporarily disable the account.
              </p>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteUser}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Permanently
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
