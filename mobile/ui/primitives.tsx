import { Pressable, StyleSheet, TextInput, View as RNView } from 'react-native';
import { Text, View } from '@/components/Themed';
import { colors, radii, spacing } from './theme';

export function Button({ title, onPress, variant = 'primary' }: { title: string; onPress: () => void; variant?: 'primary' | 'secondary' | 'outline' }) {
  const style: any[] = [
    styles.btn,
    variant === 'primary' && { backgroundColor: colors.primary },
    variant === 'secondary' && { backgroundColor: '#111827' },
    variant === 'outline' && { backgroundColor: 'transparent', borderWidth: 1, borderColor: colors.border },
  ];
  const textStyle: any[] = [styles.btnText, variant === 'outline' && { color: colors.text }];
  return (
    <Pressable onPress={onPress} style={style}>
      <Text style={textStyle}>{title}</Text>
    </Pressable>
  );
}

export function Card({ children }: { children: React.ReactNode }) {
  return <RNView style={styles.card}>{children}</RNView>;
}

export function Badge({ children }: { children: React.ReactNode }) {
  return (
    <RNView style={styles.badge}>
      <Text style={{ color: colors.primary, fontWeight: '600' }}>{children}</Text>
    </RNView>
  );
}

export function TextField(props: React.ComponentProps<typeof TextInput>) {
  return <TextInput {...props} style={[styles.input, props.style]} />;
}

const styles = StyleSheet.create({
  btn: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.lg,
    borderRadius: radii.md,
    alignItems: 'center',
  },
  btnText: { color: 'white', fontWeight: '700' },
  card: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.lg,
    padding: spacing.lg,
  },
  badge: {
    borderWidth: 1,
    borderColor: colors.primary,
    paddingVertical: 2,
    paddingHorizontal: 8,
    borderRadius: radii.sm,
    alignSelf: 'flex-start',
  },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.md,
    padding: spacing.md,
  },
});


