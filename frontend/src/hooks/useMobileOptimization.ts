"""
Mobile optimization hooks and utilities.
"""

import { useEffect, useState, useCallback, useMemo } from 'react';
import { debounce } from 'lodash';

// Hook for detecting mobile devices
export const useMobileDetection = () => {
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);
  const [deviceType, setDeviceType] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');

  useEffect(() => {
    const checkDevice = () => {
      const userAgent = navigator.userAgent.toLowerCase();
      const isMobileDevice = /mobile|android|iphone|ipad|phone/.test(userAgent);
      const isTabletDevice = /ipad|tablet/.test(userAgent) && !/mobile/.test(userAgent);
      
      const screenWidth = window.innerWidth;
      const mobileBreakpoint = 768;
      const tabletBreakpoint = 1024;

      const mobile = isMobileDevice || screenWidth < mobileBreakpoint;
      const tablet = isTabletDevice || (screenWidth >= mobileBreakpoint && screenWidth < tabletBreakpoint);

      setIsMobile(mobile);
      setIsTablet(tablet);
      setDeviceType(mobile ? 'mobile' : tablet ? 'tablet' : 'desktop');
    };

    checkDevice();
    window.addEventListener('resize', checkDevice);
    return () => window.removeEventListener('resize', checkDevice);
  }, []);

  return { isMobile, isTablet, deviceType };
};

// Hook for touch gestures
export const useTouchGestures = () => {
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);
  const [touchEnd, setTouchEnd] = useState<{ x: number; y: number } | null>(null);

  const onTouchStart = useCallback((e: React.TouchEvent) => {
    const touch = e.touches[0];
    setTouchStart({ x: touch.clientX, y: touch.clientY });
    setTouchEnd(null);
  }, []);

  const onTouchMove = useCallback((e: React.TouchEvent) => {
    const touch = e.touches[0];
    setTouchEnd({ x: touch.clientX, y: touch.clientY });
  }, []);

  const onTouchEnd = useCallback(() => {
    if (!touchStart || !touchEnd) return null;

    const deltaX = touchEnd.x - touchStart.x;
    const deltaY = touchEnd.y - touchStart.y;
    const absDeltaX = Math.abs(deltaX);
    const absDeltaY = Math.abs(deltaY);

    if (absDeltaX > absDeltaY) {
      if (absDeltaX > 50) {
        return deltaX > 0 ? 'swipe-right' : 'swipe-left';
      }
    } else {
      if (absDeltaY > 50) {
        return deltaY > 0 ? 'swipe-down' : 'swipe-up';
      }
    }

    return null;
  }, [touchStart, touchEnd]);

  return {
    onTouchStart,
    onTouchMove,
    onTouchEnd,
    touchStart,
    touchEnd
  };
};

// Hook for viewport optimization
export const useViewportOptimization = () => {
  const [viewport, setViewport] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
    isPortrait: window.innerHeight > window.innerWidth,
    scale: 1
  });

  useEffect(() => {
    const updateViewport = debounce(() => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      setViewport({
        width,
        height,
        isPortrait: height > width,
        scale: Math.min(width / 375, 1) // Scale based on iPhone 375px width
      });

      // Update viewport meta tag for mobile
      if (width <= 768) {
        const viewportMeta = document.querySelector('meta[name=viewport]');
        if (viewportMeta) {
          viewportMeta.setAttribute('content', 
            'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no'
          );
        }
      }
    }, 100);

    updateViewport();
    window.addEventListener('resize', updateViewport);
    window.addEventListener('orientationchange', updateViewport);
    
    return () => {
      window.removeEventListener('resize', updateViewport);
      window.removeEventListener('orientationchange', updateViewport);
    };
  }, []);

  return viewport;
};

// Hook for performance monitoring
export const usePerformanceMonitoring = () => {
  const [metrics, setMetrics] = useState({
    loadTime: 0,
    renderTime: 0,
    memoryUsage: 0,
    fps: 60
  });

  useEffect(() => {
    if ('performance' in window) {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      setMetrics(prev => ({
        ...prev,
        loadTime: navigation.loadEventEnd - navigation.loadEventStart
      }));
    }

    if ('memory' in performance) {
      const memory = (performance as any).memory;
      setMetrics(prev => ({
        ...prev,
        memoryUsage: memory.usedJSHeapSize / 1024 / 1024 // MB
      }));
    }

    // Monitor FPS
    let frameCount = 0;
    let lastTime = performance.now();
    
    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime - lastTime >= 1000) {
        setMetrics(prev => ({ ...prev, fps: frameCount }));
        frameCount = 0;
        lastTime = currentTime;
      }
      
      requestAnimationFrame(measureFPS);
    };
    
    requestAnimationFrame(measureFPS);

    return () => {
      // Cleanup
    };
  }, []);

  return metrics;
};

