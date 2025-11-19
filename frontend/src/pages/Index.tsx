import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Sprout, Users, DollarSign, Brain, Package, Vote } from "lucide-react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { useAuth } from "@/hooks/use-auth";

const Index = () => {
  const { isAuthenticated } = useAuth();
  const epics = [
    {
      title: "Farmer Identity & Onboarding",
      description: "Decentralized identity system for farmer verification and registration",
      icon: Users,
      path: "/farmer-onboarding",
      color: "text-green-600",
    },
    {
      title: "AgriMarketplace",
      description: "Direct marketplace connecting farmers with buyers and cooperatives",
      icon: Sprout,
      path: "/marketplace",
      color: "text-blue-600",
    },
    {
      title: "Ethical AgriFinance",
      description: "Interest-free funding through community donations and sponsorships",
      icon: DollarSign,
      path: "/finance",
      color: "text-purple-600",
    },
    {
      title: "AI Crop Advisory",
      description: "AI-powered assistance for weather, pricing, and yield predictions",
      icon: Brain,
      path: "/ai-advisory",
      color: "text-orange-600",
    },
    {
      title: "Supply Chain Tracking",
      description: "Blockchain-based tracking from farm to fork with QR codes",
      icon: Package,
      path: "/supply-chain",
      color: "text-teal-600",
    },
    {
      title: "DAO Governance",
      description: "Community-driven decision making for fund allocation and features",
      icon: Vote,
      path: "/governance",
      color: "text-indigo-600",
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
            AgriDAO
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
            Empowering small and medium-scale farmers through ethical financing, AI-powered advisory, 
            transparent supply chains, and decentralized governance.
          </p>
          <div className="flex flex-wrap justify-center gap-4 items-center">
            {!isAuthenticated ? (
              <>
                <Link to="/auth">
                  <Button size="lg" className="text-lg">
                    Get Started
                  </Button>
                </Link>
                <Button variant="outline" size="lg" className="text-lg">
                  Learn More
                </Button>
                <Link to="/auth">
                  <Button variant="secondary" size="lg" className="text-lg">
                    Sign In
                  </Button>
                </Link>
              </>
            ) : (
              <>
                <Link to="/dashboard">
                  <Button size="lg" className="text-lg">
                    Go to Dashboard
                  </Button>
                </Link>
                <Link to="/marketplace">
                  <Button variant="outline" size="lg" className="text-lg">
                    Browse Marketplace
                  </Button>
                </Link>
              </>
            )}
            <div className="mt-2">
              <ConnectButton showBalance={false} chainStatus="icon" />
            </div>
          </div>
        </div>

        {/* Epics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {epics.map((epic) => {
            const IconComponent = epic.icon;
            return (
              <Card key={epic.path} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <IconComponent className={`h-8 w-8 ${epic.color}`} />
                    <CardTitle className="text-lg">{epic.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="mb-4">
                    {epic.description}
                  </CardDescription>
                  <Link to={epic.path}>
                    <Button variant="outline" className="w-full">
                      Explore Epic
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Features Section */}
        <div className="mt-20 text-center">
          <h2 className="text-3xl font-bold mb-8">Why AgriDAO?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="space-y-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                <Sprout className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold">Ethical & Sustainable</h3>
              <p className="text-muted-foreground">
                Interest-free financing and sustainable farming practices that benefit both farmers and the environment.
              </p>
            </div>
            <div className="space-y-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                <Brain className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold">AI-Powered</h3>
              <p className="text-muted-foreground">
                Advanced AI provides weather alerts, market insights, and yield predictions to maximize farmer success.
              </p>
            </div>
            <div className="space-y-4">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto">
                <Vote className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold">Community Governed</h3>
              <p className="text-muted-foreground">
                Decentralized decision-making ensures the platform serves the real needs of the farming community.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;