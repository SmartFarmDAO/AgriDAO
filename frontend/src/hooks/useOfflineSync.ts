"""
React hooks for offline synchronization.
"""

import { useCallback, useEffect, useState } from 'react';
import { useOfflineSync as useOfflineSyncStore } from '@/lib/offline-sync';

// Hook for bid creation with offline support
export const useOfflineBidCreation = () => {
  const { queueItem } = useOfflineSyncStore();

  const createBid = useCallback(async (bidData: any) => {
    try {
      // Try to create bid online
      const response = await fetch('/api/bids', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(bidData)
      });

      if (response.ok) {
        return await response.json();
      }

      // If offline or server error, queue for sync
      if (!navigator.onLine || response.status >= 500) {
        queueItem('bid', 'create', bidData);
        return { id: 'pending', ...bidData, _pending: true };
      }

      throw new Error('Failed to create bid');
    } catch (error) {
      // Network error, queue for sync
      queueItem('bid', 'create', bidData);
      return { id: 'pending', ...bidData, _pending: true };
    }
  }, [queueItem]);

  return { createBid };
};

// Hook for order updates with offline support
export const useOfflineOrderUpdate = () => {
  const { queueItem } = useOfflineSyncStore();

  const updateOrder = useCallback(async (orderId: string, orderData: any) => {
    try {
      const response = await fetch(`/api/orders/${orderId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(orderData)
      });

      if (response.ok) {
        return await response.json();
      }

      if (!navigator.onLine || response.status >= 500) {
        queueItem('order', 'update', { id: orderId, ...orderData });
        return { id: orderId, ...orderData, _pending: true };
      }

      throw new Error('Failed to update order');
    } catch (error) {
      queueItem('order', 'update', { id: orderId, ...orderData });
      return { id: orderId, ...orderData, _pending: true };
    }
  }, [queueItem]);

  return { updateOrder };
};

// Hook for product management with offline support
export const useOfflineProductManagement = () => {
  const { queueItem } = useOfflineSyncStore();

  const createProduct = useCallback(async (productData: any) => {
    try {
      const response = await fetch('/api/products', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(productData)
      });

      if (response.ok) {
        return await response.json();
      }

      if (!navigator.onLine || response.status >= 500) {
        queueItem('product', 'create', productData);
        return { id: 'pending', ...productData, _pending: true };
      }

      throw new Error('Failed to create product');
    } catch (error) {
      queueItem('product', 'create', productData);
      return { id: 'pending', ...productData, _pending: true };
    }
  }, [queueItem]);

  const updateProduct = useCallback(async (productId: string, productData: any) => {
    try {
      const response = await fetch(`/api/products/${productId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(productData)
      });

      if (response.ok) {
        return await response.json();
      }

      if (!navigator.onLine || response.status >= 500) {
        queueItem('product', 'update', { id: productId, ...productData });
        return { id: productId, ...productData, _pending: true };
      }

      throw new Error('Failed to update product');
    } catch (error) {
      queueItem('product', 'update', { id: productId, ...productData });
      return { id: productId, ...productData, _pending: true };
    }
  }, [queueItem]);

  const deleteProduct = useCallback(async (productId: string) => {
    try {
      const response = await fetch(`/api/products/${productId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        return true;
      }

      if (!navigator.onLine || response.status >= 500) {
        queueItem('product', 'delete', { id: productId });
        return true;
      }

      throw new Error('Failed to delete product');
    } catch (error) {
      queueItem('product', 'delete', { id: productId });
      return true;
    }
  }, [queueItem]);

  return { createProduct, updateProduct, deleteProduct };
};

// Hook for profile updates with offline support
export const useOfflineProfileUpdate = () => {
  const { queueItem } = useOfflineSyncStore();

  const updateProfile = useCallback(async (profileData: any) => {
    try {
      const response = await fetch('/api/users/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        return await response.json();
      }

      if (!navigator.onLine || response.status >= 500) {
        queueItem('profile', 'update', profileData);
        return { ...profileData, _pending: true };
      }

      throw new Error('Failed to update profile');
    } catch (error) {
      queueItem('profile', 'update', profileData);
      return { ...profileData, _pending: true };
    }
  }, [queueItem]);

  return { updateProfile };
};

// Hook for checking if data is pending sync
export const useIsPendingSync = (type: string, id?: string) => {
  const { getPendingItems } = useOfflineSyncStore();
  const [isPending, setIsPending] = useState(false);

  useEffect(() => {
    const checkPending = () => {
      const pendingItems = getPendingItems(type);
      if (id) {
        setIsPending(pendingItems.some(item => item.data.id === id));
      } else {
        setIsPending(pendingItems.length > 0);
      }
    };

    checkPending();
    const interval = setInterval(checkPending, 1000);
    return () => clearInterval(interval);
  }, [type, id, getPendingItems]);

  return isPending;
};

// Hook for getting pending items count
export const usePendingCount = (type?: string) => {
  const { getPendingCount } = useOfflineSyncStore();
  const [count, setCount] = useState(0);

  useEffect(() => {
    const updateCount = () => {
      setCount(getPendingCount(type));
    };

    updateCount();
    const interval = setInterval(updateCount, 1000);
    return () => clearInterval(interval);
  }, [type, getPendingCount]);

  return count;
};

// Hook for sync status monitoring
export const useSyncStatus = () => {
  const {
    isOnline,
    pendingSync,
    syncInProgress,
    lastSyncTime,
    syncErrors
  } = useOfflineSyncStore();

  return {
    isOnline,
    pendingCount: pendingSync.length,
    syncInProgress,
    lastSyncTime,
    syncErrors,
    hasPending: pendingSync.length > 0,
    hasErrors: syncErrors.length > 0
  };
};