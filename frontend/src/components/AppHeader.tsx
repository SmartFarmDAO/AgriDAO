import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { secureStorage } from "@/lib/security";
import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { NavLink } from "./NavLink";
import { CartButton } from "./CartButton";
import { UserMenu } from "./UserMenu";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { useTranslation } from "@/i18n/config";
import { createCheckoutSession } from "@/lib/api";
import { useCart } from "@/contexts/CartContext";

export function AppHeader() {
  const navigate = useNavigate();
  const location = useLocation();
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const { cart, cartTotal, updateQuantity, removeFromCart } = useCart();
  const { toast } = useToast();
  const { t } = useTranslation();

  useEffect(() => {
    const u = secureStorage.get<{ id: number; email: string; role: string }>("current_user");
    setUserEmail(u?.email ?? null);
  }, [location.pathname]);

  const handleCheckout = async () => {
    if (!cart.length) return;
    try {
      const payload = {
        items: cart.map(i => ({ product_id: i.product.id, quantity: i.quantity })),
        success_url: `${window.location.origin}/orders`,
        cancel_url: window.location.href,
      };
      const data = await createCheckoutSession(payload);
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        toast({ title: "Checkout Error", description: "Could not retrieve checkout URL.", variant: "destructive" });
      }
    } catch (error: any) {
      const msg = String(error?.message ?? "Failed to create checkout session.");
      if (msg.includes("401")) {
        toast({ title: "Sign in required", description: "Please sign in to checkout.", variant: "destructive" });
        const redirect = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/auth?redirect=${redirect}`;
      } else {
        toast({ title: "Checkout Error", description: msg, variant: "destructive" });
      }
    }
  };

  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/80 backdrop-blur-md shadow-sm">
      <div className="container flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <div className="flex items-center">
          <button
            className="mr-2 p-2 text-gray-600 hover:bg-gray-100 rounded-md md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            <span className="sr-only">Toggle menu</span>
          </button>
          <a href="/" className="flex items-center space-x-2">
            <span className="text-xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              AgriDAO
            </span>
          </a>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-1">
          <NavLink to="/marketplace">{t('common.marketplace')}</NavLink>
          <NavLink to="/finance">{t('common.finance')}</NavLink>
          <NavLink to="/supply-chain">{t('common.supplyChain')}</NavLink>
          <NavLink to="/governance">{t('common.governance')}</NavLink>
          <NavLink to="/ai">
            <span className="flex items-center">
              {t('common.aiAssistant')}
              <span className="ml-1.5 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 px-2 py-0.5 text-xs font-medium text-white">
                New
              </span>
            </span>
          </NavLink>
        </nav>

        {/* Right side actions */}
        <div className="flex items-center space-x-3">
          {/* Search - Hidden on mobile */}
          <div className="hidden md:block relative">
            <div className="relative">
              <input
                placeholder="Search products, farms..."
                className="h-9 w-64 rounded-full border border-gray-200 bg-gray-50 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                type="search"
              />
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="absolute left-3 top-2.5 h-4 w-4 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          {/* Cart */}
          <CartButton
            cartCount={cartCount}
            cartItems={cart}
            cartTotal={cartTotal}
            onCheckout={handleCheckout}
            onUpdateQuantity={updateQuantity}
            onRemoveItem={removeFromCart}
          />

          {/* Language Switcher */}
          <LanguageSwitcher />

          {/* User menu */}
          {userEmail ? (
            <UserMenu userEmail={userEmail} />
          ) : (
            <Button
              onClick={() => navigate('/auth')}
              className="hidden md:flex items-center space-x-1.5 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white"
            >
              <span>{t('common.signIn')}</span>
            </Button>
          )}
        </div>
      </div>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t bg-white">
          <div className="px-2 pt-2 pb-3 space-y-1">
            <NavLink to="/marketplace" className="block px-3 py-2">{t('common.marketplace')}</NavLink>
            <NavLink to="/finance" className="block px-3 py-2">{t('common.finance')}</NavLink>
            <NavLink to="/supply-chain" className="block px-3 py-2">{t('common.supplyChain')}</NavLink>
            <NavLink to="/governance" className="block px-3 py-2">{t('common.governance')}</NavLink>
            <NavLink to="/ai" className="block px-3 py-2">
              <span className="flex items-center">
                {t('common.aiAssistant')}
                <span className="ml-2 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 px-2 py-0.5 text-xs font-medium text-white">
                  New
                </span>
              </span>
            </NavLink>
            {!userEmail && (
              <Button
                onClick={() => navigate('/auth')}
                className="w-full mt-2 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white"
              >
                {t('common.signIn')}
              </Button>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

export default AppHeader;
