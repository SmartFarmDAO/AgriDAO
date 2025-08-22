import { StyleSheet } from 'react-native';
import { Text, View } from '@/components/Themed';

export default function Success() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Payment successful</Text>
      <Text>Your order has been paid. You will receive updates shortly.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 16, gap: 8 },
  title: { fontSize: 22, fontWeight: '700' },
});

