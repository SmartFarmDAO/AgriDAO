import { useState } from 'react';
import { useAuth } from '@/hooks/use-auth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Users, ShoppingCart, Package, DollarSign,
  Search, Trash2, Ban, CheckCircle, TrendingUp,
  Activity, BarChart3, Shield, AlertTriangle, UserX, Bot
} from 'lucide-react';
import { AgentOrchestration } from '@/components/AgentOrchestration';
import { useToast } from '@/components/ui/use-toast';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { listAllUsers, updateUserRole, suspendUser, deleteUserById } from '@/lib/api';
import { secureStorage } from '@/lib/security';

export default function AdminDashboard() {
  const { user: currentUser, logout } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState('all');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<any>(null);

  // Check if user is admin
  if (currentUser?.role?.toUpperCase() !== 'ADMIN') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-100 rounded-full">
                <Shield className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <CardTitle>Access Denied</CardTitle>
                <CardDescription>Admin privileges required</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              You don't have permission to access the admin dashboard.
            </p>
            <Button onClick={() => navigate('/dashboard')} className="w-full">
              Go to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Fetch users
  const { data: users, refetch: refetchUsers, isLoading: loadingUsers, error: usersError } = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => {
      console.log('Fetching users...');
      console.log('Access token:', secureStorage.get('access_token'));
      try {
        const result = await listAllUsers();
        console.log('Users fetched:', result);
        return result;
      } catch (err: any) {
        console.error('Error fetching users:', err);
        console.error('Error response:', err.response);
        console.error('Error message:', err.message);
        throw err;
      }
    },
  });

  // Fetch products
  const { data: products, refetch: refetchProducts, isLoading: loadingProducts } = useQuery({
    queryKey: ['admin-products'],
    queryFn: async () => {
      const response = await fetch('/api/marketplace/products', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch products');
      return response.json();
    },
  });

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

  const handleToggleProductStatus = async (productId: number, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';

      const response = await fetch(`/api/marketplace/products/${productId}/status?status=${newStatus}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to update product status');

      toast({
        title: "Success",
        description: `Product ${newStatus === 'ACTIVE' ? 'activated' : 'deactivated'} successfully`,
      });

      refetchProducts();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update product status",
        variant: "destructive",
      });
    }
  };

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
        description: error instanceof Error ? error.message : "Failed to delete product",
        variant: "destructive",
      });
    }
  };

  const handleExportUsers = () => {
    if (!users || users.length === 0) return;
    const csv = [
      ['ID', 'Email', 'Name', 'Role', 'Status'].join(','),
      ...users.map((u: any) => [u.id, u.email, u.name || '', u.role, u.status || 'ACTIVE'].join(','))
    ].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `users-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    toast({ title: "Success", description: "Users exported" });
  };

  // Show error if users failed to load
  if (usersError) {
    console.error('Users error:', usersError);
  }

  const filteredUsers = users?.filter((u: any) => {
    const matchesSearch = u.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = selectedRole === 'all' || u.role?.toLowerCase() === selectedRole.toLowerCase();
    return matchesSearch && matchesRole;
  }) || [];

  const stats = {
    totalUsers: users?.length || 0,
    farmers: users?.filter((u: any) => u.role?.toUpperCase() === 'FARMER').length || 0,
    buyers: users?.filter((u: any) => u.role?.toUpperCase() === 'BUYER').length || 0,
    admins: users?.filter((u: any) => u.role?.toUpperCase() === 'ADMIN').length || 0,
    totalProducts: products?.length || 0,
    activeProducts: products?.filter((p: any) => p.status === 'ACTIVE').length || 0,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Shield className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
              <p className="text-muted-foreground">
                Platform management and analytics
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => navigate('/dashboard')}>
            User Dashboard
          </Button>
          <Button variant="outline" onClick={logout}>
            Sign Out
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalUsers}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {stats.farmers} farmers • {stats.buyers} buyers • {stats.admins} admins
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Products</CardTitle>
            <Package className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalProducts}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {stats.activeProducts} active listings
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Orders</CardTitle>
            <ShoppingCart className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground mt-1">
              0 pending • 0 completed
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">৳0.00</div>
            <p className="text-xs text-muted-foreground mt-1">
              All time revenue
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="users" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="users" className="gap-2">
            <Users className="h-4 w-4" />
            Users
          </TabsTrigger>
          <TabsTrigger value="products" className="gap-2">
            <Package className="h-4 w-4" />
            Products
          </TabsTrigger>
          <TabsTrigger value="orders" className="gap-2">
            <ShoppingCart className="h-4 w-4" />
            Orders
          </TabsTrigger>
          <TabsTrigger value="agents" className="gap-2">
            <Bot className="h-4 w-4" />
            Agents
          </TabsTrigger>
          <TabsTrigger value="analytics" className="gap-2">
            <BarChart3 className="h-4 w-4" />
            Analytics
          </TabsTrigger>
        </TabsList>

        {/* User Management Tab */}
        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>User Management</CardTitle>
                  <CardDescription>Manage user accounts, roles, and permissions</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">{filteredUsers.length} users</Badge>
                  <Button variant="outline" size="sm" onClick={handleExportUsers}>
                    Export CSV
                  </Button>
                </div>
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
                    <SelectItem value="admin">Admins</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {loadingUsers ? (
                <div className="text-center py-8 text-muted-foreground">Loading users...</div>
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
                        filteredUsers.map((user: any) => (
                          <TableRow key={user.id} className="hover:bg-muted/30">
                            <TableCell className="font-mono text-sm text-muted-foreground">{user.id}</TableCell>
                            <TableCell>
                              <div>
                                <div className="font-medium">{user.email}</div>
                                {user.name && <div className="text-sm text-muted-foreground">{user.name}</div>}
                              </div>
                            </TableCell>
                            <TableCell>
                              <Select
                                value={user.role}
                                onValueChange={(value) => handleUpdateUserRole(user.id, value)}
                                disabled={user.id === currentUser?.id}
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
                                variant={user.status === 'ACTIVE' ? 'default' : 'destructive'}
                                className="font-medium"
                              >
                                {user.status || 'ACTIVE'}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div className="flex justify-end gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleSuspendUser(user.id)}
                                  disabled={user.id === currentUser?.id}
                                  title="Suspend user"
                                >
                                  <Ban className="h-4 w-4 mr-1" />
                                  Suspend
                                </Button>
                                <Button
                                  variant="destructive"
                                  size="sm"
                                  onClick={() => {
                                    setUserToDelete(user);
                                    setDeleteDialogOpen(true);
                                  }}
                                  disabled={user.id === currentUser?.id}
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
        </TabsContent>

        {/* Product Moderation Tab */}
        <TabsContent value="products" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Product Moderation</CardTitle>
                  <CardDescription>Review and manage all product listings</CardDescription>
                </div>
                <Badge variant="secondary">{products?.length || 0} products</Badge>
              </div>
            </CardHeader>
            <CardContent>
              {loadingProducts ? (
                <div className="text-center py-8 text-muted-foreground">Loading products...</div>
              ) : (
                <div className="border rounded-lg">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-16">ID</TableHead>
                        <TableHead>Product Name</TableHead>
                        <TableHead>Category</TableHead>
                        <TableHead>Price</TableHead>
                        <TableHead>Farmer</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {!products || products.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                            No products found
                          </TableCell>
                        </TableRow>
                      ) : (
                        products.map((product: any) => (
                          <TableRow key={product.id}>
                            <TableCell className="font-mono text-sm">{product.id}</TableCell>
                            <TableCell className="font-medium">{product.name}</TableCell>
                            <TableCell>{product.category}</TableCell>
                            <TableCell className="font-mono">
                              ${typeof product.price === 'number' ? product.price.toFixed(2) : parseFloat(product.price).toFixed(2)}
                            </TableCell>
                            <TableCell>Farmer #{product.farmer_id}</TableCell>
                            <TableCell>
                              <Badge variant={product.status === 'ACTIVE' ? 'default' : 'secondary'}>
                                {product.status}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div className="flex justify-end gap-2">
                                <Button
                                  variant={product.status === 'ACTIVE' ? 'default' : 'secondary'}
                                  size="sm"
                                  onClick={() => handleToggleProductStatus(product.id, product.status)}
                                >
                                  {product.status === 'ACTIVE' ? 'Active' : 'Inactive'}
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleDeleteProduct(product.id)}
                                >
                                  <Trash2 className="h-4 w-4" />
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
        </TabsContent>

        {/* Orders Tab */}
        <TabsContent value="orders" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Order Management</CardTitle>
              <CardDescription>View and manage all platform orders</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <ShoppingCart className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No orders yet</h3>
                <p className="text-muted-foreground">
                  Orders will appear here once customers start purchasing
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Agent Orchestration Tab */}
        <TabsContent value="agents" className="space-y-6">
          <AgentOrchestration />
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* User Growth */}
            <Card>
              <CardHeader>
                <CardTitle>User Growth</CardTitle>
                <CardDescription>Platform user statistics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Total Users</span>
                    <span className="text-2xl font-bold">{stats.totalUsers}</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Farmers</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-500"
                            style={{ width: `${stats.totalUsers ? (stats.farmers / stats.totalUsers * 100) : 0}%` }}
                          />
                        </div>
                        <span className="font-medium w-8 text-right">{stats.farmers}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Buyers</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500"
                            style={{ width: `${stats.totalUsers ? (stats.buyers / stats.totalUsers * 100) : 0}%` }}
                          />
                        </div>
                        <span className="font-medium w-8 text-right">{stats.buyers}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Admins</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-purple-500"
                            style={{ width: `${stats.totalUsers ? (stats.admins / stats.totalUsers * 100) : 0}%` }}
                          />
                        </div>
                        <span className="font-medium w-8 text-right">{stats.admins}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Product Statistics */}
            <Card>
              <CardHeader>
                <CardTitle>Product Statistics</CardTitle>
                <CardDescription>Marketplace inventory overview</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Total Products</span>
                    <span className="text-2xl font-bold">{stats.totalProducts}</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Active Listings</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-500"
                            style={{ width: `${stats.totalProducts ? (stats.activeProducts / stats.totalProducts * 100) : 0}%` }}
                          />
                        </div>
                        <span className="font-medium w-8 text-right">{stats.activeProducts}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Inactive</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gray-400"
                            style={{ width: `${stats.totalProducts ? ((stats.totalProducts - stats.activeProducts) / stats.totalProducts * 100) : 0}%` }}
                          />
                        </div>
                        <span className="font-medium w-8 text-right">{stats.totalProducts - stats.activeProducts}</span>
                      </div>
                    </div>
                    <div className="flex justify-between pt-2 border-t">
                      <span className="text-muted-foreground">Avg per Farmer</span>
                      <span className="font-medium">{stats.farmers ? (stats.totalProducts / stats.farmers).toFixed(1) : 0}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Category Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Product Categories</CardTitle>
                <CardDescription>Distribution by category</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {products && (() => {
                    const categories = products.reduce((acc: any, p: any) => {
                      acc[p.category] = (acc[p.category] || 0) + 1;
                      return acc;
                    }, {});
                    return Object.entries(categories)
                      .sort(([, a]: any, [, b]: any) => b - a)
                      .slice(0, 5)
                      .map(([category, count]: any) => (
                        <div key={category} className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">{category}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-blue-500"
                                style={{ width: `${(count / stats.totalProducts * 100)}%` }}
                              />
                            </div>
                            <span className="font-medium w-6 text-right">{count}</span>
                          </div>
                        </div>
                      ));
                  })()}
                  {(!products || products.length === 0) && (
                    <p className="text-sm text-muted-foreground text-center py-4">No products yet</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Additional Analytics */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Platform Activity</CardTitle>
                <CardDescription>Recent platform metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium">User Engagement</p>
                      <p className="text-xs text-muted-foreground">Active users today</p>
                    </div>
                    <div className="text-2xl font-bold text-blue-600">-</div>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium">New Listings</p>
                      <p className="text-xs text-muted-foreground">Products added this week</p>
                    </div>
                    <div className="text-2xl font-bold text-green-600">-</div>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium">Pending Actions</p>
                      <p className="text-xs text-muted-foreground">Items requiring review</p>
                    </div>
                    <div className="text-2xl font-bold text-orange-600">0</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>System Health</CardTitle>
                <CardDescription>Platform performance metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Database Status</span>
                      <Badge variant="default">Healthy</Badge>
                    </div>
                    <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500" style={{ width: '95%' }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">API Response Time</span>
                      <span className="text-sm text-muted-foreground">~50ms</span>
                    </div>
                    <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500" style={{ width: '85%' }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Storage Usage</span>
                      <span className="text-sm text-muted-foreground">12% used</span>
                    </div>
                    <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-purple-500" style={{ width: '12%' }} />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-red-100 rounded-full">
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              <AlertDialogTitle>Delete User Permanently?</AlertDialogTitle>
            </div>
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
