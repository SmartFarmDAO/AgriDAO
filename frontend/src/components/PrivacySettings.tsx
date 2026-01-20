import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { PrivacyManager } from '@/utils/security';

export function PrivacySettings() {
  const [loading, setLoading] = useState<string | null>(null);
  const [settings, setSettings] = useState({
    analytics: true,
    marketing: false,
    dataSharing: false,
  });

  const handleDataExport = async () => {
    setLoading('export');
    try {
      const data = await PrivacyManager.exportUserData('current-user-id');
      const url = URL.createObjectURL(data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `agridao-data-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success('Your data has been exported');
    } catch (error) {
      toast.error('Failed to export data');
    } finally {
      setLoading(null);
    }
  };

  const handleDataDeletion = async () => {
    if (window.confirm('Are you sure you want to delete all your data? This action cannot be undone.')) {
      setLoading('delete');
      try {
        await PrivacyManager.deleteUserData('current-user-id');
        toast.success('Your data has been scheduled for deletion');
        // Redirect to logout
        window.location.href = '/logout';
      } catch (error) {
        toast.error('Failed to delete data');
      } finally {
        setLoading(null);
      }
    }
  };

  const handleSettingChange = (setting: keyof typeof settings) => {
    setSettings(prev => ({ ...prev, [setting]: !prev[setting] }));
    toast.success('Privacy settings updated');
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Privacy Settings</CardTitle>
          <CardDescription>
            Manage your privacy preferences and data sharing settings
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Analytics Tracking</Label>
              <p className="text-sm text-muted-foreground">
                Allow us to collect anonymous usage data to improve the service
              </p>
            </div>
            <Switch
              checked={settings.analytics}
              onCheckedChange={() => handleSettingChange('analytics')}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Marketing Communications</Label>
              <p className="text-sm text-muted-foreground">
                Receive updates about new features and promotions
              </p>
            </div>
            <Switch
              checked={settings.marketing}
              onCheckedChange={() => handleSettingChange('marketing')}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Data Sharing</Label>
              <p className="text-sm text-muted-foreground">
                Share data with trusted partners for service improvements
              </p>
            </div>
            <Switch
              checked={settings.dataSharing}
              onCheckedChange={() => handleSettingChange('dataSharing')}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Data Management</CardTitle>
          <CardDescription>
            Export or delete your personal data in compliance with GDPR and CCPA
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h4 className="font-medium">Export Your Data</h4>
            <p className="text-sm text-muted-foreground">
              Download a copy of all your personal data in JSON format
            </p>
            <Button
              onClick={handleDataExport}
              disabled={loading === 'export'}
              variant="outline"
            >
              {loading === 'export' ? 'Exporting...' : 'Export Data'}
            </Button>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">Delete Your Data</h4>
            <p className="text-sm text-muted-foreground">
              Permanently delete all your personal data and account information
            </p>
            <Button
              onClick={handleDataDeletion}
              disabled={loading === 'delete'}
              variant="destructive"
            >
              {loading === 'delete' ? 'Deleting...' : 'Delete All Data'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Data Retention Policy</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="text-sm text-muted-foreground whitespace-pre-wrap">
            {PrivacyManager.getDataRetentionPolicy()}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}