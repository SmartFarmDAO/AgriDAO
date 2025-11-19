import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useToast } from "@/components/ui/use-toast";
import { listMyOrders } from "@/lib/api";
import { Order } from "@/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

const OrdersPage = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const data = await listMyOrders();
        setOrders(data);
      } catch (err) {
        setError("Failed to fetch orders.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, []);

  // If redirected from Stripe success with ?order_id=..., jump to detail
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const oid = params.get("order_id");
    if (oid) {
      navigate(`/orders/${oid}`, { replace: true });
    }
  }, [location.search, navigate]);

  if (loading) return <div>Loading...</div>;
  if (error) {
    toast({ title: "Orders Error", description: error, variant: "destructive" });
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">My Orders</h1>
      {orders.length === 0 && (
        <div className="text-center text-muted-foreground mb-4">No orders yet.</div>
      )}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Order ID</TableHead>
            <TableHead>Date</TableHead>
            <TableHead>Total</TableHead>
            <TableHead>Payment Status</TableHead>
            <TableHead>Status</TableHead>
            <TableHead></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {orders.map((order) => (
            <TableRow key={order.id}>
              <TableCell>#{order.id}</TableCell>
              <TableCell>{new Date(order.created_at).toLocaleDateString()}</TableCell>
              <TableCell>${order.total.toFixed(2)}</TableCell>
              <TableCell>
                <Badge variant={order.payment_status === 'paid' ? 'default' : 'destructive'}>
                  {order.payment_status}
                </Badge>
              </TableCell>
              <TableCell>
                 <Badge variant="secondary">{order.status}</Badge>
              </TableCell>
              <TableCell>
                <Link to={`/orders/${order.id}`} className="text-blue-500 hover:underline">
                  View Details
                </Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default OrdersPage;
