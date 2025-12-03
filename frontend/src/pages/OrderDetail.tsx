import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getOrder } from "@/lib/api";
import { Order } from "@/types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/use-toast";

const OrderDetailPage = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

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
  if (error) {
    toast({ title: "Order Error", description: error, variant: "destructive" });
  }
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
          {order.items && order.items.length > 0 ? (
            order.items.map((item) => (
              <TableRow key={item.product_id}>
                <TableCell>{item.product_name || 'N/A'}</TableCell>
                <TableCell>{item.quantity}</TableCell>
                <TableCell>${item.unit_price.toFixed(2)}</TableCell>
                <TableCell>${(item.quantity * item.unit_price).toFixed(2)}</TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={4} className="text-center text-muted-foreground">No items on this order.</TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      {/* Fee Breakdown */}
      <div className="mt-6 max-w-md ml-auto space-y-1">
        <div className="flex justify-between text-sm">
          <span>Subtotal</span>
          <span>${order.subtotal.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Platform fee</span>
          <span>${order.platform_fee.toFixed(2)}</span>
        </div>
        <div className="flex justify-between items-center border-t pt-2 mt-2">
          <span className="font-semibold">Total</span>
          <span className="font-semibold">${order.total.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
};

export default OrderDetailPage;
