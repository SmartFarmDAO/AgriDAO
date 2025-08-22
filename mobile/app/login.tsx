import { useState } from 'react';
import { StyleSheet } from 'react-native';
import { Text, View } from '@/components/Themed';
import { requestOtp, verifyOtp, setAuthToken } from '@/constants/Api';
import { AuthContext } from '@/app/_layout';
import { useContext } from 'react';
import { Button, TextField, Card } from '@/ui/primitives';

export default function Login() {
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [step, setStep] = useState<'request' | 'verify'>('request');
  const [message, setMessage] = useState<string | null>(null);

  const onRequest = async () => {
    try {
      const res = await requestOtp(email);
      setMessage(res.dev_code ? `Dev code: ${res.dev_code}` : 'Code sent');
      setStep('verify');
    } catch (e: any) {
      setMessage(e.message);
    }
  };

  const auth = useContext(AuthContext);
  const onVerify = async () => {
    try {
      const res = await verifyOtp(email, code);
      setAuthToken(res.access_token);
      auth?.setToken(res.access_token);
      setMessage('Logged in');
    } catch (e: any) {
      setMessage(e.message);
    }
  };

  return (
    <View style={styles.container}>
      <Card>
        <Text style={styles.title}>Sign in</Text>
        <Text style={styles.sub}>We’ll email a one-time code to verify you</Text>
        <View style={{ height: 12 }} />
        <TextField
          placeholder="email@example.com"
          autoCapitalize="none"
          keyboardType="email-address"
          value={email}
          onChangeText={setEmail}
        />
        {step === 'verify' && (
          <>
            <View style={{ height: 8 }} />
            <TextField
              placeholder="6-digit code"
              autoCapitalize="none"
              keyboardType="number-pad"
              value={code}
              onChangeText={setCode}
            />
          </>
        )}
        <View style={{ height: 12 }} />
        {step === 'request' ? (
          <Button title="Send Code" onPress={onRequest} />
        ) : (
          <Button title="Verify" onPress={onVerify} />
        )}
        {!!message && (
          <>
            <View style={{ height: 8 }} />
            <Text>{message}</Text>
          </>
        )}
      </Card>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, gap: 12, justifyContent: 'center' },
  title: { fontSize: 22, fontWeight: '700' },
  sub: { color: '#6b7280' },
});


