import { useMemo, useState } from 'react';
import { StyleSheet, Pressable, FlatList } from 'react-native';
import { Text, View } from '@/components/Themed';
import { useQuery } from '@tanstack/react-query';

import { apiGet, apiPost } from '@/constants/Api';
import { useRouter } from 'expo-router';
import { useContext } from 'react';
import { CartContext } from '@/app/_layout';

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

type Cart = Record<number, number>; // product_id -> quantity

export default function CatalogScreen() {
  const router = useRouter();
  const cartCtx = useContext(CartContext);
  const { data: products, isLoading, isError } = useQuery<Product[]>({
    queryKey: ['products'],
    queryFn: () => apiGet('/marketplace/products'),
  });

  const [cart, setCart] = useState<Cart>({});

  const addToCart = (productId: number) => {
    if (cartCtx) cartCtx.add(productId, 1);
    setCart((c) => ({ ...c, [productId]: (c[productId] ?? 0) + 1 }));
  };

  const clearCart = () => setCart({});

  const subtotal = useMemo(() => {
    if (!products) return 0;
    return Object.entries(cart).reduce((sum, [pid, qty]) => {
      const p = products.find((pp) => pp.id === Number(pid));
      return sum + (p ? p.price * (qty as number) : 0);
    }, 0);
  }, [cart, products]);

  const checkout = async () => {
    if (!products) return;
    const items = Object.entries(cart)
      .filter(([, qty]) => (qty as number) > 0)
      .map(([pid, qty]) => ({ product_id: Number(pid), quantity: Number(qty) }));
    if (items.length === 0) return;

    const origin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8081';

    try {
      const resp = await apiPost<{ checkout_url: string; order_id: number }>(
        '/commerce/checkout_session',
        {
          items,
          success_url: `${origin}/success`,
          cancel_url: `${origin}/cancel`,
        }
      );
      if (resp.checkout_url) {
        if (typeof window !== 'undefined') {
          window.location.href = resp.checkout_url;
        }
      }
    } catch (e) {
      console.error('Checkout failed', e);
      // Possible unauthenticated
      router.push('/login');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Catalog</Text>
      <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />

      {isLoading && <Text>Loading products…</Text>}
      {isError && <Text style={{ color: 'red' }}>Failed to load products</Text>}

      {!!products && (
        <FlatList
          data={products}
          keyExtractor={(item) => String(item.id)}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>{item.name}</Text>
              {!!item.description && <Text style={styles.cardDesc}>{item.description}</Text>}
              <Text style={styles.cardPrice}>${item.price.toFixed(2)}</Text>
              <Pressable style={styles.btn} onPress={() => addToCart(item.id)}>
                <Text style={styles.btnText}>Add to cart</Text>
              </Pressable>
            </View>
          )}
          ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
        />
      )}

      <View style={styles.cartBar}>
        <Text>Subtotal: ${subtotal.toFixed(2)}</Text>
        <View style={{ flexDirection: 'row', gap: 12 }}>
          <Pressable style={[styles.btn, styles.btnSecondary]} onPress={clearCart}>
            <Text style={styles.btnText}>Clear</Text>
          </Pressable>
          <Pressable style={styles.btn} onPress={checkout}>
            <Text style={styles.btnText}>Checkout</Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    gap: 12,
  },
  title: {
    fontSize: 22,
    fontWeight: '700',
  },
  separator: {
    marginVertical: 6,
    height: 1,
    width: '100%',
  },
  card: {
    padding: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 8,
    gap: 6,
  },
  cardTitle: { fontSize: 16, fontWeight: '600' },
  cardDesc: { color: '#6b7280' },
  cardPrice: { fontWeight: '700' },
  btn: {
    backgroundColor: '#16a34a',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  btnSecondary: {
    backgroundColor: '#374151',
  },
  btnText: { color: 'white', fontWeight: '600' },
  cartBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
  },
});
