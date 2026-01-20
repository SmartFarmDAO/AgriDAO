"""
Offline data synchronization system for AgriDAO.
"""

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface OfflineData {
  id: string;
  type: string;
  data: any;
  action: 'create' | 'update' | 'delete';
  timestamp: number;
  synced: boolean;
  retryCount: number;
  lastSyncError?: string;
}

interface SyncState {
  isOnline: boolean;
  pendingSync: OfflineData[];
  syncInProgress: boolean;
  lastSyncTime: number | null;
  syncErrors: string[];
}

interface SyncActions {
  setOnline: (online: boolean) => void;
  addToQueue: (item: Omit<OfflineData, 'id' | 'timestamp' | 'synced' | 'retryCount'>) => void;
  markSynced: (id: string) => void;
  markFailed: (id: string, error: string) => void;
  removeFromQueue: (id: string) => void;
  clearSyncErrors: () => void;
  startSync: () => void;
  finishSync: () => void;
  getPendingItems: (type?: string) => OfflineData[];
}

const useSyncStore = create<SyncState & SyncActions>()(
  persist(
    (set, get) => ({
      // State
      isOnline: navigator.onLine,
      pendingSync: [],
      syncInProgress: false,
      lastSyncTime: null,
      syncErrors: [],

      // Actions
      setOnline: (online) => set({ isOnline: online }),
      
      addToQueue: (item) => set((state) => ({
        pendingSync: [...state.pendingSync, {
          ...item,
          id: crypto.randomUUID(),
          timestamp: Date.now(),
          synced: false,
          retryCount: 0
        }]
      })),
      
      markSynced: (id) => set((state) => ({
        pendingSync: state.pendingSync.filter(item => item.id !== id)
      })),
      
      markFailed: (id, error) => set((state) => ({
        pendingSync: state.pendingSync.map(item =>
          item.id === id
            ? { ...item, retryCount: item.retryCount + 1, lastSyncError: error }
            : item
        ),
        syncErrors: [...state.syncErrors, error]
      })),
      
      removeFromQueue: (id) => set((state) => ({
        pendingSync: state.pendingSync.filter(item => item.id !== id)
      })),
      
      clearSyncErrors: () => set({ syncErrors: [] }),
      
      startSync: () => set({ syncInProgress: true }),
      
      finishSync: () => set({ 
        syncInProgress: false, 
        lastSyncTime: Date.now() 
      }),
      
      getPendingItems: (type) => {
        const state = get();
        return type 
          ? state.pendingSync.filter(item => item.type === type)
          : state.pendingSync;
      }
    }),
    {
      name: 'offline-sync-storage',
      version: 1
    }
  )
);

export class OfflineSyncManager {
  private syncInterval: number | null = null;
  private maxRetries = 3;
  private retryDelay = 1000; // 1 second

  constructor() {
    this.setupEventListeners();
    this.startAutoSync();
  }

  private setupEventListeners() {
    // Listen for online/offline events
    window.addEventListener('online', () => {
      useSyncStore.getState().setOnline(true);
      this.syncPendingData();
    });

    window.addEventListener('offline', () => {
      useSyncStore.getState().setOnline(false);
    });

    // Listen for page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && navigator.onLine) {
        this.syncPendingData();
      }
    });
  }

  private startAutoSync() {
    // Sync every 30 seconds when online
    this.syncInterval = window.setInterval(() => {
      if (navigator.onLine) {
        this.syncPendingData();
      }
    }, 30000);
  }

  public stopAutoSync() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  public async syncPendingData() {
    const { pendingSync, syncInProgress, startSync, finishSync } = useSyncStore.getState();
    
    if (syncInProgress || pendingSync.length === 0 || !navigator.onLine) {
      return;
    }

    startSync();

    try {
      for (const item of pendingSync) {
        if (item.retryCount >= this.maxRetries) {
          console.warn(`Max retries reached for item ${item.id}, skipping`);
          continue;
        }

        try {
          await this.syncItem(item);
          useSyncStore.getState().markSynced(item.id);
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          useSyncStore.getState().markFailed(item.id, errorMessage);
          
          if (item.retryCount >= this.maxRetries) {
            console.error(`Failed to sync item ${item.id} after ${this.maxRetries} attempts:`, error);
          }
        }

        // Add delay between syncs to avoid overwhelming the server
        await new Promise(resolve => setTimeout(resolve, this.retryDelay));
      }
    } finally {
      finishSync();
    }
  }

  private async syncItem(item: OfflineData) {
    const endpoint = this.getEndpointForType(item.type, item.action);
    const method = this.getMethodForAction(item.action);

    const response = await fetch(endpoint, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(item.data)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  private getEndpointForType(type: string, action: string): string {
    const endpoints: Record<string, Record<string, string>> = {
      'bid': {
        create: '/api/bids',
        update: `/api/bids/${type}`,
        delete: `/api/bids/${type}`
      },
      'order': {
        create: '/api/orders',
        update: `/api/orders/${type}`,
        delete: `/api/orders/${type}`
      },
      'product': {
        create: '/api/products',
        update: `/api/products/${type}`,
        delete: `/api/products/${type}`
      },
      'profile': {
        create: '/api/users/profile',
        update: '/api/users/profile',
        delete: '/api/users/profile'
      }
    };

    const endpoint = endpoints[type]?.[action];
    if (!endpoint) {
      throw new Error(`No endpoint configured for type: ${type}, action: ${action}`);
    }

    return endpoint;
  }

  private getMethodForAction(action: string): string {
    const methods: Record<string, string> = {
      create: 'POST',
      update: 'PUT',
      delete: 'DELETE'
    };
    return methods[action] || 'POST';
  }

  public queueItem(type: string, action: 'create' | 'update' | 'delete', data: any) {
    useSyncStore.getState().addToQueue({ type, action, data });
    
    // Try to sync immediately if online
    if (navigator.onLine) {
      this.syncPendingData();
    }
  }

  public getSyncStatus() {
    return useSyncStore.getState();
  }

  public clearSyncData() {
    useSyncStore.getState().pendingSync = [];
    useSyncStore.getState().syncErrors = [];
  }

  public getPendingCount(type?: string): number {
    return useSyncStore.getState().getPendingItems(type).length;
  }

  public async forceSync() {
    if (!navigator.onLine) {
      throw new Error('Cannot sync: No internet connection');
    }
    
    await this.syncPendingData();
  }
}

// React hook for offline sync
export const useOfflineSync = () => {
  const syncState = useSyncStore();
  const syncManager = new OfflineSyncManager();

  return {
    // State
    isOnline: syncState.isOnline,
    pendingSync: syncState.pendingSync,
    syncInProgress: syncState.syncInProgress,
    lastSyncTime: syncState.lastSyncTime,
    syncErrors: syncState.syncErrors,
    
    // Actions
    queueItem: syncManager.queueItem.bind(syncManager),
    forceSync: syncManager.forceSync.bind(syncManager),
    clearSyncData: syncManager.clearSyncData.bind(syncManager),
    getPendingCount: syncManager.getPendingCount.bind(syncManager),
    
    // Utilities
    hasPendingItems: (type?: string) => syncManager.getPendingCount(type) > 0
  };
};

// Global sync manager instance
export const offlineSyncManager = new OfflineSyncManager();