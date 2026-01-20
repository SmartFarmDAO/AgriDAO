import { useLocalSearchParams, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { StyleSheet } from 'react-native';
import { Text, View } from '@/components/Themed';
import { apiGet } from '@/constants/Api';
import { Button, Card } from '@/ui/primitives';

type Product = {
  id: number;
  name: string;
  description?: string;
  category?: string;
  price: number;
  quantity: string;
  farmer_id?: number;
  created_at: string;
};

export default function ProductDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    (async () => {
      try {
        const p = await apiGet<Product>(`/marketplace/products/${id}`);
        setProduct(p);
      } catch (e: any) {
        setError(e.message);
      }
    })();
  }, [id]);

  if (error) return <View style={styles.container}><Text style={{ color: 'red' }}>{error}</Text></View>;
  if (!product) return <View style={styles.container}><Text>Loading…</Text></View>;

  return (
    <View style={styles.container}>
      <Card>
        <Text style={styles.title}>{product.name}</Text>
        {!!product.description && <Text style={styles.muted}>{product.description}</Text>}
        <View style={{ height: 12 }} />
        <Text style={styles.price}>${product.price.toFixed(2)}</Text>
        <View style={{ height: 12 }} />
        <Button title="Add to cart" onPress={() => router.push('/(tabs)/two')} />
      </Card>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 22, fontWeight: '700' },
  muted: { color: '#6b7280' },
  price: { fontSize: 18, fontWeight: '700' },
});


