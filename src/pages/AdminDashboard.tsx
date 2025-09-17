import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Users, ShoppingCart, Package, AlertTriangle, TrendingUp, 
  DollarSign, Activity, Search, Filter, MoreHorizontal,
  CheckCircle, XCircle, Clock, User, FileText, Settings,
  RefreshCw, Download, Eye, Edit, Trash2
} from 'lucide-react';
import { useAuth } from '@/hooks/use-auth';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/lib/api';

interface AdminStats {
  users: {
    total: number;
    active: number;
    farmers: number;
    buyers: number;
    new_this_month: number;
  };
  orders: {
    total: number;
    pending: number;
    completed: number;
    cancelled: number;
    today: number;
  };
  products: {
    total: number;
    active: number;
    out_of_stock: number;
    new_this_month: number;
  };
  disputes: {
    total: number;
    open: number;
    resolved: number;
    escalated: number;
  };
  revenue: {
    total: number;
    this_month: number;
    growth_rate: number;
  };
}

interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  status: string;
  created_at: string;
  last_login?: string;
}

interface Order {
  id: number;
  user_email: string;
  total: number;
  status: string;
  created_at: string;
  items_count: number;
}

interface Dispute {
  id: number;
  order_id: number;
  user_email: string;
  status: string;
  priority: number;
  created_at: string;
  subject: string;
}

