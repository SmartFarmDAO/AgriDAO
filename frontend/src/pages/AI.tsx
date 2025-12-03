import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Brain, Cloud, TrendingUp, Calculator, MessageSquare, Leaf } from "lucide-react";
import { useTranslation } from "@/i18n/config";

const AI = () => {
  const { t } = useTranslation();
  const [cropAdvice, setCropAdvice] = useState<string>("");
  const [priceAnalysis, setPriceAnalysis] = useState<string>("");
  const [yieldEstimate, setYieldEstimate] = useState<string>("");
  const [chatResponse, setChatResponse] = useState<string>("");

  // Crop Advisory AI
  const getCropAdvice = (crop: string, location: string, season: string) => {
    const advice = {
      rice: {
        planting: "Plant rice during monsoon season (June-July). Ensure proper water management.",
        care: "Maintain 2-3 inches of water. Apply nitrogen fertilizer in 3 splits.",
        harvest: "Harvest when 80% grains turn golden yellow (120-150 days).",
        pests: "Watch for stem borers and leaf folders. Use neem-based pesticides.",
      },
      wheat: {
        planting: "Sow wheat in November-December. Use 100-120 kg seeds per hectare.",
        care: "Irrigate at crown root, tillering, and grain filling stages.",
        harvest: "Harvest when moisture content is 20-25% (130-150 days).",
        pests: "Monitor for aphids and rust. Apply recommended fungicides.",
      },
      tomato: {
        planting: "Plant tomatoes in well-drained soil. Space plants 60cm apart.",
        care: "Water regularly but avoid waterlogging. Stake plants for support.",
        harvest: "Harvest when fruits are firm and fully colored (60-80 days).",
        pests: "Control whiteflies and fruit borers with organic pesticides.",
      },
      potato: {
        planting: "Plant seed potatoes in October-November. Use certified seeds.",
        care: "Earth up plants twice. Apply balanced NPK fertilizer.",
        harvest: "Harvest when leaves turn yellow (90-120 days).",
        pests: "Prevent late blight with copper-based fungicides.",
      },
    };

    const cropLower = crop.toLowerCase();
    const cropData = advice[cropLower as keyof typeof advice] || advice.rice;

    return `🌾 **${crop.toUpperCase()} Farming Guide for ${location}**

📍 **Planting:** ${cropData.planting}

💧 **Care:** ${cropData.care}

🌾 **Harvest:** ${cropData.harvest}

🐛 **Pest Control:** ${cropData.pests}

🌡️ **Season Tip:** ${season === 'monsoon' ? 'Ensure proper drainage' : season === 'winter' ? 'Protect from frost' : 'Provide adequate irrigation'}`;
  };

  // Price Prediction AI
  const analyzePriceMarket = (product: string, quantity: number) => {
    const basePrice = {
      rice: 25,
      wheat: 22,
      tomato: 30,
      potato: 18,
      onion: 20,
      corn: 20,
    };

    const price = basePrice[product.toLowerCase() as keyof typeof basePrice] || 25;
    const total = price * quantity;
    const trend = Math.random() > 0.5 ? 'increasing' : 'stable';
    const forecast = trend === 'increasing' ? price * 1.1 : price;

    return `📊 **Market Analysis for ${product}**

💰 **Current Price:** ৳${price}/kg
📦 **Your Quantity:** ${quantity} kg
💵 **Estimated Value:** ৳${total.toFixed(2)}

📈 **Market Trend:** ${trend.toUpperCase()}
🔮 **7-Day Forecast:** ৳${forecast.toFixed(2)}/kg

💡 **Recommendation:** ${trend === 'increasing' ? 'Hold for better prices' : 'Good time to sell'}

🎯 **Best Markets:** Dhaka (৳${(price * 1.15).toFixed(2)}), Chittagong (৳${(price * 1.1).toFixed(2)}), Sylhet (৳${(price * 1.05).toFixed(2)})`;
  };

  // Yield Calculator AI
  const calculateYield = (crop: string, area: number, soilQuality: string) => {
    const yieldPerHectare = {
      rice: 4.5,
      wheat: 3.5,
      tomato: 25,
      potato: 20,
      corn: 5,
    };

    const baseYield = yieldPerHectare[crop.toLowerCase() as keyof typeof yieldPerHectare] || 4;
    const qualityMultiplier = soilQuality === 'good' ? 1.2 : soilQuality === 'average' ? 1.0 : 0.8;
    const expectedYield = baseYield * area * qualityMultiplier;

    return `🌾 **Yield Estimation for ${crop}**

📏 **Farm Area:** ${area} hectares
🌱 **Soil Quality:** ${soilQuality.toUpperCase()}

📊 **Expected Yield:** ${expectedYield.toFixed(2)} tons
📈 **Per Hectare:** ${(expectedYield / area).toFixed(2)} tons/ha

💰 **Revenue Estimate:** ৳${(expectedYield * 1000 * 25).toLocaleString()}
💵 **Cost Estimate:** ৳${(area * 50000).toLocaleString()}
📊 **Profit Estimate:** ৳${(expectedYield * 1000 * 25 - area * 50000).toLocaleString()}

💡 **Tips to Improve:**
• Use quality seeds (certified)
• Apply balanced fertilizers
• Ensure proper irrigation
• Control pests early`;
  };

  // AI Chatbot
  const getAIResponse = (question: string) => {
    const q = question.toLowerCase();
    
    if (q.includes('weather') || q.includes('rain')) {
      return "🌦️ For accurate weather forecasts, check local meteorological services. Generally, monsoon season (June-September) brings heavy rainfall. Plan your planting accordingly!";
    }
    if (q.includes('fertilizer') || q.includes('nutrient')) {
      return "🌱 Use NPK fertilizers based on soil test. General recommendation: N:P:K = 120:60:40 kg/ha for rice. Organic options: compost, vermicompost, green manure.";
    }
    if (q.includes('pest') || q.includes('disease')) {
      return "🐛 Common pests: stem borers, aphids, whiteflies. Use integrated pest management (IPM): neem oil, pheromone traps, biological control. Avoid excessive pesticides.";
    }
    if (q.includes('price') || q.includes('sell')) {
      return "💰 Check daily market prices on our Marketplace. Sell directly to buyers to get better prices. Consider value addition (processing, packaging) for higher profits.";
    }
    if (q.includes('loan') || q.includes('fund')) {
      return "💵 Visit our Finance page for interest-free funding options. Community members can support your farming projects through donations.";
    }
    if (q.includes('organic')) {
      return "🌿 Organic farming tips: Use compost, crop rotation, green manure, biological pest control. Organic products fetch 20-30% premium prices!";
    }
    
    return "🤖 I can help with: weather advice, fertilizer recommendations, pest control, market prices, funding options, and organic farming. Ask me anything!";
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">🤖 AI Assistant</h1>
        <p className="text-gray-600">Free AI-powered tools to help you make better farming decisions</p>
      </div>

      <Tabs defaultValue="advisor" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4">
          <TabsTrigger value="advisor" className="flex items-center gap-2">
            <Leaf className="h-4 w-4" />
            Crop Advisor
          </TabsTrigger>
          <TabsTrigger value="price" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Price Analysis
          </TabsTrigger>
          <TabsTrigger value="yield" className="flex items-center gap-2">
            <Calculator className="h-4 w-4" />
            Yield Calculator
          </TabsTrigger>
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            AI Chat
          </TabsTrigger>
        </TabsList>

        {/* Crop Advisor */}
        <TabsContent value="advisor">
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Leaf className="h-5 w-5 text-green-600" />
                  Crop Advisory
                </CardTitle>
                <CardDescription>Get personalized farming advice for your crop</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.currentTarget);
                  const advice = getCropAdvice(
                    formData.get('crop') as string,
                    formData.get('location') as string,
                    formData.get('season') as string
                  );
                  setCropAdvice(advice);
                }} className="space-y-4">
                  <div>
                    <Label htmlFor="crop">Crop Type</Label>
                    <Input id="crop" name="crop" placeholder="e.g., Rice, Wheat, Tomato" required />
                  </div>
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input id="location" name="location" placeholder="e.g., Dhaka, Chittagong" required />
                  </div>
                  <div>
                    <Label htmlFor="season">Season</Label>
                    <select id="season" name="season" className="w-full p-2 border rounded" required>
                      <option value="monsoon">Monsoon (June-Sep)</option>
                      <option value="winter">Winter (Oct-Feb)</option>
                      <option value="summer">Summer (Mar-May)</option>
                    </select>
                  </div>
                  <Button type="submit" className="w-full">Get Advice</Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                {cropAdvice ? (
                  <div className="whitespace-pre-line text-sm">{cropAdvice}</div>
                ) : (
                  <p className="text-gray-500">Enter crop details to get personalized advice</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Price Analysis */}
        <TabsContent value="price">
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-blue-600" />
                  Market Price Analysis
                </CardTitle>
                <CardDescription>Analyze market trends and get price predictions</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.currentTarget);
                  const analysis = analyzePriceMarket(
                    formData.get('product') as string,
                    Number(formData.get('quantity'))
                  );
                  setPriceAnalysis(analysis);
                }} className="space-y-4">
                  <div>
                    <Label htmlFor="product">Product</Label>
                    <Input id="product" name="product" placeholder="e.g., Rice, Tomato" required />
                  </div>
                  <div>
                    <Label htmlFor="quantity">Quantity (kg)</Label>
                    <Input id="quantity" name="quantity" type="number" placeholder="e.g., 1000" required />
                  </div>
                  <Button type="submit" className="w-full">Analyze Market</Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Market Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                {priceAnalysis ? (
                  <div className="whitespace-pre-line text-sm">{priceAnalysis}</div>
                ) : (
                  <p className="text-gray-500">Enter product details to get market analysis</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Yield Calculator */}
        <TabsContent value="yield">
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="h-5 w-5 text-purple-600" />
                  Yield Estimator
                </CardTitle>
                <CardDescription>Calculate expected harvest and revenue</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.currentTarget);
                  const estimate = calculateYield(
                    formData.get('cropType') as string,
                    Number(formData.get('area')),
                    formData.get('soilQuality') as string
                  );
                  setYieldEstimate(estimate);
                }} className="space-y-4">
                  <div>
                    <Label htmlFor="cropType">Crop Type</Label>
                    <Input id="cropType" name="cropType" placeholder="e.g., Rice, Wheat" required />
                  </div>
                  <div>
                    <Label htmlFor="area">Farm Area (hectares)</Label>
                    <Input id="area" name="area" type="number" step="0.1" placeholder="e.g., 2.5" required />
                  </div>
                  <div>
                    <Label htmlFor="soilQuality">Soil Quality</Label>
                    <select id="soilQuality" name="soilQuality" className="w-full p-2 border rounded" required>
                      <option value="good">Good</option>
                      <option value="average">Average</option>
                      <option value="poor">Poor</option>
                    </select>
                  </div>
                  <Button type="submit" className="w-full">Calculate Yield</Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Yield Estimation</CardTitle>
              </CardHeader>
              <CardContent>
                {yieldEstimate ? (
                  <div className="whitespace-pre-line text-sm">{yieldEstimate}</div>
                ) : (
                  <p className="text-gray-500">Enter farm details to estimate yield</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* AI Chat */}
        <TabsContent value="chat">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-green-600" />
                AI Farming Assistant
              </CardTitle>
              <CardDescription>Ask me anything about farming, markets, or AgriDAO</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                const question = formData.get('question') as string;
                const response = getAIResponse(question);
                setChatResponse(response);
                e.currentTarget.reset();
              }} className="space-y-4">
                <div>
                  <Label htmlFor="question">Your Question</Label>
                  <Textarea 
                    id="question" 
                    name="question" 
                    placeholder="e.g., What fertilizer should I use for rice?" 
                    rows={3}
                    required 
                  />
                </div>
                <Button type="submit" className="w-full">Ask AI</Button>
              </form>

              {chatResponse && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm font-semibold text-green-800 mb-2">AI Response:</p>
                  <p className="text-sm text-gray-700">{chatResponse}</p>
                </div>
              )}

              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm font-semibold text-blue-800 mb-2">💡 Quick Tips:</p>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Ask about weather, fertilizers, pests, prices, or funding</li>
                  <li>• Get organic farming advice</li>
                  <li>• Learn about market trends</li>
                  <li>• Discover best farming practices</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AI;
