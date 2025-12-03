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
import { ProductRecommendations } from "@/components/ProductRecommendations";
import { useTranslation } from "@/i18n/config";

const Index = () => {
  const { isAuthenticated } = useAuth();
  const { t, language } = useTranslation();
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
      titleKey: "home.features.directMarketplace.title",
      descriptionKey: "home.features.directMarketplace.description",
      gradient: "from-green-500 to-emerald-600",
    },
    {
      icon: DollarSign,
      titleKey: "home.features.ethicalFinancing.title",
      descriptionKey: "home.features.ethicalFinancing.description",
      gradient: "from-blue-500 to-cyan-600",
    },
    {
      icon: Brain,
      titleKey: "home.features.aiAdvisory.title",
      descriptionKey: "home.features.aiAdvisory.description",
      gradient: "from-purple-500 to-pink-600",
    },
    {
      icon: Package,
      titleKey: "home.features.supplyChainTracking.title",
      descriptionKey: "home.features.supplyChainTracking.description",
      gradient: "from-orange-500 to-red-600",
    },
    {
      icon: Vote,
      titleKey: "home.features.daoGovernance.title",
      descriptionKey: "home.features.daoGovernance.description",
      gradient: "from-indigo-500 to-purple-600",
    },
    {
      icon: Shield,
      titleKey: "home.features.secureTransparent.title",
      descriptionKey: "home.features.secureTransparent.description",
      gradient: "from-teal-500 to-green-600",
    },
  ];

  const stats = [
    { value: "1,000+", valueBn: "১,০০০+", label: t('home.activeFarmers'), icon: Users },
    { value: "৳5M+", valueBn: "৳৫০L+", label: t('home.totalFunded'), icon: TrendingUp },
    { value: "500+", valueBn: "৫০০+", label: t('home.productsListed'), icon: Package },
    { value: "98%", valueBn: "৯৮%", label: t('home.satisfactionRate'), icon: Star },
  ];

  const testimonials = [
    {
      nameKey: "home.testimonials.karim.name",
      roleKey: "home.testimonials.karim.role",
      contentKey: "home.testimonials.karim.content",
      rating: 5,
    },
    {
      nameKey: "home.testimonials.fatema.name",
      roleKey: "home.testimonials.fatema.role",
      contentKey: "home.testimonials.fatema.content",
      rating: 5,
    },
    {
      nameKey: "home.testimonials.rahman.name",
      roleKey: "home.testimonials.rahman.role",
      contentKey: "home.testimonials.rahman.content",
      rating: 5,
    },
  ];

  const benefits = [
    { icon: TrendingUp, textKey: "home.benefits.incomeIncrease" },
    { icon: Zap, textKey: "home.benefits.instantAccess" },
    { icon: Shield, textKey: "home.benefits.secureTransactions" },
    { icon: CheckCircle2, textKey: "home.benefits.transparentPricing" },
    { icon: Heart, textKey: "home.benefits.communitySupport" },
    { icon: Award, textKey: "home.benefits.qualityCertification" },
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
                {t('common.marketplace')}
              </Link>
              <Link to="/finance" className="text-gray-600 hover:text-green-600 transition-colors font-medium">
                {t('common.finance')}
              </Link>
              <Link to="/supply-chain" className="text-gray-600 hover:text-green-600 transition-colors font-medium">
                {t('common.supplyChain')}
              </Link>
              <Link to="/governance" className="text-gray-600 hover:text-green-600 transition-colors font-medium">
                {t('common.governance')}
              </Link>
            </div>
            <div className="flex items-center gap-3">
              <ConnectButton showBalance={false} chainStatus="icon" />
              {!isAuthenticated ? (
                <Link to="/auth">
                  <Button className="bg-green-600 hover:bg-green-700">{t('common.signIn')}</Button>
                </Link>
              ) : (
                <Link to="/dashboard">
                  <Button className="bg-green-600 hover:bg-green-700">{t('common.dashboard')}</Button>
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
              {t('home.platformBadge')}
            </Badge>
            <h1
              className={`text-5xl md:text-7xl font-bold mb-6 leading-tight transition-all duration-1000 ${
                isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
              }`}
            >
              {t('home.hero')}
              <span className="block bg-gradient-to-r from-green-600 via-blue-600 to-purple-600 bg-clip-text text-transparent">
                {t('home.subtitle')}
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-10 leading-relaxed max-w-3xl mx-auto">
              {t('home.description')}
            </p>
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              {!isAuthenticated ? (
                <>
                  <Link to="/auth">
                    <Button size="lg" className="bg-green-600 hover:bg-green-700 text-lg px-8 py-6 shadow-lg hover:shadow-xl transition-all">
                      {t('home.getStarted')}
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                  </Link>
                  <Link to="/marketplace">
                    <Button
                      size="lg"
                      variant="outline"
                      className="text-lg px-8 py-6 border-2 hover:bg-gray-50 transition-all"
                    >
                      {t('marketplace.title')}
                    </Button>
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/dashboard">
                    <Button size="lg" className="bg-green-600 hover:bg-green-700 text-lg px-8 py-6 shadow-lg">
                      {t('home.goToDashboard')}
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                  </Link>
                  <Link to="/marketplace">
                    <Button size="lg" variant="outline" className="text-lg px-8 py-6 border-2">
                      {t('home.browseProducts')}
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
                    <div className="text-3xl font-bold text-gray-900 mb-1">
                      {language === 'bn' ? stat.valueBn : stat.value}
                    </div>
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
            <Badge className="mb-4 bg-blue-100 text-blue-700 px-4 py-2">{t('home.platformFeatures')}</Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">{t('home.everythingYouNeed')}</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              {t('home.comprehensiveTools')}
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
                    {t(feature.titleKey)}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">{t(feature.descriptionKey)}</p>
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
              <h2 className="text-4xl md:text-5xl font-bold mb-4">{t('home.whyFarmersChoose')}</h2>
              <p className="text-xl text-green-100">
                {t('home.joinThousands')}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {benefits.map((benefit, i) => (
                <div
                  key={i}
                  className="flex items-center gap-4 bg-white/10 backdrop-blur-md rounded-xl p-6 hover:bg-white/20 transition-all duration-300 hover:scale-105"
                >
                  <benefit.icon className="h-8 w-8 flex-shrink-0" />
                  <span className="text-lg font-medium">{t(benefit.textKey)}</span>
                </div>
              ))}
            </div>

            <div className="mt-12 text-center">
              <Link to="/auth">
                <Button
                  size="lg"
                  className="bg-white text-green-600 hover:bg-gray-100 text-lg px-8 py-6 shadow-xl"
                >
                  {t('home.joinToday')}
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
            <Badge className="mb-4 bg-purple-100 text-purple-700 px-4 py-2">{t('home.successStories')}</Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">{t('home.whatFarmersSay')}</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              {t('home.realStories')}
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
                  "{t(testimonials[activeTestimonial].contentKey)}"
                </p>
                <div className="text-center">
                  <div className="font-bold text-xl text-gray-900">{t(testimonials[activeTestimonial].nameKey)}</div>
                  <div className="text-gray-600">{t(testimonials[activeTestimonial].roleKey)}</div>
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
            <Badge className="mb-4 bg-green-100 text-green-700 px-4 py-2">{t('home.steps.simpleProcess')}</Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">{t('home.steps.getStartedSteps')}</h2>
          </div>

          <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                titleKey: "home.steps.createAccount.title",
                descriptionKey: "home.steps.createAccount.description",
                icon: Users,
              },
              {
                step: "02",
                titleKey: "home.steps.listProducts.title",
                descriptionKey: "home.steps.listProducts.description",
                icon: Package,
              },
              {
                step: "03",
                titleKey: "home.steps.startSelling.title",
                descriptionKey: "home.steps.startSelling.description",
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
                <h3 className="text-2xl font-bold mb-3">{t(item.titleKey)}</h3>
                <p className="text-gray-600 leading-relaxed">{t(item.descriptionKey)}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-green-600 to-blue-600">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center text-white">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">{t('home.cta.readyToTransform')}</h2>
            <p className="text-xl mb-10 text-green-100">
              {t('home.cta.joinRevolution')}
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link to="/auth">
                <Button size="lg" className="bg-white text-green-600 hover:bg-gray-100 text-lg px-8 py-6 shadow-xl">
                  {t('home.cta.getStartedFree')}
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to="/marketplace">
                <Button
                  size="lg"
                  variant="outline"
                  className="border-2 border-white text-white hover:bg-white/10 text-lg px-8 py-6"
                >
                  {t('home.cta.explorePlatform')}
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Product Recommendations */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <ProductRecommendations type="trending" limit={6} />
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
              <p className="text-sm">{t('home.footer.tagline')}</p>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">{t('home.footer.platform')}</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/marketplace" className="hover:text-green-500 transition-colors">
                    {t('home.footer.marketplace')}
                  </Link>
                </li>
                <li>
                  <Link to="/finance" className="hover:text-green-500 transition-colors">
                    {t('home.footer.finance')}
                  </Link>
                </li>
                <li>
                  <Link to="/supply-chain" className="hover:text-green-500 transition-colors">
                    {t('home.footer.supplyChain')}
                  </Link>
                </li>
                <li>
                  <Link to="/governance" className="hover:text-green-500 transition-colors">
                    {t('home.footer.governance')}
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">{t('home.footer.resources')}</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/ai" className="hover:text-green-500 transition-colors">
                    {t('home.footer.aiAdvisory')}
                  </Link>
                </li>
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    {t('home.footer.documentation')}
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    {t('home.footer.support')}
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    {t('home.footer.blog')}
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">{t('home.footer.connect')}</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    {t('home.footer.twitter')}
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    {t('home.footer.facebook')}
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    {t('home.footer.linkedin')}
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-green-500 transition-colors">
                    {t('home.footer.contactUs')}
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>{t('home.footer.copyright')}</p>
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
