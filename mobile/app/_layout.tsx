import FontAwesome from '@expo/vector-icons/FontAwesome';
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import React, { useEffect, createContext, useMemo, useState } from 'react';
import * as SecureStore from 'expo-secure-store';
import 'react-native-reanimated';

import { useColorScheme } from '@/components/useColorScheme';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export {
  // Catch any errors thrown by the Layout component.
  ErrorBoundary,
} from 'expo-router';

export const unstable_settings = {
  // Ensure that reloading on `/modal` keeps a back button present.
  initialRouteName: '(tabs)',
};

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

const queryClient = new QueryClient();

type CartItems = Record<number, number>;
type CartContextType = {
  items: CartItems;
  add: (id: number, qty?: number) => void;
  clear: () => void;
};
export const CartContext = createContext<CartContextType | null>(null);

type AuthContextType = {
  token: string | null;
  setToken: (t: string | null) => void;
};
export const AuthContext = createContext<AuthContextType | null>(null);

export default function RootLayout() {
  const [loaded, error] = useFonts({
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
    ...FontAwesome.font,
  });

  // Expo Router uses Error Boundaries to catch errors in the navigation tree.
  useEffect(() => {
    if (error) throw error;
  }, [error]);

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  const [items, setItems] = useState<CartItems>({});
  const [token, setTokenState] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const stored = await SecureStore.getItemAsync('authToken');
      if (stored) setTokenState(stored);
    })();
  }, []);

  const setToken = async (t: string | null) => {
    setTokenState(t);
    if (t) await SecureStore.setItemAsync('authToken', t);
    else await SecureStore.deleteItemAsync('authToken');
  };
  const value = useMemo<CartContextType>(() => ({
    items,
    add: (id, qty = 1) => setItems((c) => ({ ...c, [id]: (c[id] ?? 0) + qty })),
    clear: () => setItems({}),
  }), [items]);

  return (
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider value={{ token, setToken }}>
        <CartContext.Provider value={value}>
          <RootLayoutNav />
        </CartContext.Provider>
      </AuthContext.Provider>
    </QueryClientProvider>
  );
}

function RootLayoutNav() {
  const colorScheme = useColorScheme();

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
      </Stack>
    </ThemeProvider>
  );
}
