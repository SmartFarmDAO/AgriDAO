import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Shield, AlertTriangle, CheckCircle, XCircle, RefreshCw, Download, Eye } from 'lucide-react';
import { api } from '@/lib/api';

interface SecurityEvent {
  event_id: string;
  timestamp: string;
  event_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  source_ip: string;
  user_id?: string;
  description: string;
  details: any;
}

interface SecurityIncident {
  incident_id: string;
  created_at: string;
  incident_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  affected_users: number;
  status: string;
  response_actions: any[];
}

interface Vulnerability {
  vuln_id: string;
  discovered_at: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  description: string;
  affected_components: string[];
  remediation: string;
  status: string;
}

interface SecuritySummary {
  summary: {
    active_incidents: number;
    open_vulnerabilities: number;
    recent_events: number;
    total_events: number;
  };
  incidents: SecurityIncident[];
  vulnerabilities: Vulnerability[];
  recent_events: SecurityEvent[];
}

export const SecurityDashboard: React.FC = () => {
  const [summary, setSummary] = useState<SecuritySummary | null>(null);
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [incidents, setIncidents] = useState<SecurityIncident[]>([]);
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const { toast } = useToast();

  useEffect(() => {
    fetchSecurityData();
  }, []);

  const fetchSecurityData = async () => {
    try {
      setLoading(true);
      
      const [summaryData, eventsData, incidentsData, vulnerabilitiesData] = await Promise.all([
        api.get('/security/summary'),
        api.get('/security/events?limit=100'),
        api.get('/security/incidents'),
        api.get('/security/vulnerabilities')
      ]);

      setSummary(summaryData);
      setEvents(eventsData.events || []);
      setIncidents(incidentsData.incidents || []);
      setVulnerabilities(vulnerabilitiesData.vulnerabilities || []);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch security data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleScanVulnerabilities = async () => {
    try {
      const result = await api.post('/security/vulnerabilities/scan');
      toast({
        title: "Success",
        description: `Scan completed. Found ${result.vulnerabilities_found} vulnerabilities`,
      });
      fetchSecurityData();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to scan vulnerabilities",
        variant: "destructive",
      });
    }
  };

  const handleGenerateReport = async () => {
    try {
      const report = await api.get('/security/audit-report');
      
      // Create and download report
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `security-audit-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      toast({
        title: "Success",
        description: "Security audit report downloaded",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate report",
        variant: "destructive",
      });
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'text-red-600';
      case 'investigating': return 'text-yellow-600';
      case 'contained': return 'text-blue-600';
      case 'resolved': return 'text-green-600';
      case 'closed': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  const filteredEvents = events.filter(event => 
    severityFilter === 'all' || event.severity === severityFilter
  );

  const filteredIncidents = incidents.filter(incident => 
    (severityFilter === 'all' || incident.severity === severityFilter) &&
    (statusFilter === 'all' || incident.status === statusFilter)
  );

  const filteredVulnerabilities = vulnerabilities.filter(vuln => 
    (severityFilter === 'all' || vuln.severity === severityFilter) &&
    (statusFilter === 'all' || vuln.status === statusFilter)
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Security Dashboard</h1>
        <div className="flex gap-2">
          <Button onClick={fetchSecurityData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={handleScanVulnerabilities} variant="outline">
            <Shield className="h-4 w-4 mr-2" />
            Scan Vulnerabilities
          </Button>
          <Button onClick={handleGenerateReport} variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Generate Report
          </Button>
        </div>
      </div>

      {/* Security Overview Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Active Incidents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{summary.summary.active_incidents}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Open Vulnerabilities</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{summary.summary.open_vulnerabilities}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Recent Events (24h)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{summary.summary.recent_events}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Total Events</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-600">{summary.summary.total_events}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-4">
        <div>
          <label className="text-sm font-medium">Severity Filter</label>
          <Select value={severityFilter} onValueChange={setSeverityFilter}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div>
          <label className="text-sm font-medium">Status Filter</label>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="open">Open</SelectItem>
              <SelectItem value="investigating">Investigating</SelectItem>
              <SelectItem value="contained">Contained</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
              <SelectItem value="closed">Closed</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="events">Security Events</TabsTrigger>
          <TabsTrigger value="incidents">Incidents</TabsTrigger>
          <TabsTrigger value="vulnerabilities">Vulnerabilities</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <Card>
            <CardHeader>
              <CardTitle>Security Overview</CardTitle>
              <CardDescription>Real-time security status and metrics</CardDescription>
            </CardHeader>
            <CardContent>
              {summary && (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Recent Critical Issues</h3>
                    {summary.incidents.slice(0, 5).map((incident) => (
                      <Alert key={incident.incident_id} className="mb-2">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertTitle>{incident.title}</AlertTitle>
                        <AlertDescription>
                          Severity: {incident.severity} | Status: {incident.status}
                        </AlertDescription>
                      </Alert>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="events">
          <Card>
            <CardHeader>
              <CardTitle>Security Events</CardTitle>
              <CardDescription>Recent security events and activities</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Event ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Severity</TableHead>
                    <TableHead>Source IP</TableHead>
                    <TableHead>User ID</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Timestamp</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredEvents.map((event) => (
                    <TableRow key={event.event_id}>
                      <TableCell className="font-mono text-sm">{event.event_id}</TableCell>
                      <TableCell>{event.event_type}</TableCell>
                      <TableCell>
                        <Badge className={getSeverityColor(event.severity)}>
                          {event.severity}
                        </Badge>
                      </TableCell>
                      <TableCell>{event.source_ip}</TableCell>
                      <TableCell>{event.user_id || '-'}</TableCell>
                      <TableCell>{event.description}</TableCell>
                      <TableCell>{new Date(event.timestamp).toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="incidents">
          <Card>
            <CardHeader>
              <CardTitle>Security Incidents</CardTitle>
              <CardDescription>Active and resolved security incidents</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Incident ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Severity</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Affected Users</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredIncidents.map((incident) => (
                    <TableRow key={incident.incident_id}>
                      <TableCell className="font-mono text-sm">{incident.incident_id}</TableCell>
                      <TableCell>{incident.incident_type}</TableCell>
                      <TableCell>
                        <Badge className={getSeverityColor(incident.severity)}>
                          {incident.severity}
                        </Badge>
                      </TableCell>
                      <TableCell>{incident.title}</TableCell>
                      <TableCell className={getStatusColor(incident.status)}>
                        {incident.status}
                      </TableCell>
                      <TableCell>{incident.affected_users}</TableCell>
                      <TableCell>{new Date(incident.created_at).toLocaleString()}</TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vulnerabilities">
          <Card>
            <CardHeader>
              <CardTitle>Vulnerabilities</CardTitle>
              <CardDescription>Security vulnerabilities and remediation steps</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Vulnerability ID</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Severity</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Components</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Discovered</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredVulnerabilities.map((vuln) => (
                    <TableRow key={vuln.vuln_id}>
                      <TableCell className="font-mono text-sm">{vuln.vuln_id}</TableCell>
                      <TableCell>{vuln.category}</TableCell>
                      <TableCell>
                        <Badge className={getSeverityColor(vuln.severity)}>
                          {vuln.severity}
                        </Badge>
                      </TableCell>
                      <TableCell>{vuln.description}</TableCell>
                      <TableCell>{vuln.affected_components.join(', ')}</TableCell>
                      <TableCell className={getStatusColor(vuln.status)}>
                        {vuln.status}
                      </TableCell>
                      <TableCell>{new Date(vuln.discovered_at).toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};