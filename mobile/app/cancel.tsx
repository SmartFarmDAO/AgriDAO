import { StyleSheet } from 'react-native';
import { Text, View } from '@/components/Themed';

export default function Cancel() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Payment cancelled</Text>
      <Text>Your checkout was cancelled. You can try again.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 16, gap: 8 },
  title: { fontSize: 22, fontWeight: '700' },
});

