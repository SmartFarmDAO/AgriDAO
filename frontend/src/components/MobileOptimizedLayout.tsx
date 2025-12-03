"""
Mobile-optimized layout component with responsive design and touch gestures.
"""

import React, { useEffect, useState } from 'react';
import { useMobileOptimization, useTouchGestures } from '@/hooks/useMobileOptimization';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Menu, 
  Home, 
  Package, 
  ShoppingCart, 
  User, 
  Settings,
  TrendingUp,
  Bell,
  Search
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface MobileOptimizedLayoutProps {
  children: React.ReactNode;
  title?: string;
  showSearch?: boolean;
  onSearch?: (query: string) => void;
}

export const MobileOptimizedLayout: React.FC<MobileOptimizedLayoutProps> = ({
  children,
  title = "AgriDAO",
  showSearch = false,
  onSearch
}) => {
  const {
    isMobile,
    isTablet,
    deviceType,
    shouldOptimize,
    prefersReducedMotion,
    effectiveType,
    lowPowerMode
  } = useMobileOptimization();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('home');
  const [searchQuery, setSearchQuery] = useState('');

  const { onTouchStart, onTouchMove, onTouchEnd } = useTouchGestures();

  const handleSwipe = (gesture: string | null) => {
    if (gesture === 'swipe-right') {
      setSidebarOpen(true);
    } else if (gesture === 'swipe-left') {
      setSidebarOpen(false);
    }
  };

  useEffect(() => {
    // Set mobile viewport meta tag
    const viewport = document.querySelector('meta[name=viewport]');
    if (viewport) {
      viewport.setAttribute('content', 
        'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no'
      );
    }

    // Add mobile CSS classes
    document.documentElement.classList.toggle('mobile', isMobile);
    document.documentElement.classList.toggle('tablet', isTablet);
    document.documentElement.classList.toggle('low-power', lowPowerMode);
  }, [isMobile, isTablet, lowPowerMode]);

  const navigationItems = [
    { id: 'home', label: 'Home', icon: Home, href: '/' },
    { id: 'products', label: 'Products', icon: Package, href: '/products' },
    { id: 'orders', label: 'Orders', icon: ShoppingCart, href: '/orders' },
    { id: 'market', label: 'Market', icon: TrendingUp, href: '/market' },
    { id: 'profile', label: 'Profile', icon: User, href: '/profile' },
  ];

  const bottomNavItems = navigationItems.slice(0, 5);

  const Sidebar = () => (
    <div className="space-y-4">
      <div className="px-4 py-2">
        <h2 className="text-lg font-semibold">{title}</h2>
        {shouldOptimize && (
          <Badge variant="outline" className="mt-1">
            {deviceType} Mode
          </Badge>
        )}
      </div>
      
      <nav className="space-y-1">
        {navigationItems.map((item) => (
          <a
            key={item.id}
            href={item.href}
            className={cn(
              "flex items-center gap-3 px-4 py-2 text-sm rounded-lg transition-colors",
              activeTab === item.id 
                ? "bg-primary text-primary-foreground" 
                : "hover:bg-accent"
            )}
            onClick={() => {
              setActiveTab(item.id);
              setSidebarOpen(false);
            }}
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </a>
        ))}
      </nav>

      {showSearch && (
        <div className="px-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                onSearch?.(e.target.value);
              }}
              className="w-full pl-10 pr-3 py-2 border rounded-lg text-sm"
            />
          </div>
        </div>
      )}

      {/* Performance indicators */}
      {(lowPowerMode || effectiveType !== '4g') && (
        <div className="px-4 space-y-2">
          <Separator />
          {lowPowerMode && (
            <div className="flex items-center gap-2 text-sm text-warning">
              <Bell className="h-4 w-4" />
              Low Power Mode
            </div>
          )}
          {effectiveType !== '4g' && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Bell className="h-4 w-4" />
              {effectiveType.toUpperCase()} Connection
            </div>
          )}
        </div>
      )}
    </div>
  );

  const BottomNavigation = () => (
    <div className="fixed bottom-0 left-0 right-0 bg-background border-t md:hidden">
      <div className="flex justify-around items-center h-16">
        {bottomNavItems.map((item) => (
          <button
            key={item.id}
            className={cn(
              "flex flex-col items-center justify-center flex-1 py-2 text-xs transition-colors",
              activeTab === item.id 
                ? "text-primary" 
                : "text-muted-foreground"
            )}
            onClick={() => {
              setActiveTab(item.id);
              window.location.href = item.href;
            }}
          >
            <item.icon className="h-5 w-5 mb-1" />
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );

  // Desktop/Tablet Layout
  if (!isMobile) {
    return (
      <div className="min-h-screen flex">
        {/* Sidebar */}
        <aside className="w-64 bg-background border-r hidden md:block">
          <Sidebar />
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col">
          <header className="border-b px-6 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold">{title}</h1>
              
              {showSearch && (
                <div className="relative w-64">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      onSearch?.(e.target.value);
                    }}
                    className="w-full pl-10 pr-3 py-2 border rounded-lg"
                  />
                </div>
              )}
            </div>
          </header>

          <div className="flex-1 overflow-hidden">
            <ScrollArea className="h-full">
              <div className="p-6">
                {children}
              </div>
            </ScrollArea>
          </div>
        </main>
      </div>
    );
  }

  // Mobile Layout
  return (
    <div 
      className="min-h-screen bg-background"
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={(e) => handleSwipe(onTouchEnd())}
    >
      {/* Mobile Header */}
      <header className="sticky top-0 z-40 bg-background border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64 p-0">
              <Sidebar />
            </SheetContent>
          </Sheet>

          <h1 className="text-lg font-semibold">{title}</h1>

          <Button variant="ghost" size="icon">
            <Bell className="h-5 w-5" />
          </Button>
        </div>

        {showSearch && (
          <div className="mt-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  onSearch?.(e.target.value);
                }}
                className="w-full pl-10 pr-3 py-2 border rounded-lg text-sm"
              />
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="pb-20">
        <ScrollArea className="h-full">
          <div className="p-4">
            {children}
          </div>
        </ScrollArea>
      </main>

      {/* Bottom Navigation */}
      <BottomNavigation />

      {/* Performance overlay for debugging */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed top-16 right-4 bg-black/80 text-white text-xs p-2 rounded z-50">
          <div>Device: {deviceType}</div>
          <div>Optimize: {shouldOptimize ? 'Yes' : 'No'}</div>
          <div>Motion: {prefersReducedMotion ? 'Reduced' : 'Normal'}</div>
        </div>
      )}
    </div>
  );
};

