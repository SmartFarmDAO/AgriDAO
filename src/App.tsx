import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
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

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/farmer-onboarding" element={<FarmerOnboarding />} />
          <Route path="/marketplace" element={<Marketplace />} />
          <Route path="/finance" element={<Finance />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/orders/:orderId" element={<OrderDetailPage />} />
          <Route path="/users" element={<UserManagement />} />
          <Route path="/supply-chain" element={<SupplyChain />} />
              <Route path="/governance" element={<Governance />} />
              <Route path="/ai" element={<AI />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