// Hook for lazy loading
export const useLazyLoading = (threshold = 0.1) => {
  const [isVisible, setIsVisible] = useState(false);
  const [ref, setRef] = useState<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!ref) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting);
      },
      { threshold }
    );

    observer.observe(ref);
    return () => observer.disconnect();
  }, [ref, threshold]);

  return { ref: setRef, isVisible };
};

// Hook for image optimization
export const useImageOptimization = () => {
  const { isMobile, deviceType } = useMobileDetection();

  const getOptimizedImage = useCallback((src: string, options?: {
    width?: number;
    height?: number;
    quality?: number;
    format?: 'webp' | 'jpeg' | 'png';
  }) => {
    const { width, height, quality = 80, format = 'webp' } = options || {};
    
    // Mobile-specific optimizations
    if (isMobile) {
      const mobileWidth = width ? Math.min(width, 375) : 375;
      const mobileHeight = height ? Math.min(height, 667) : undefined;
      
      // Use CDN or image service URL
      const optimizedUrl = new URL(src);
      optimizedUrl.searchParams.set('w', mobileWidth.toString());
      optimizedUrl.searchParams.set('q', quality.toString());
      optimizedUrl.searchParams.set('f', format);
      
      if (mobileHeight) {
        optimizedUrl.searchParams.set('h', mobileHeight.toString());
      }
      
      return optimizedUrl.toString();
    }

    return src;
  }, [isMobile]);

  return { getOptimizedImage };
};

// Hook for reduced motion preference
export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return { prefersReducedMotion };
};

// Hook for battery optimization
export const useBatteryOptimization = () => {
  const [batteryInfo, setBatteryInfo] = useState<{
    level: number;
    charging: boolean;
    lowPowerMode: boolean;
  }>({ level: 1, charging: false, lowPowerMode: false });

  useEffect(() => {
    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        const updateBattery = () => {
          setBatteryInfo({
            level: battery.level,
            charging: battery.charging,
            lowPowerMode: battery.level < 0.2 && !battery.charging
          });
        };

        updateBattery();
        battery.addEventListener('levelchange', updateBattery);
        battery.addEventListener('chargingchange', updateBattery);

        return () => {
          battery.removeEventListener('levelchange', updateBattery);
          battery.removeEventListener('chargingchange', updateBattery);
        };
      });
    }
  }, []);

  return batteryInfo;
};

// Hook for network optimization
export const useNetworkOptimization = () => {
  const [connectionInfo, setConnectionInfo] = useState<{
    effectiveType: string;
    downlink: number;
    saveData: boolean;
  }>({ effectiveType: '4g', downlink: 10, saveData: false });

  useEffect(() => {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      
      const updateConnection = () => {
        setConnectionInfo({
          effectiveType: connection.effectiveType,
          downlink: connection.downlink,
          saveData: connection.saveData
        });
      };

      updateConnection();
      connection.addEventListener('change', updateConnection);
      
      return () => connection.removeEventListener('change', updateConnection);
    }
  }, []);

  return connectionInfo;
};

// Combined mobile optimization hook
export const useMobileOptimization = () => {
  const mobileDetection = useMobileDetection();
  const viewport = useViewportOptimization();
  const performance = usePerformanceMonitoring();
  const battery = useBatteryOptimization();
  const network = useNetworkOptimization();
  const reducedMotion = useReducedMotion();

  const shouldOptimize = useMemo(() => {
    return mobileDetection.isMobile || 
           battery.lowPowerMode || 
           network.saveData || 
           network.effectiveType === '2g' ||
           network.effectiveType === '3g';
  }, [mobileDetection.isMobile, battery.lowPowerMode, network]);

  return {
    ...mobileDetection,
    ...viewport,
    ...performance,
    ...battery,
    ...network,
    ...reducedMotion,
    shouldOptimize
  };
};