// Mobile-optimized card component
export const MobileCard: React.FC<{
  children: React.ReactNode;
  className?: string;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
}> = ({ children, className, onSwipeLeft, onSwipeRight }) => {
  const { onTouchStart, onTouchMove, onTouchEnd } = useTouchGestures();

  const handleSwipe = (gesture: string | null) => {
    if (gesture === 'swipe-left') {
      onSwipeLeft?.();
    } else if (gesture === 'swipe-right') {
      onSwipeRight?.();
    }
  };

  return (
    <Card
      className={className}
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={(e) => handleSwipe(onTouchEnd())}
    >
      <CardContent className="p-4">
        {children}
      </CardContent>
    </Card>
  );
};

// Mobile-optimized tabs component
export const MobileTabs: React.FC<{
  tabs: Array<{ id: string; label: string; content: React.ReactNode }>;
  defaultTab?: string;
}> = ({ tabs, defaultTab }) => {
  const { isMobile } = useMobileOptimization();

  if (!isMobile) {
    return (
      <Tabs defaultValue={defaultTab || tabs[0]?.id}>
        <TabsList>
          {tabs.map((tab) => (
            <TabsTrigger key={tab.id} value={tab.id}>
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>
        {tabs.map((tab) => (
          <TabsContent key={tab.id} value={tab.id}>
            {tab.content}
          </TabsContent>
        ))}
      </Tabs>
    );
  }

  return (
    <Tabs defaultValue={defaultTab || tabs[0]?.id} className="w-full">
      <TabsList className="w-full grid grid-cols-2">
        {tabs.slice(0, 2).map((tab) => (
          <TabsTrigger key={tab.id} value={tab.id}>
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>
      {tabs.map((tab) => (
        <TabsContent key={tab.id} value={tab.id} className="mt-4">
          {tab.content}
        </TabsContent>
      ))}
    </Tabs>
  );
};