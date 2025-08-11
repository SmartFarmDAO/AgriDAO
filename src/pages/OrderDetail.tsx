import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getOrder } from "@/lib/api";
import { Order } from "@/types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

const OrderDetailPage = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOrder = async () => {
      if (!orderId) return;
      try {
        const data = await getOrder(parseInt(orderId, 10));
        setOrder(data);
      } catch (err) {
        setError("Failed to fetch order details.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchOrder();
  }, [orderId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;
  if (!order) return <div>Order not found.</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Order #{order.id}</h1>
      <div className="grid md:grid-cols-2 gap-4 mb-4">
        <div>
          <p><strong>Date:</strong> {new Date(order.created_at).toLocaleDateString()}</p>
          <p><strong>Total:</strong> ${order.total.toFixed(2)}</p>
        </div>
        <div>
          <p><strong>Payment Status:</strong> <Badge variant={order.payment_status === 'paid' ? 'default' : 'destructive'}>{order.payment_status}</Badge></p>
          <p><strong>Status:</strong> <Badge variant="secondary">{order.status}</Badge></p>
        </div>
      </div>
      <h2 className="text-xl font-bold mb-2">Items</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Product</TableHead>
            <TableHead>Quantity</TableHead>
            <TableHead>Unit Price</TableHead>
            <TableHead>Subtotal</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {order.items?.map((item) => (
            <TableRow key={item.product_id}>
              <TableCell>{item.product_name || 'N/A'}</TableCell>
              <TableCell>{item.quantity}</TableCell>
              <TableCell>${item.unit_price.toFixed(2)}</TableCell>
              <TableCell>${(item.quantity * item.unit_price).toFixed(2)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default OrderDetailPage;
