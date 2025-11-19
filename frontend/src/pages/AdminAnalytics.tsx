import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DatePickerWithRange } from '@/components/ui/date-range-picker';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  Loader2, Download, RefreshCw, TrendingUp, TrendingDown, Users, 
  ShoppingCart, DollarSign, Package, BarChart2, PieChart as PieChartIcon,
  LineChart as LineChartIcon, Activity, Database, Calendar, Filter,
  Sliders, BarChart3, PieChart as PieChartLucide, LineChart as LineChartLucide
} from 'lucide-react';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, 
  Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadialBarChart, RadialBar, ComposedChart, Scatter
} from 'recharts';
import { format, subDays, parseISO, differenceInDays, startOfDay, endOfDay, isSameDay } from 'date-fns';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/utils/api-client';
import { Skeleton } from '@/components/ui/skeleton';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';

interface MetricsData {
  revenue: {
    gmv: number;
    platform_fees: number;
    take_rate: number;
    average_order_value: number;
    daily_revenue: Record<string, any>;
    top_farmers: Array<{
      farmer_id: number;
      revenue: number;
      order_count: number;
      items_sold: number;
    }>;
  };
  orders: {
    total_orders: number;
    status_breakdown: Record<string, number>;
    payment_breakdown: Record<string, number>;
    cancellation_rate: number;
    daily_orders: Record<string, number>;
  };
  users: {
    total_users: number;
    new_users: number;
    active_users: number;
    role_breakdown: Record<string, number>;
    daily_registrations: Record<string, number>;
  };
  products: {
    total_products: number;
    new_products: number;
    status_breakdown: Record<string, number>;
    top_products: Array<{
      product_id: number;
      product_name: string;
      quantity_sold: number;
      revenue: number;
    }>;
  };
}

interface DateRange {
  from: Date;
  to: Date;
}

