import { useContext, useMemo } from 'react';
import { StyleSheet, FlatList } from 'react-native';
import { Text, View } from '@/components/Themed';
import { CartContext } from '@/app/_layout';
import { Button, Card } from '@/ui/primitives';
import { apiGet } from '@/constants/Api';
import { useRouter } from 'expo-router';

type Product = { id: number; name: string; price: number };

export default function Cart() {
  const router = useRouter();
  const cart = useContext(CartContext);
  const productIds = Object.keys(cart?.items ?? {}).map((k) => Number(k));

  // In a real app, preload products or fetch details per id.
  const subtotal = useMemo(() => 0, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Cart</Text>
      <FlatList
        data={productIds}
        keyExtractor={(id) => String(id)}
        renderItem={({ item }) => (
          <Card>
            <Text>Product #{item}</Text>
            <Text>Qty: {cart?.items[item]}</Text>
          </Card>
        )}
        ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
      />
      <View style={{ height: 12 }} />
      <Button title="Go to Catalog" onPress={() => router.push('/(tabs)/two')} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, gap: 12 },
  title: { fontSize: 22, fontWeight: '700' },
});


