import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Download, Trash2, FileText, Shield, AlertTriangle, CheckCircle } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface ConsentStatus {
  essential: boolean;
  analytics: boolean;
  marketing: boolean;
  third_party: boolean;
  location: boolean;
}

interface DataRequest {
  id: string;
  request_type: string;
  status: string;
  requested_at: string;
  completed_at?: string;
  data_url?: string;
}

interface PrivacySummary {
  consent_status: ConsentStatus;
  privacy_rights: Record<string, boolean>;
  data_retention: Record<string, string>;
  contact: Record<string, string>;
}

export function PrivacyDashboard() {
  const { user } = useAuth();
  const [consent, setConsent] = useState<ConsentStatus>({
    essential: true,
    analytics: true,
    marketing: false,
    third_party: false,
    location: false
  });
  const [loading, setLoading] = useState(false);
  const [privacySummary, setPrivacySummary] = useState<PrivacySummary | null>(null);
  const [dataRequests, setDataRequests] = useState<DataRequest[]>([]);
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    fetchPrivacyData();
  }, []);

  const fetchPrivacyData = async () => {
    try {
      setLoading(true);
      
      const [consentResponse, summaryResponse] = await Promise.all([
        api.get('/privacy/consent'),
        api.get('/privacy/summary')
      ]);
      
      setConsent(consentResponse.data.consent);
      setPrivacySummary(summaryResponse.data);
      
      // Fetch data requests history
      const requestsResponse = await api.get('/privacy/data-requests');
      setDataRequests(requestsResponse.data || []);
      
    } catch (error) {
      console.error('Failed to fetch privacy data:', error);
      toast.error('Failed to load privacy settings');
    } finally {
      setLoading(false);
    }
  };

  const handleConsentChange = async (consentType: keyof ConsentStatus, granted: boolean) => {
    try {
      setLoading(true);
      
      await api.post('/privacy/consent', {
        consent_type: consentType,
        granted
      });
      
      setConsent(prev => ({ ...prev, [consentType]: granted }));
      toast.success(`Consent updated for ${consentType}`);
      
    } catch (error) {
      console.error('Failed to update consent:', error);
      toast.error('Failed to update consent');
    } finally {
      setLoading(false);
    }
  };

  const handleExportData = async () => {
    try {
      setIsExporting(true);
      
      const response = await api.get('/privacy/export', {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `user-data-${user?.id}-${new Date().toISOString()}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Data export started');
      
    } catch (error) {
      console.error('Failed to export data:', error);
      toast.error('Failed to export data');
    } finally {
      setIsExporting(false);
    }
  };

  const handleDeleteData = async () => {
    if (!window.confirm('Are you sure you want to delete your data? This action cannot be undone.')) {
      return;
    }
    
    try {
      setLoading(true);
      
      const response = await api.post('/privacy/delete', {
        deletion_scope: 'full'
      });
      
      toast.success('Data deletion request submitted');
      
      // Logout user after deletion
      window.location.href = '/logout';
      
    } catch (error) {
      console.error('Failed to delete data:', error);
      toast.error('Failed to delete data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'processing': return 'text-blue-600';
      case 'pending': return 'text-yellow-600';
      case 'failed': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const consentTypes = [
    { key: 'essential', label: 'Essential Services', description: 'Required for basic functionality', required: true },
    { key: 'analytics', label: 'Analytics', description: 'Help us improve our services' },
    { key: 'marketing', label: 'Marketing', description: 'Personalized recommendations and offers' },
    { key: 'third_party', label: 'Third-party Sharing', description: 'Share data with trusted partners' },
    { key: 'location', label: 'Location Services', description: 'Location-based features and recommendations' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center space-x-2">
        <Shield className="h-6 w-6 text-primary" />
        <h1 className="text-3xl font-bold">Privacy Dashboard</h1>
      </div>

      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Your Privacy Rights</AlertTitle>
        <AlertDescription>
          You have full control over your data. You can view, export, or delete your data at any time.
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>Consent Management</CardTitle>
          <CardDescription>
            Manage your consent preferences for different types of data processing
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {consentTypes.map(({ key, label, description, required }) => (
            <div key={key} className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex-1">
                <Label className="text-lg font-medium">
                  {label}
                  {required && <Badge variant="secondary" className="ml-2">Required</Badge>}
                </Label>
                <p className="text-sm text-gray-600 mt-1">{description}</p>
              </div>
              <Switch
                checked={consent[key as keyof ConsentStatus]}
                onCheckedChange={(checked) => handleConsentChange(key as keyof ConsentStatus, checked)}
                disabled={required || loading}
              />
            </div>
          ))}
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Data Export</CardTitle>
            <CardDescription>
              Download all your data in a portable format
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={handleExportData} 
              disabled={isExporting}
              className="w-full"
            >
              <Download className="mr-2 h-4 w-4" />
              {isExporting ? 'Exporting...' : 'Export My Data'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Data Deletion</CardTitle>
            <CardDescription>
              Permanently delete your account and all associated data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={handleDeleteData}
              disabled={loading}
              variant="destructive"
              className="w-full"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete My Data
            </Button>
          </CardContent>
        </Card>
      </div>

      {privacySummary && (
        <Card>
          <CardHeader>
            <CardTitle>Privacy Summary</CardTitle>
            <CardDescription>
              Overview of your privacy settings and rights
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-medium mb-2">Your Rights</h3>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(privacySummary.privacy_rights).map(([right, enabled]) => (
                  <div key={right} className="flex items-center space-x-2">
                    {enabled ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    )}
                    <span className="text-sm capitalize">
                      {right.replace('right_to_', '').replace('_', ' ')}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            <div>
              <h3 className="font-medium mb-2">Data Retention</h3>
              <div className="space-y-1 text-sm">
                {Object.entries(privacySummary.data_retention).map(([type, period]) => (
                  <div key={type} className="flex justify-between">
                    <span className="capitalize">{type.replace('_', ' ')}:</span>
                    <span className="text-gray-600">{period}</span>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            <div>
              <h3 className="font-medium mb-2">Contact Information</h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Privacy Officer:</span>
                  <span className="text-gray-600">{privacySummary.contact.privacy_officer}</span>
                </div>
                <div className="flex justify-between">
                  <span>Data Protection Officer:</span>
                  <span className="text-gray-600">{privacySummary.contact.data_protection_officer}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {dataRequests.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Data Request History</CardTitle>
            <CardDescription>
              History of your data access and deletion requests
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dataRequests.map((request) => (
                <div key={request.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium capitalize">{request.request_type} Request</p>
                    <p className="text-sm text-gray-600">
                      Requested: {new Date(request.requested_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Badge 
                    variant={request.status === 'completed' ? 'default' : 'secondary'}
                    className={getStatusColor(request.status)}
                  >
                    {request.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}