const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [disputes, setDisputes] = useState<Dispute[]>([]);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [userFilter, setUserFilter] = useState('all');
  const [orderFilter, setOrderFilter] = useState('all');
  const [disputeFilter, setDisputeFilter] = useState('all');

  // Check admin permissions
  if (!user || user.role !== 'admin') {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="mx-auto h-12 w-12 text-yellow-500 mb-4" />
          <h2 className="text-lg font-semibold mb-2">Access Denied</h2>
          <p className="text-muted-foreground">You need admin privileges to access this page.</p>
        </div>
      </div>
    );
  }

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch dashboard stats
      const statsResponse = await apiClient.get('/admin/stats');
      setStats(statsResponse.data);

      // Fetch users
      const usersResponse = await apiClient.get('/admin/users', {
        params: { limit: 100 }
      });
      setUsers(usersResponse.data);

      // Fetch recent orders
      const ordersResponse = await apiClient.get('/admin/orders', {
        params: { limit: 50 }
      });
      setOrders(ordersResponse.data);

      // Fetch disputes
      const disputesResponse = await apiClient.get('/admin/disputes', {
        params: { limit: 50 }
      });
      setDisputes(disputesResponse.data);

    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load dashboard data',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUserAction = async (action: string, userId: number) => {
    try {
      switch (action) {
        case 'activate':
          await apiClient.put(`/admin/users/${userId}/status`, { status: 'active' });
          break;
        case 'suspend':
          await apiClient.put(`/admin/users/${userId}/status`, { status: 'suspended' });
          break;
        case 'delete':
          if (confirm('Are you sure you want to delete this user?')) {
            await apiClient.delete(`/admin/users/${userId}`);
          }
          break;
      }
      
      toast({
        title: 'Success',
        description: `User ${action}d successfully`
      });
      
      fetchDashboardData();
    } catch (error) {
      toast({
        title: 'Error',
        description: `Failed to ${action} user`,
        variant: 'destructive'
      });
    }
  };

  const handleOrderAction = async (action: string, orderId: number) => {
    try {
      switch (action) {
        case 'cancel':
          await apiClient.post(`/admin/orders/${orderId}/cancel`);
          break;
        case 'refund':
          await apiClient.post(`/admin/orders/${orderId}/refund`);
          break;
      }
      
      toast({
        title: 'Success',
        description: `Order ${action}ed successfully`
      });
      
      fetchDashboardData();
    } catch (error) {
      toast({
        title: 'Error',
        description: `Failed to ${action} order`,
        variant: 'destructive'
      });
    }
  };

  const handleDisputeAction = async (action: string, disputeId: number) => {
    try {
      await apiClient.put(`/admin/disputes/${disputeId}/status`, {
        status: action === 'resolve' ? 'resolved' : 'escalated'
      });
      
      toast({
        title: 'Success',
        description: `Dispute ${action}d successfully`
      });
      
      fetchDashboardData();
    } catch (error) {
      toast({
        title: 'Error',
        description: `Failed to ${action} dispute`,
        variant: 'destructive'
      });
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusBadge = (status: string, type: 'user' | 'order' | 'dispute' = 'user') => {
    const statusConfig = {
      user: {
        active: { variant: 'default' as const, color: 'bg-green-100 text-green-800' },
        inactive: { variant: 'secondary' as const, color: 'bg-gray-100 text-gray-800' },
        suspended: { variant: 'destructive' as const, color: 'bg-red-100 text-red-800' }
      },
      order: {
        pending: { variant: 'secondary' as const, color: 'bg-yellow-100 text-yellow-800' },
        processing: { variant: 'default' as const, color: 'bg-blue-100 text-blue-800' },
        completed: { variant: 'default' as const, color: 'bg-green-100 text-green-800' },
        cancelled: { variant: 'destructive' as const, color: 'bg-red-100 text-red-800' }
      },
      dispute: {
        open: { variant: 'destructive' as const, color: 'bg-red-100 text-red-800' },
        in_progress: { variant: 'secondary' as const, color: 'bg-yellow-100 text-yellow-800' },
        resolved: { variant: 'default' as const, color: 'bg-green-100 text-green-800' },
        escalated: { variant: 'destructive' as const, color: 'bg-orange-100 text-orange-800' }
      }
    };

    const config = statusConfig[type][status as keyof typeof statusConfig[typeof type]] || 
                   statusConfig[type].active;
    
    return (
      <Badge variant={config.variant} className={config.color}>
        {status}
      </Badge>
    );
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = userFilter === 'all' || user.role === userFilter || user.status === userFilter;
    return matchesSearch && matchesFilter;
  });

  const filteredOrders = orders.filter(order => {
    const matchesSearch = order.user_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         order.id.toString().includes(searchTerm);
    const matchesFilter = orderFilter === 'all' || order.status === orderFilter;
    return matchesSearch && matchesFilter;
  });

  const filteredDisputes = disputes.filter(dispute => {
    const matchesSearch = dispute.user_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         dispute.subject.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = disputeFilter === 'all' || dispute.status === disputeFilter;
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground">Manage users, orders, and platform operations</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={fetchDashboardData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.users.total.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                +{stats.users.new_this_month} this month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Orders</CardTitle>
              <ShoppingCart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.orders.total.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                {stats.orders.today} today
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Products</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.products.total.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                {stats.products.out_of_stock} out of stock
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Disputes</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.disputes.total}</div>
              <p className="text-xs text-muted-foreground">
                {stats.disputes.open} open
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(stats.revenue.total)}</div>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="h-3 w-3 mr-1" />
                {stats.revenue.growth_rate.toFixed(1)}% growth
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="orders">Orders</TabsTrigger>
          <TabsTrigger value="disputes">Disputes</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <Activity className="h-4 w-4 text-blue-500" />
                    <span className="text-sm">New user registered</span>
                    <span className="text-xs text-muted-foreground ml-auto">2m ago</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <ShoppingCart className="h-4 w-4 text-green-500" />
                    <span className="text-sm">Order #1234 completed</span>
                    <span className="text-xs text-muted-foreground ml-auto">5m ago</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <AlertTriangle className="h-4 w-4 text-orange-500" />
                    <span className="text-sm">New dispute opened</span>
                    <span className="text-xs text-muted-foreground ml-auto">10m ago</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>System Health</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Database</span>
                    <Badge variant="default" className="bg-green-100 text-green-800">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Healthy
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Redis Cache</span>
                    <Badge variant="default" className="bg-green-100 text-green-800">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Healthy
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Payment System</span>
                    <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                      <Clock className="h-3 w-3 mr-1" />
                      Slow
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="users" className="space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex space-x-2">
              <Input
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
              <Select value={userFilter} onValueChange={setUserFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Users</SelectItem>
                  <SelectItem value="farmer">Farmers</SelectItem>
                  <SelectItem value="buyer">Buyers</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="suspended">Suspended</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Joined</TableHead>
                  <TableHead>Last Login</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{user.name}</div>
                        <div className="text-sm text-muted-foreground">{user.email}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{user.role}</Badge>
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(user.status, 'user')}
                    </TableCell>
                    <TableCell>{formatDate(user.created_at)}</TableCell>
                    <TableCell>
                      {user.last_login ? formatDate(user.last_login) : 'Never'}
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleUserAction('activate', user.id)}
                          disabled={user.status === 'active'}
                        >
                          <CheckCircle className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleUserAction('suspend', user.id)}
                          disabled={user.status === 'suspended'}
                        >
                          <XCircle className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleUserAction('delete', user.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="orders" className="space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex space-x-2">
              <Input
                placeholder="Search orders..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
              <Select value={orderFilter} onValueChange={setOrderFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Orders</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="processing">Processing</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Order ID</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Items</TableHead>
                  <TableHead>Total</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredOrders.map((order) => (
                  <TableRow key={order.id}>
                    <TableCell>#{order.id}</TableCell>
                    <TableCell>{order.user_email}</TableCell>
                    <TableCell>{order.items_count} items</TableCell>
                    <TableCell>{formatCurrency(order.total)}</TableCell>
                    <TableCell>
                      {getStatusBadge(order.status, 'order')}
                    </TableCell>
                    <TableCell>{formatDate(order.created_at)}</TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleOrderAction('cancel', order.id)}
                          disabled={order.status === 'cancelled' || order.status === 'completed'}
                        >
                          <XCircle className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="disputes" className="space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex space-x-2">
              <Input
                placeholder="Search disputes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
              <Select value={disputeFilter} onValueChange={setDisputeFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Disputes</SelectItem>
                  <SelectItem value="open">Open</SelectItem>
                  <SelectItem value="in_progress">In Progress</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
                  <SelectItem value="escalated">Escalated</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Order</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredDisputes.map((dispute) => (
                  <TableRow key={dispute.id}>
                    <TableCell>#{dispute.id}</TableCell>
                    <TableCell>#{dispute.order_id}</TableCell>
                    <TableCell>{dispute.user_email}</TableCell>
                    <TableCell>{dispute.subject}</TableCell>
                    <TableCell>
                      <Badge variant={dispute.priority > 3 ? 'destructive' : 'secondary'}>
                        {dispute.priority === 5 ? 'Critical' : 
                         dispute.priority === 4 ? 'High' : 
                         dispute.priority === 3 ? 'Medium' : 'Low'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(dispute.status, 'dispute')}
                    </TableCell>
                    <TableCell>{formatDate(dispute.created_at)}</TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDisputeAction('resolve', dispute.id)}
                          disabled={dispute.status === 'resolved'}
                        >
                          <CheckCircle className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDisputeAction('escalate', dispute.id)}
                          disabled={dispute.status === 'escalated'}
                        >
                          <AlertTriangle className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Analytics Dashboard</CardTitle>
              <CardDescription>
                Detailed analytics and reporting are available in the dedicated analytics section.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button>
                <FileText className="h-4 w-4 mr-2" />
                Go to Analytics
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminDashboard;