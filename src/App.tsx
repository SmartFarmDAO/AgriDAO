import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { WalletProvider } from "@/lib/wallet";
import AppLayout from "@/components/layout/AppLayout";
import { AuthProvider, useAuth } from "@/hooks/use-auth";
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
import Profile from "./pages/Profile";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Protected route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
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

const AppRoutes = () => (
  <Routes>
    {/* Public routes */}
    <Route path="/" element={<Index />} />
    <Route path="/auth" element={<Auth />} />
    
    {/* Protected routes */}
    <Route
      path="/dashboard"
      element={
        <ProtectedRoute>
          <AppLayout>
            <Dashboard />
          </AppLayout>
        </ProtectedRoute>
      }
    />
    <Route
      path="/profile"
      element={
        <ProtectedRoute>
          <AppLayout>
            <Profile />
          </AppLayout>
        </ProtectedRoute>
      }
    />
    <Route
      path="/farmer-onboarding"
      element={
        <ProtectedRoute>
          <AppLayout>
            <FarmerOnboarding />
          </AppLayout>
        </ProtectedRoute>
      }
    />
    <Route
      path="/marketplace"
      element={
        <AppLayout>
          <Marketplace />
        </AppLayout>
      }
    />
    <Route
      path="/finance"
      element={
        <ProtectedRoute>
          <AppLayout>
            <Finance />
          </AppLayout>
        </ProtectedRoute>
      }
    />
    <Route
      path="/orders"
      element={
        <ProtectedRoute>
          <AppLayout>
            <OrdersPage />
          </AppLayout>
        </ProtectedRoute>
      }
    />
    <Route
      path="/orders/:orderId"
      element={
        <ProtectedRoute>
          <AppLayout>
            <OrderDetailPage />
          </AppLayout>
        </ProtectedRoute>
      }
    />
    <Route
      path="/users"
      element={
        <ProtectedRoute>
          <AppLayout>
            <UserManagement />
          </AppLayout>
        </ProtectedRoute>
      }
    />
    <Route
      path="/supply-chain"
      element={
        <AppLayout>
          <SupplyChain />
        </AppLayout>
      }
    />
    <Route
      path="/governance"
      element={
        <AppLayout>
          <Governance />
        </AppLayout>
      }
    />
    <Route
      path="/ai"
      element={
        <AppLayout>
          <AI />
        </AppLayout>
      }
    />
    
    {/* 404 - Not Found */}
    <Route path="*" element={<NotFound />} />
  </Routes>
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <WalletProvider>
        <AuthProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </AuthProvider>
      </WalletProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