const AdminAnalytics: React.FC = () => {
  const [metricsData, setMetricsData] = useState<MetricsData | null>(null);
  const [realTimeData, setRealTimeData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [dateRange, setDateRange] = useState<DateRange>({
    from: subDays(new Date(), 29),
    to: new Date()
  });
  const [compareEnabled, setCompareEnabled] = useState<boolean>(false);
  const [compareDateRange, setCompareDateRange] = useState<DateRange>({
    from: subDays(subDays(new Date(), 30), 30), // 60 days ago
    to: subDays(new Date(), 30) // 30 days ago
  });
  const [compareData, setCompareData] = useState<MetricsData | null>(null);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [exportFormat, setExportFormat] = useState('csv');
  const [chartType, setChartType] = useState<'line' | 'bar' | 'area'>('line');
  const [timeGranularity, setTimeGranularity] = useState<'day' | 'week' | 'month'>('day');
  const [isLoadingCompare, setIsLoadingCompare] = useState(false);
  const { toast } = useToast();

  const fetchAllData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Fetch main data
      const data = await fetchAnalyticsData();
      setMetricsData(data);
      
      // Fetch comparison data if enabled
      if (compareEnabled && compareDateRange.from && compareDateRange.to) {
        const compareData = await fetchAnalyticsData(compareDateRange.from, compareDateRange.to);
        setCompareData(compareData);
      } else {
        setCompareData(null);
      }
      
      // Fetch real-time data
      await fetchRealTimeData();
      
    } catch (error) {
      console.error('Error in fetchAllData:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [dateRange, compareEnabled, compareDateRange, timeGranularity]);

  useEffect(() => {
    fetchAllData();
    
    // Set up real-time data refresh
    const interval = setInterval(() => {
      fetchRealTimeData();
      // Refresh all data periodically
      if (compareEnabled) {
        fetchAllData();
      }
    }, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, [fetchAllData, compareEnabled]);

  const fetchAnalyticsData = async (startDate?: Date, endDate?: Date) => {
    const start = startDate || dateRange.from;
    const end = endDate || dateRange.to;
    
    if (!start || !end) return null;
    
    try {
      const response = await apiClient.get('/analytics/dashboard', {
        params: {
          start_date: start.toISOString(),
          end_date: end.toISOString(),
          granularity: timeGranularity
        }
      });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching analytics data:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch analytics data',
        variant: 'destructive'
      });
      throw error;
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchAllData();
  };

  const handleDateRangeChange = (newDateRange: DateRange | undefined) => {
    if (!newDateRange?.from || !newDateRange?.to) return;
    
    setDateRange({
      from: startOfDay(newDateRange.from),
      to: endOfDay(newDateRange.to)
    });
    
    // If comparison is enabled, update the comparison range to match the duration
    if (compareEnabled && newDateRange.from && newDateRange.to) {
      const duration = differenceInDays(newDateRange.to, newDateRange.from);
      setCompareDateRange({
        from: subDays(newDateRange.from, duration + 1),
        to: subDays(newDateRange.from, 1)
      });
    }
  };

  const handleCompareToggle = (enabled: boolean) => {
    setCompareEnabled(enabled);
    
    if (enabled && dateRange.from && dateRange.to) {
      const duration = differenceInDays(dateRange.to, dateRange.from);
      setCompareDateRange({
        from: subDays(dateRange.from, duration + 1),
        to: subDays(dateRange.from, 1)
      });
    }
  };

  const fetchRealTimeData = async () => {
    try {
      const response = await apiClient.get('/analytics/real-time');
      setRealTimeData(response.data);
    } catch (error) {
      console.error('Failed to fetch real-time data:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const prepareChartData = (dailyData: Record<string, any>, compareData?: Record<string, any>) => {
    if (!dailyData) return [];
    
    // Format the main data
    const formattedData = Object.entries(dailyData).map(([date, data]) => ({
      date: format(new Date(date), timeGranularity === 'month' ? 'MMM yyyy' : 'MMM dd'),
      originalDate: date,
      ...data,
      // Add comparison data if available
      ...(compareData?.[date] && Object.fromEntries(
        Object.entries(compareData[date]).map(([key, value]) => 
          [`compare_${key}`, value]
        )
      ))
    }));
    
    return formattedData;
  };

  const calculateChange = (current: number, previous: number): number => {
    if (previous === 0) return current > 0 ? 100 : 0;
    return ((current - previous) / previous) * 100;

    // Align comparison data with the same date range
    return baseData.map(item => {
      const compareItem = compareData[item.originalDate] || {};
      return {
        ...item,
        compareValue: compareItem.value || 0,
        compareRevenue: compareItem.revenue || 0,
        compareOrders: compareItem.orders || 0,
        compareUsers: compareItem.users || 0,
      };
    });
  };

  const renderChart = (data: any[], dataKey: string, name: string, color: string, compareKey?: string) => {
    const ChartComponent = {
      line: Line,
      bar: Bar,
      area: Area
    }[chartType];

    return (
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => {
              if (timeGranularity === 'month') return value.split(' ')[0];
              return value;
            }}
          />
          <YAxis />
          <Tooltip 
            formatter={(value: number, name: string) => {
              if (name.includes('compare')) {
                return [value, `Previous ${name.replace('compare', '')}`];
              }
              return [value, name];
            }}
            labelFormatter={(label) => {
              const date = data.find(d => d.date === label)?.originalDate;
              return format(new Date(date || label), 'PPP');
            }}
          />
          <Legend />
          
          {compareDateRange.enabled && compareKey && (
            <ChartComponent
              type="monotone"
              dataKey={compareKey}
              name={`Previous ${name}`}
              stroke={`${color}80`}
              fill={`${color}20`}
              strokeDasharray="5 5"
              activeDot={{ r: 4 }}
            />
          )}
          
          <ChartComponent
            type="monotone"
            dataKey={dataKey}
            name={name}
            stroke={color}
            fill={color}
            fillOpacity={0.3}
            activeDot={{ r: 6 }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    );
  };

  const renderMetricCard = (title: string, value: string | number, icon: React.ReactNode, change?: number, loading?: boolean) => (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className="h-4 w-4 text-muted-foreground">
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-2">
            <Skeleton className="h-8 w-24" />
            <Skeleton className="h-4 w-16" />
          </div>
        ) : (
          <>
            <div className="text-2xl font-bold">{value}</div>
            {change !== undefined && (
              <div className={`text-xs ${change >= 0 ? 'text-green-500' : 'text-red-500'} flex items-center`}>
                {change >= 0 ? (
                  <TrendingUp className="h-3 w-3 mr-1" />
                ) : (
                  <TrendingDown className="h-3 w-3 mr-1" />
                )}
                {Math.abs(change)}% from previous period
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );

  const renderPieChart = (data: { name: string; value: number }[], colors: string[], title: string) => (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent className="flex justify-center">
        {data.length > 0 ? (
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => [value, 'Count']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            No data available
          </div>
        )}
      </CardContent>
    </Card>
  );

  const renderLoadingSkeleton = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-32 w-full" />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Skeleton className="h-80 w-full" />
        <Skeleton className="h-80 w-full" />
      </div>
      <Skeleton className="h-96 w-full" />
    </div>
  );

  if (loading && !metricsData) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading analytics...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
          <p className="text-muted-foreground">
            Comprehensive platform metrics and insights
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <DatePickerWithRange
            date={dateRange}
            onDateChange={handleDateRangeChange}
            compareEnabled={compareEnabled}
            onCompareChange={handleCompareToggle}
            compareDate={compareDateRange}
            onCompareDateChange={setCompareDateRange}
          />
          <Select value={exportFormat} onValueChange={setExportFormat}>
            <SelectTrigger className="w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="csv">CSV</SelectItem>
              <SelectItem value="json">JSON</SelectItem>
            </SelectContent>
          </Select>
          <Select 
            value={timeGranularity} 
            onValueChange={(value: 'day' | 'week' | 'month') => setTimeGranularity(value)}
          >
            <SelectTrigger className="w-24">
              <SelectValue placeholder="Granularity" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="day">Daily</SelectItem>
              <SelectItem value="week">Weekly</SelectItem>
              <SelectItem value="month">Monthly</SelectItem>
            </SelectContent>
          </Select>
          <Button
            onClick={handleRefresh}
            variant="outline"
            size="icon"
            disabled={refreshing}
            className="ml-2"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
          <Button
            onClick={() => handleExport()}
            variant="outline"
            className="ml-2"
            size="sm"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button
            onClick={fetchAnalyticsData}
            variant="outline"
            size="sm"
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Real-time Metrics */}
      {realTimeData && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" />
              Real-time Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {Object.entries(realTimeData.current_hour_events || {}).map(([event, count]) => (
                <div key={event} className="text-center">
                  <div className="text-2xl font-bold">{count as number}</div>
                  <div className="text-sm text-muted-foreground capitalize">
                    {event.replace('_', ' ')}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Metrics Cards */}
      {metricsData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(metricsData.revenue.gmv)}
              </div>
              <p className="text-xs text-muted-foreground">
                Take rate: {formatPercentage(metricsData.revenue.take_rate)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Orders</CardTitle>
              <ShoppingCart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metricsData.orders.total_orders.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                AOV: {formatCurrency(metricsData.revenue.average_order_value)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metricsData.users.active_users.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                New: {metricsData.users.new_users}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Products</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metricsData.products.total_products.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                New: {metricsData.products.new_products}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Detailed Analytics Tabs */}
      {metricsData && (
        <Tabs value={selectedTab} onValueChange={setSelectedTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="revenue">Revenue</TabsTrigger>
            <TabsTrigger value="orders">Orders</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="products">Products</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Revenue Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={prepareChartData(metricsData.revenue.daily_revenue)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip formatter={(value) => formatCurrency(value as number)} />
                      <Area type="monotone" dataKey="gmv" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Order Status Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={Object.entries(metricsData.orders.status_breakdown).map(([status, count]) => ({
                          name: status,
                          value: count
                        }))}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {Object.entries(metricsData.orders.status_breakdown).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={`hsl(${index * 45}, 70%, 60%)`} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="revenue" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Daily Revenue</CardTitle>
                  <CardDescription>GMV and platform fees over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={prepareChartData(metricsData.revenue.daily_revenue)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip formatter={(value) => formatCurrency(value as number)} />
                      <Legend />
                      <Line type="monotone" dataKey="gmv" stroke="#8884d8" name="GMV" />
                      <Line type="monotone" dataKey="platform_fees" stroke="#82ca9d" name="Platform Fees" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Top Performing Farmers</CardTitle>
                  <CardDescription>By revenue generated</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {metricsData.revenue.top_farmers.slice(0, 5).map((farmer, index) => (
                      <div key={farmer.farmer_id} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <Badge variant="outline">#{index + 1}</Badge>
                          <div>
                            <div className="font-medium">Farmer {farmer.farmer_id}</div>
                            <div className="text-sm text-muted-foreground">
                              {farmer.order_count} orders • {farmer.items_sold} items
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold">{formatCurrency(farmer.revenue)}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="orders" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Daily Orders</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={prepareChartData(metricsData.orders.daily_orders)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="orders" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Payment Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(metricsData.orders.payment_breakdown).map(([status, count]) => (
                      <div key={status} className="flex items-center justify-between">
                        <span className="capitalize">{status.replace('_', ' ')}</span>
                        <Badge variant="secondary">{count}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="users" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>User Registrations</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={prepareChartData(metricsData.users.daily_registrations)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Area type="monotone" dataKey="registrations" stroke="#8884d8" fill="#8884d8" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>User Roles</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(metricsData.users.role_breakdown).map(([role, count]) => (
                      <div key={role} className="flex items-center justify-between">
                        <span className="capitalize">{role}</span>
                        <Badge variant="secondary">{count}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="products" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Top Products</CardTitle>
                  <CardDescription>By revenue generated</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {metricsData.products.top_products.slice(0, 5).map((product, index) => (
                      <div key={product.product_id} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <Badge variant="outline">#{index + 1}</Badge>
                          <div>
                            <div className="font-medium">{product.product_name}</div>
                            <div className="text-sm text-muted-foreground">
                              {product.quantity_sold} sold
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold">{formatCurrency(product.revenue)}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Product Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(metricsData.products.status_breakdown).map(([status, count]) => (
                      <div key={status} className="flex items-center justify-between">
                        <span className="capitalize">{status.replace('_', ' ')}</span>
                        <Badge variant="secondary">{count}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};

export default AdminAnalytics;