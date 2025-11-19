import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, Heart, DollarSign, TrendingUp, Users, CheckCircle } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { donateToRequest, listFundingRequests, getFinanceMetrics, type FinanceMetrics } from "@/lib/api";
import type { FundingRequest } from "@/types";

const Finance = () => {
  const [selectedAmount, setSelectedAmount] = useState("");

  const queryClient = useQueryClient();
  const { data: fundingRequests, isLoading, isError } = useQuery<FundingRequest[]>({
    queryKey: ["fundingRequests"],
    queryFn: listFundingRequests,
  });

  const { data: metrics } = useQuery<FinanceMetrics>({
    queryKey: ["financeMetrics"],
    queryFn: getFinanceMetrics,
  });

  const donateMutation = useMutation({
    mutationFn: ({ id, amount }: { id: number; amount: number }) => donateToRequest(id, amount),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fundingRequests"] });
      setSelectedAmount("");
    },
  });

  const quickAmounts = [50, 100, 250, 500, 1000];

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link to="/dashboard">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
          <div className="flex-1">
            <h1 className="text-3xl font-bold">Ethical AgriFinance</h1>
            <p className="text-muted-foreground">Interest-free funding through community support</p>
          </div>
        </div>

        {/* Impact Stats (live metrics) */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-6 text-center">
              <Heart className="h-8 w-8 text-red-500 mx-auto mb-2" />
              <div className="text-2xl font-bold">${(metrics?.gmv ?? 0).toFixed(2)}</div>
              <div className="text-sm text-muted-foreground">GMV (Paid Orders)</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <Users className="h-8 w-8 text-blue-500 mx-auto mb-2" />
              <div className="text-2xl font-bold">{metrics?.orders_paid ?? 0}</div>
              <div className="text-sm text-muted-foreground">Paid Orders</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <TrendingUp className="h-8 w-8 text-green-500 mx-auto mb-2" />
              <div className="text-2xl font-bold">{((metrics?.take_rate ?? 0) * 100).toFixed(1)}%</div>
              <div className="text-sm text-muted-foreground">Take Rate</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <CheckCircle className="h-8 w-8 text-purple-500 mx-auto mb-2" />
              <div className="text-2xl font-bold">${(metrics?.fee_revenue ?? 0).toFixed(2)}</div>
              <div className="text-sm text-muted-foreground">Fee Revenue</div>
            </CardContent>
          </Card>
        </div>

        {/* Main Tabs */}
        <Tabs defaultValue="browse" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="browse">Browse Requests</TabsTrigger>
            <TabsTrigger value="request">Request Funding</TabsTrigger>
            <TabsTrigger value="mycontributions">My Contributions</TabsTrigger>
          </TabsList>

          <TabsContent value="browse" className="space-y-6">
            {/* Categories */}
            <div className="flex flex-wrap gap-2 mb-6">
              {["All", "Seeds & Supplies", "Equipment", "Infrastructure", "Emergency", "Education"].map((category) => (
                <Badge key={category} variant={category === "All" ? "default" : "secondary"} className="cursor-pointer">
                  {category}
                </Badge>
              ))}
            </div>

            {/* Funding Requests */}
            {isLoading && <p className="text-center py-8 text-muted-foreground">Loading funding requests...</p>}
            {isError && <p className="text-center py-8 text-red-600">Failed to load funding requests.</p>}
            {!isLoading && !isError && (!fundingRequests || fundingRequests.length === 0) && (
              <div className="text-center py-12">
                <Heart className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">No funding requests yet</h3>
                <p className="text-muted-foreground">Be the first to request funding for your farm</p>
              </div>
            )}
            {!isLoading && !isError && fundingRequests && fundingRequests.length > 0 && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {fundingRequests.map((request) => {
                const progressPercentage = (request.amount_raised / request.amount_needed) * 100;
                const isCompleted = request.status === "Funded";

                return (
                  <Card key={request.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">{request.purpose}</CardTitle>
                          <CardDescription>by {request.farmer_name} • {request.location}</CardDescription>
                        </div>
                        <Badge variant={isCompleted ? "default" : "secondary"}>
                          {isCompleted ? "Funded" : request.category}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-sm text-muted-foreground">{request.description}</p>
                      
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>${request.amount_raised} raised</span>
                          <span>${request.amount_needed} goal</span>
                        </div>
                        <Progress value={progressPercentage} className="h-2" />
                        <div className="flex justify-between text-sm text-muted-foreground">
                          <span>{Math.round(progressPercentage)}% funded</span>
                          <span>{isCompleted ? "Completed" : `${request.days_left} days left`}</span>
                        </div>
                      </div>

                      {!isCompleted && (
                        <div className="space-y-3 pt-2">
                          <div className="flex gap-2">
                            {quickAmounts.map((amount) => (
                              <Button 
                                key={amount} 
                                variant="outline" 
                                size="sm"
                                onClick={() => setSelectedAmount(amount.toString())}
                                className={selectedAmount === amount.toString() ? "bg-primary text-primary-foreground" : ""}
                              >
                                ${amount}
                              </Button>
                            ))}
                          </div>
                          <div className="flex gap-2">
                            <Input
                              placeholder="Custom amount"
                              value={selectedAmount}
                              onChange={(e) => setSelectedAmount(e.target.value)}
                              type="number"
                            />
                            <Button className="whitespace-nowrap">
                              <Heart className="h-4 w-4 mr-2" />
                              Donate
                            </Button>
                          </div>
                        </div>
                      )}

                      {isCompleted && (
                        <div className="bg-green-50 p-3 rounded-lg text-center">
                          <CheckCircle className="h-5 w-5 text-green-500 mx-auto mb-1" />
                          <p className="text-sm text-green-700 font-medium">Successfully Funded!</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
            )}
          </TabsContent>

          <TabsContent value="request" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Request Ethical Funding</CardTitle>
                <CardDescription>
                  Submit a funding request for your agricultural needs. All funding is interest-free and community-supported.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="purpose">Purpose of Funding</Label>
                    <Input id="purpose" placeholder="e.g., Organic Seeds Purchase" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="amount">Amount Needed ($)</Label>
                    <Input id="amount" placeholder="2500" type="number" />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Detailed Description</Label>
                  <textarea 
                    id="description"
                    className="w-full min-h-24 px-3 py-2 border border-input rounded-md resize-none"
                    placeholder="Explain how the funding will be used and the expected impact on your farm..."
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="category">Category</Label>
                    <select id="category" className="w-full px-3 py-2 border border-input rounded-md">
                      <option>Seeds & Supplies</option>
                      <option>Equipment</option>
                      <option>Infrastructure</option>
                      <option>Emergency</option>
                      <option>Education</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="timeline">Timeline (days)</Label>
                    <Input id="timeline" placeholder="30" type="number" />
                  </div>
                </div>

                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-blue-900 mb-2">Ethical Funding Principles</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Interest-free: No interest charges or hidden fees</li>
                    <li>• Community-driven: Funded by fellow farmers and supporters</li>
                    <li>• Transparent: All transactions recorded on blockchain</li>
                    <li>• Accountable: Regular progress updates required</li>
                  </ul>
                </div>

                <Button className="w-full">Submit Funding Request</Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="mycontributions" className="space-y-6">
            <div className="text-center py-12">
              <Heart className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No contributions yet</h3>
              <p className="text-muted-foreground mb-4">Start supporting farmers in your community</p>
              <Button>Browse Funding Requests</Button>
            </div>
          </TabsContent>
        </Tabs>

        {/* How It Works */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-center mb-8">How Ethical Financing Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                <DollarSign className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold">Community Donations</h3>
              <p className="text-muted-foreground">
                Supporters contribute to a shared fund pool that helps farmers access resources without interest.
              </p>
            </div>
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                <Users className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold">Smart Contract Distribution</h3>
              <p className="text-muted-foreground">
                Blockchain technology ensures transparent, automated fund distribution based on community approval.
              </p>
            </div>
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto">
                <TrendingUp className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold">Impact Tracking</h3>
              <p className="text-muted-foreground">
                Monitor the real-world impact of funding through transparent reporting and blockchain records.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Finance;