import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Sprout,
  Users,
  DollarSign,
  Brain,
  Package,
  Vote,
  ArrowRight,
  TrendingUp,
  Shield,
  Zap,
  CheckCircle2,
  Star,
  Globe,
  Leaf,
  Heart,
  Award,
} from "lucide-react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { useAuth } from "@/hooks/use-auth";
import { useState, useEffect } from "react";

const Index = () => {
  const { isAuthenticated } = useAuth();
  const [activeTestimonial, setActiveTestimonial] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setActiveTestimonial((prev) => (prev + 1) % 3);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const features = [
    {
      icon: Sprout,
      title: "Direct Marketplace",
      description: "Connect directly with buyers and eliminate middlemen. Get fair prices for your produce.",
      gradient: "from-green-500 to-emerald-600",
    },
    {
      icon: DollarSign,
      title: "Ethical Financing",
      description: "Access interest-free funding through community donations and transparent sponsorships.",
      gradient: "from-blue-500 to-cyan-600",
    },
    {
      icon: Brain,
      title: "AI Advisory",
      description: "Get real-time weather alerts, market insights, and yield predictions powered by AI.",
      gradient: "from-purple-500 to-pink-600",
    },
    {
      icon: Package,
      title: "Supply Chain Tracking",
      description: "Blockchain-based tracking ensures transparency from farm to consumer with QR codes.",
      gradient: "from-orange-500 to-red-600",
    },
    {
      icon: Vote,
      title: "DAO Governance",
      description: "Participate in platform decisions and vote on fund allocation and new features.",
      gradient: "from-indigo-500 to-purple-600",
    },
    {
      icon: Shield,
      title: "Secure & Transparent",
      description: "All transactions are secured on blockchain with complete transparency and traceability.",
      gradient: "from-teal-500 to-green-600",
    },
  ];

  const stats = [
    { value: "1,000+", label: "Active Farmers", icon: Users },
    { value: "৳5M+", label: "Total Funded", icon: TrendingUp },
    { value: "500+", label: "Products Listed", icon: Package },
    { value: "98%", label: "Satisfaction Rate", icon: Star },
  ];

  const testimonials = [
    {
      name: "Md. Karim",
      role: "Rice Farmer, Dinajpur",
      content: "AgriDAO helped me get fair prices for my rice. The AI advisory saved my crop from pest damage. My income increased by 45%!",
      rating: 5,
    },
    {
      name: "Fatema Begum",
      role: "Vegetable Farmer, Jessore",
      content: "The interest-free funding helped me expand my farm. Now I sell directly to buyers through the marketplace. Life-changing!",
      rating: 5,
    },
    {
      name: "Abdul Rahman",
      role: "Fruit Farmer, Rajshahi",
      content: "Supply chain tracking gave my products credibility. Buyers trust the blockchain verification. Sales doubled in 6 months!",
      rating: 5,
    },
  ];

  const benefits = [
    { icon: TrendingUp, text: "40% average income increase" },
    { icon: Zap, text: "Instant market access" },
    { icon: Shield, text: "Secure blockchain transactions" },
    { icon: CheckCircle2, text: "Transparent pricing" },
    { icon: Heart, text: "Community support" },
    { icon: Award, text: "Quality certification" },
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation Bar */}
      <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Leaf className="h-8 w-8 text-green-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                AgriDAO
              </span>
            </div>
            <div className="hidden md:flex items-center gap-6">
              <Link to="/marketplace" className="text-gray-600 hover:text-green-600 transition-colors font-medium">
                Marketplace
              </Link>
              <Link to="/finance" className="text-gray-600 hover:text-green-600 transition-colors font-medium">
                Finance
              </Link>
              <Link to="/supply-chain" className="text-gray-600 hover:text-green-600 transition-colors font-medium">
                Supply Chain
              </Link>
              <Link to="/governance" className="text-gray-600 hover:text-green-600 transition-colors font-medium">
                Governance
              </Link>
            </div>
            <div className="flex items-center gap-3">
              <ConnectButton showBalance={false} chainStatus="icon" />
              {!isAuthenticated ? (
                <Link to="/auth">
                  <Button className="bg-green-600 hover:bg-green-700">Sign In</Button>
                </Link>
              ) : (
                <Link to="/dashboard">
                  <Button className="bg-green-600 hover:bg-green-700">Dashboard</Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 py-20 md:py-32">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        <div className="container mx-auto px-4 relative">
          <div className="max-w-4xl mx-auto text-center">
            <Badge className="mb-6 bg-green-100 text-green-700 hover:bg-green-200 px-4 py-2 text-sm font-semibold">
              <Globe className="h-4 w-4 mr-2 inline" />
              Blockchain-Powered Agricultural Platform
            </Badge>
            <h1
              className={`text-5xl md:text-7xl font-bold mb-6 leading-tight transition-all duration-1000 ${
                isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
              }`}
            >
              Empowering Farmers Through
              <span className="block bg-gradient-to-r from-green-600 via-blue-600 to-purple-600 bg-clip-text text-transparent">
                Technology & Community
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-10 leading-relaxed max-w-3xl mx-auto">
              Join Bangladesh's first decentralized agricultural platform. Get fair prices, access ethical financing,
              and leverage AI-powered insights to grow your farm.
            </p>
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              {!isAuthenticated ? (
                <>
                  <Link to="/auth">
                    <Button size="lg" className="bg-green-600 hover:bg-green-700 text-lg px-8 py-6 shadow-lg hover:shadow-xl transition-all">
                      Start Your Journey
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                  </Link>
                  <Link to="/marketplace">
                    <Button
                      size="lg"
                      variant="outline"
                      className="text-lg px-8 py-6 border-2 hover:bg-gray-50 transition-all"
                    >
                      Explore Marketplace
                    </Button>
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/dashboard">
                    <Button size="lg" className="bg-green-600 hover:bg-green-700 text-lg px-8 py-6 shadow-lg">
                      Go to Dashboard
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                  </Link>
                  <Link to="/marketplace">
                    <Button size="lg" variant="outline" className="text-lg px-8 py-6 border-2">
                      Browse Products
                    </Button>
                  </Link>
                </>
              )}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
              {stats.map((stat, i) => (
                <Card
                  key={i}
                  className="border-none shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                >
                  <CardContent className="p-6 text-center">
                    <stat.icon className="h-8 w-8 text-green-600 mx-auto mb-3" />
                    <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
                    <div className="text-sm text-gray-600">{stat.label}</div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-blue-100 text-blue-700 px-4 py-2">Platform Features</Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Everything You Need to Succeed</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Comprehensive tools and services designed specifically for small and medium-scale farmers
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, i) => (
              <Card
                key={i}
                className="group border-2 hover:border-green-200 transition-all duration-300 hover:shadow-2xl hover:-translate-y-2 cursor-pointer"
              >
                <CardContent className="p-8">
                  <div
                    className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg`}
                  >
                    <feature.icon className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold mb-3 group-hover:text-green-600 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-gradient-to-br from-green-600 via-blue-600 to-purple-600 text-white">
        <div className="container mx-auto px-4">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl md:text-5xl font-bold mb-4">Why Farmers Choose AgriDAO</h2>
              <p className="text-xl text-green-100">
                Join thousands of farmers who have transformed their agricultural business
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {benefits.map((benefit, i) => (
                <div
                  key={i}
                  className="flex items-center gap-4 bg-white/10 backdrop-blur-md rounded-xl p-6 hover:bg-white/20 transition-all duration-300 hover:scale-105"
                >
                  <benefit.icon className="h-8 w-8 flex-shrink-0" />
                  <span className="text-lg font-medium">{benefit.text}</span>
                </div>
              ))}
            </div>

            <div className="mt-12 text-center">
              <Link to="/auth">
                <Button
                  size="lg"
                  className="bg-white text-green-600 hover:bg-gray-100 text-lg px-8 py-6 shadow-xl"
                >
                  Join AgriDAO Today
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-purple-100 text-purple-700 px-4 py-2">Success Stories</Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">What Farmers Say About Us</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Real stories from real farmers who have transformed their lives with AgriDAO
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <Card className="border-none shadow-2xl">
              <CardContent className="p-12">
                <div className="flex justify-center mb-6">
                  {[...Array(testimonials[activeTestimonial].rating)].map((_, i) => (
                    <Star key={i} className="h-6 w-6 text-yellow-400 fill-yellow-400" />
                  ))}
                </div>
                <p className="text-2xl text-gray-700 mb-8 text-center leading-relaxed italic">
                  "{testimonials[activeTestimonial].content}"
                </p>
                <div className="text-center">
                  <div className="font-bold text-xl text-gray-900">{testimonials[activeTestimonial].name}</div>
                  <div className="text-gray-600">{testimonials[activeTestimonial].role}</div>
                </div>
                <div className="flex justify-center gap-2 mt-8">
                  {testimonials.map((_, i) => (
                    <button
                      key={i}
                      onClick={() => setActiveTestimonial(i)}
                      className={`w-3 h-3 rounded-full transition-all ${
                        i === activeTestimonial ? "bg-green-600 w-8" : "bg-gray-300"
                      }`}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-green-100 text-green-700 px-4 py-2">Simple Process</Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Get Started in 3 Easy Steps</h2>
          </div>

          <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Create Account",
                description: "Sign up and complete your farmer profile with verification",
                icon: Users,
              },
              {
                step: "02",
                title: "List Products",
                description: "Add your products to the marketplace with photos and details",
                icon: Package,
              },
              {
                step: "03",
                title: "Start Selling",
                description: "Connect with buyers and receive payments directly",
                icon: TrendingUp,
              },
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="relative mb-6">
                  <div className="w-24 h-24 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center mx-auto shadow-xl">
                    <item.icon className="h-12 w-12 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-12 h-12 bg-green-600 text-white rounded-full flex items-center justify-center font-bold text-lg shadow-lg">
                    {item.step}
                  </div>
                </div>
                <h3 className="text-2xl font-bold mb-3">{item.title}</h3>
                <p className="text-gray-600 leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-green-600 to-blue-600">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center text-white">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">Ready to Transform Your Farm?</h2>
            <p className="text-xl mb-10 text-green-100">
              Join AgriDAO today and become part of Bangladesh's agricultural revolution
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link to="/auth">
                <Button size="lg" className="bg-white text-green-600 hover:bg-gray-100 text-lg px-8 py-6 shadow-xl">
                  Get Started Free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to="/marketplace">
                <Button
                  size="lg"
                  variant="outline"
                  className="border-2 border-white text-white hover:bg-white/10 text-lg px-8 py-6"
                >
                  Explore Platform
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Leaf className="h-6 w-6 text-green-500" />
                <span className="text-xl font-bold text-white">AgriDAO</span>
              </div>
              <p className="text-sm">Empowering farmers through blockchain technology and community support.</p>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Platform</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/marketplace" className="hover:text-green-500 transition-colors">
                    Marketplace
                  </Link>
                </li>
                <li>
                  <Link to="/finance" className="hover:text-green-500 transition-colors">
                    Finance
                  </Link>
                </li>
                <li>
                  <Link to="/supply-chain" className="hover:text-green-500 transition-colors">
                    Supply Chain
                  </Link>
                </li>
                <li>
                  <Link to="/governance" className="hover:text-green-500 transition-colors">
                    Governance
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Resources</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/ai" className="hover:text-green-500 transition-colors">
                    AI Advisory
                  </Link>
                </li>
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    Documentation
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    Support
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    Blog
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Connect</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    Twitter
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    Facebook
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    LinkedIn
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    Contact Us
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>&copy; 2025 AgriDAO. All rights reserved. Built with ❤️ for farmers in Bangladesh.</p>
          </div>
        </div>
      </footer>

      <style>{`
        .bg-grid-pattern {
          background-image: linear-gradient(rgba(0, 0, 0, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
          background-size: 50px 50px;
        }
      `}</style>
    </div>
  );
};

export default Index;
