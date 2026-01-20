import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Bot, TrendingUp, Cloud, Truck } from 'lucide-react';

interface AgentResult {
  agent_id: string;
  task_id: string;
  result: any;
}

interface OrchestrationResult {
  workflow_id: string;
  market_analysis: AgentResult;
  weather_data: AgentResult;
  supply_chain: AgentResult;
}

export function AgentOrchestration() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OrchestrationResult | null>(null);
  const [fleetStatus, setFleetStatus] = useState<any>(null);

  const runOrchestration = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/agents/orchestrate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farmer_id: 'farmer_123',
          crop_type: 'rice',
          location: 'Dhaka, Bangladesh',
          season: 'monsoon'
        })
      });
      
      const data = await response.json();
      setResult(data.data);
    } catch (error) {
      console.error('Orchestration failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkFleetStatus = async () => {
    try {
      const response = await fetch('/api/agents/status');
      const data = await response.json();
      setFleetStatus(data.agents);
    } catch (error) {
      console.error('Failed to get fleet status:', error);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            Agent Fleet Orchestration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button onClick={runOrchestration} disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Run Agricultural Analysis
            </Button>
            <Button variant="outline" onClick={checkFleetStatus}>
              Check Fleet Status
            </Button>
          </div>

          {fleetStatus && (
            <div className="grid grid-cols-3 gap-4">
              {Object.entries(fleetStatus).map(([agentId, status]: [string, any]) => (
                <Card key={agentId}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{agentId}</span>
                      <Badge variant={status.status === 'idle' ? 'default' : 'secondary'}>
                        {status.status}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <TrendingUp className="h-4 w-4" />
                Market Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Trend:</span>
                  <Badge>{result.market_analysis.result.market_trend}</Badge>
                </div>
                <div className="flex justify-between">
                  <span>Price:</span>
                  <span>৳{result.market_analysis.result.price_prediction}</span>
                </div>
                <div className="flex justify-between">
                  <span>Demand:</span>
                  <Badge variant="secondary">{result.market_analysis.result.demand_forecast}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Cloud className="h-4 w-4" />
                Weather Data
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Temperature:</span>
                  <span>{result.weather_data.result.temperature}°C</span>
                </div>
                <div className="flex justify-between">
                  <span>Humidity:</span>
                  <span>{result.weather_data.result.humidity}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Rainfall:</span>
                  <Badge variant="outline">{result.weather_data.result.rainfall_forecast}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Truck className="h-4 w-4" />
                Supply Chain
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Status:</span>
                  <Badge>{result.supply_chain.result.logistics_status}</Badge>
                </div>
                <div className="flex justify-between">
                  <span>Delivery:</span>
                  <span>{result.supply_chain.result.delivery_time}</span>
                </div>
                <div className="flex justify-between">
                  <span>Cost:</span>
                  <span>৳{result.supply_chain.result.cost_estimate}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
