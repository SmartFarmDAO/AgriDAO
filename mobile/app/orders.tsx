import { useEffect, useState } from 'react';
import { StyleSheet, FlatList } from 'react-native';
import { Text, View } from '@/components/Themed';
import { apiGet } from '@/constants/Api';
import { Card } from '@/ui/primitives';

type Order = {
  id: number;
  status: string;
  subtotal: number;
  platform_fee: number;
  total: number;
  payment_status: string;
  created_at: string;
};

export default function Orders() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await apiGet<Order[]>(`/commerce/orders`);
        setOrders(data);
      } catch (e: any) {
        setError(e.message);
      }
    })();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My Orders</Text>
      {!!error && <Text style={{ color: 'red' }}>{error}</Text>}
      <FlatList
        data={orders}
        keyExtractor={(o) => String(o.id)}
        renderItem={({ item }) => (
          <Card>
            <Text style={{ fontWeight: '700' }}>Order #{item.id}</Text>
            <Text>Status: {item.status} • Payment: {item.payment_status}</Text>
            <Text>Total: ${item.total.toFixed(2)}</Text>
            <Text>Date: {new Date(item.created_at).toLocaleString()}</Text>
          </Card>
        )}
        ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, gap: 12 },
  title: { fontSize: 22, fontWeight: '700' },
});


