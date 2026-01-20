import React from 'react';
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate, useLocation, Outlet } from "react-router-dom";
import { WalletProvider } from "@/lib/wallet";
import AppLayout from "@/components/layout/AppLayout";
import { AuthProvider, useAuth } from "@/hooks/use-auth";
import { useConfig } from "@/hooks/use-config";
import { Loader2 } from "lucide-react";
import { WagmiProvider } from 'wagmi';
import { RainbowKitProvider } from '@rainbow-me/rainbowkit';
import { config } from '@/config/wagmi';
import { LanguageProvider } from '@/components/LanguageProvider';
import { CartProvider } from '@/contexts/CartContext';
import '@rainbow-me/rainbowkit/styles.css';

// Pages
import Index from "./pages/Index";
import Auth from "./pages/Auth";
import NotFound from "./pages/NotFound";
import FarmerOnboarding from "./pages/FarmerOnboarding";
import Marketplace from "./pages/Marketplace";
import Finance from "./pages/Finance";
import OrdersPage from "./pages/Orders";
import OrderDetailPage from "./pages/OrderDetail";
import UserManagement from "./pages/UserManagement";
import SupplyChain from "./pages/SupplyChain";
import Governance from "./pages/Governance";
import AI from "./pages/AI";
import Dashboard from "./pages/Dashboard";
import AddProduct from "./pages/AddProduct";
import Profile from "./pages/Profile";
import AdminDashboard from "./pages/AdminDashboard";
import Community from "./pages/Community";
import BlockchainPage from "./pages/BlockchainPage";

// Initialize query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Type definitions
interface WithChildren {
  children: React.ReactNode;
}

// Protected route component
const ProtectedRoute: React.FC<WithChildren> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-t-4 border-gray-200 border-t-green-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

// Main App Routes component
const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        {/* Public routes */}
        <Route index element={<Index />} />
        <Route path="auth" element={<Auth />} />
        <Route path="marketplace" element={<Marketplace />} />

        {/* Protected routes */}
        <Route element={
          <ProtectedRoute>
            <Outlet />
          </ProtectedRoute>
        }>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="profile" element={<Profile />} />
          <Route path="onboarding" element={<FarmerOnboarding />} />
          <Route path="products/new" element={<AddProduct />} />
          <Route path="products/:id/edit" element={<AddProduct />} />
          <Route path="finance" element={<Finance />} />
          <Route path="orders">
            <Route index element={<OrdersPage />} />
            <Route path=":id" element={<OrderDetailPage />} />
          </Route>
          <Route path="users" element={<UserManagement />} />
          <Route path="supply-chain" element={<SupplyChain />} />
          <Route path="governance" element={<Governance />} />
          <Route path="ai" element={<AI />} />
          <Route path="admin" element={<AdminDashboard />} />
          <Route path="community" element={<Community />} />
          <Route path="blockchain" element={<BlockchainPage />} />
        </Route>

        {/* 404 - Not Found */}
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
};

// Configuration Provider Component
const ConfigProvider: React.FC<WithChildren> = ({ children }) => {
  const { isLoading, error } = useConfig();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-12 w-12 animate-spin text-green-600" />
          <p className="text-muted-foreground">Loading configuration...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center p-4">
        <div className="max-w-md rounded-lg border border-red-200 bg-red-50 p-6 text-center">
          <h2 className="mb-2 text-xl font-semibold text-red-700">Configuration Error</h2>
          <p className="mb-4 text-red-600">Failed to load application configuration.</p>
          <button
            onClick={() => window.location.reload()}
            className="rounded bg-red-100 px-4 py-2 text-red-700 hover:bg-red-200"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

// Main App Component
const App: React.FC = () => {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          <BrowserRouter>
            <TooltipProvider>
              <WalletProvider>
                <AuthProvider>
                  <LanguageProvider>
                    <ConfigProvider>
                      <CartProvider>
                        <Toaster />
                        <Sonner />
                        <AppRoutes />
                      </CartProvider>
                    </ConfigProvider>
                  </LanguageProvider>
                </AuthProvider>
              </WalletProvider>
            </TooltipProvider>
          </BrowserRouter>
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
};

export default App;
