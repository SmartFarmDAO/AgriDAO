import { StyleSheet } from 'react-native';

import { Text, View } from '@/components/Themed';
import { useQuery } from '@tanstack/react-query';
import { Card, Button } from '@/ui/primitives';
import { useRouter } from 'expo-router';

const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export default function TabOneScreen() {
  const router = useRouter();
  const { data, isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const res = await fetch(`${BASE_URL}/health`);
      if (!res.ok) throw new Error('health failed');
      return res.json();
    },
  });
  return (
    <View style={styles.container}>
      <Card>
        <Text style={styles.title}>AgriDAO</Text>
        <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
        {isLoading && <Text>Loading backend…</Text>}
        {isError && <Text style={{ color: 'red' }}>Backend not reachable</Text>}
        {data && <Text>Backend: {data.status}</Text>}
        <View style={{ height: 12 }} />
        <Button title="Browse Catalog" onPress={() => router.push('/(tabs)/two')} />
      </Card>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  separator: {
    marginVertical: 30,
    height: 1,
    width: '80%',
  },
});
