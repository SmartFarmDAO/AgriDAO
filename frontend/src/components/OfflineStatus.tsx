"""
Offline status indicator and sync management component.
"""

import React, { useEffect, useState } from 'react';
import { Wifi, WifiOff, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';
import { useOfflineSync } from '@/lib/offline-sync';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'sonner';

export const OfflineStatus: React.FC = () => {
  const {
    isOnline,
    pendingSync,
    syncInProgress,
    lastSyncTime,
    syncErrors,
    forceSync,
    clearSyncData,
    getPendingCount
  } = useOfflineSync();

  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Show toast when sync completes
    if (!syncInProgress && lastSyncTime) {
      const pendingCount = getPendingCount();
      if (pendingCount === 0) {
        toast.success('All changes synced successfully');
      } else {
        toast.info(`${pendingCount} changes pending sync`);
      }
    }
  }, [syncInProgress, lastSyncTime, getPendingCount]);

  const handleForceSync = async () => {
    try {
      await forceSync();
      toast.success('Sync completed successfully');
    } catch (error) {
      toast.error('Sync failed: ' + (error as Error).message);
    }
  };

  const handleClearSyncData = () => {
    if (window.confirm('Are you sure you want to clear all pending sync data? This action cannot be undone.')) {
      clearSyncData();
      toast.success('Sync data cleared');
    }
  };

  const getStatusIcon = () => {
    if (syncInProgress) {
      return <RefreshCw className="h-4 w-4 animate-spin" />;
    }
    if (!isOnline) {
      return <WifiOff className="h-4 w-4 text-destructive" />;
    }
    if (getPendingCount() > 0) {
      return <AlertCircle className="h-4 w-4 text-warning" />;
    }
    return <CheckCircle className="h-4 w-4 text-success" />;
  };

  const getStatusText = () => {
    if (syncInProgress) {
      return 'Syncing...';
    }
    if (!isOnline) {
      return 'Offline';
    }
    const pendingCount = getPendingCount();
    if (pendingCount > 0) {
      return `${pendingCount} pending`;
    }
    return 'All synced';
  };

  const getStatusColor = () => {
    if (syncInProgress) {
      return 'text-muted-foreground';
    }
    if (!isOnline) {
      return 'text-destructive';
    }
    if (getPendingCount() > 0) {
      return 'text-warning';
    }
    return 'text-success';
  };

  const formatTimestamp = (timestamp: number) => {
    return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
  };

  const groupedPending = pendingSync.reduce((acc, item) => {
    if (!acc[item.type]) {
      acc[item.type] = [];
    }
    acc[item.type].push(item);
    return acc;
  }, {} as Record<string, typeof pendingSync>);

  return (
    <>
      <div className="fixed bottom-4 right-4 z-50">
        <Button
          variant="outline"
          size="sm"
          className={`flex items-center gap-2 ${getStatusColor()}`}
          onClick={() => setIsOpen(true)}
        >
          {getStatusIcon()}
          <span className="text-sm">{getStatusText()}</span>
          {getPendingCount() > 0 && (
            <Badge variant="secondary" className="ml-1">
              {getPendingCount()}
            </Badge>
          )}
        </Button>
      </div>

      {isOpen && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <Card className="w-full max-w-2xl max-h-[80vh] flex flex-col">
            <CardHeader>
              <CardTitle>Offline Sync Status</CardTitle>
              <CardDescription>
                Manage your offline data synchronization
              </CardDescription>
            </CardHeader>
            
            <CardContent className="flex-1 overflow-hidden">
              <Tabs defaultValue="status" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="status">Status</TabsTrigger>
                  <TabsTrigger value="pending">Pending ({getPendingCount()})</TabsTrigger>
                  <TabsTrigger value="errors">Errors ({syncErrors.length})</TabsTrigger>
                </TabsList>

                <TabsContent value="status" className="mt-4">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-3">
                        {getStatusIcon()}
                        <div>
                          <p className="font-medium">{getStatusText()}</p>
                          <p className="text-sm text-muted-foreground">
                            {isOnline ? 'Connected to internet' : 'Working offline'}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={handleForceSync}
                          disabled={syncInProgress || !isOnline || getPendingCount() === 0}
                        >
                          <RefreshCw className="h-4 w-4 mr-1" />
                          Force Sync
                        </Button>
                        
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={handleClearSyncData}
                          disabled={getPendingCount() === 0}
                          className="text-destructive"
                        >
                          Clear All
                        </Button>
                      </div>
                    </div>

                    {lastSyncTime && (
                      <div className="text-sm text-muted-foreground">
                        Last sync: {formatTimestamp(lastSyncTime)}
                      </div>
                    )}

                    {syncInProgress && (
                      <div className="space-y-2">
                        <Progress value={((pendingSync.length - getPendingCount()) / pendingSync.length) * 100} />
                        <p className="text-sm text-center">
                          Syncing {pendingSync.length - getPendingCount()} of {pendingSync.length} items...
                        </p>
                      </div>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="pending" className="mt-4">
                  <ScrollArea className="h-64">
                    {getPendingCount() === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <CheckCircle className="h-12 w-12 mx-auto mb-2" />
                        <p>No pending sync items</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {Object.entries(groupedPending).map(([type, items]) => (
                          <div key={type}>
                            <h4 className="font-medium capitalize mb-2">{type}</h4>
                            <div className="space-y-2">
                              {items.map((item) => (
                                <div key={item.id} className="p-3 border rounded-lg">
                                  <div className="flex items-center justify-between">
                                    <div>
                                      <p className="text-sm font-medium capitalize">{item.action}</p>
                                      <p className="text-xs text-muted-foreground">
                                        {formatTimestamp(item.timestamp)}
                                      </p>
                                    </div>
                                    <Badge variant={item.retryCount > 0 ? "warning" : "secondary"}>
                                      {item.retryCount > 0 ? `${item.retryCount} retries` : 'Pending'}
                                    </Badge>
                                  </div>
                                  {item.lastSyncError && (
                                    <p className="text-xs text-destructive mt-1">
                                      {item.lastSyncError}
                                    </p>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </ScrollArea>
                </TabsContent>

                <TabsContent value="errors" className="mt-4">
                  <ScrollArea className="h-64">
                    {syncErrors.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <CheckCircle className="h-12 w-12 mx-auto mb-2" />
                        <p>No sync errors</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {syncErrors.map((error, index) => (
                          <div key={index} className="p-3 border rounded-lg border-destructive/50">
                            <div className="flex items-start gap-2">
                              <AlertCircle className="h-4 w-4 text-destructive mt-0.5" />
                              <p className="text-sm">{error}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </ScrollArea>
                </TabsContent>
              </Tabs>
            </CardContent>
            
            <div className="p-4 border-t">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
                className="w-full"
              >
                Close
              </Button>
            </div>
          </Card>
        </div>
      )}
    </>
  );
};

export default OfflineStatus;