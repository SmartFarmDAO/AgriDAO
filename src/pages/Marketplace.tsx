import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Search, Filter, MapPin, Star, Plus } from "lucide-react";

const Marketplace = () => {
  const [searchQuery, setSearchQuery] = useState("");

  const featuredProducts = [
    {
      id: 1,
      name: "Organic Tomatoes",
      farmer: "Maria Santos",
      location: "California, USA",
      price: "$4.50/kg",
      rating: 4.8,
      image: "/placeholder.svg",
      category: "Vegetables",
      harvestDate: "2024-01-15",
      quantity: "500 kg",
      description: "Fresh organic tomatoes grown using sustainable farming practices.",
    },
    {
      id: 2,
      name: "Premium Rice",
      farmer: "Chen Wei",
      location: "Hunan, China",
      price: "$2.20/kg",
      rating: 4.9,
      image: "/placeholder.svg",
      category: "Grains",
      harvestDate: "2024-01-10",
      quantity: "2000 kg",
      description: "High-quality jasmine rice with excellent aroma and taste.",
    },
    {
      id: 3,
      name: "Free-Range Eggs",
      farmer: "John Smith",
      location: "Iowa, USA",
      price: "$0.80/dozen",
      rating: 4.7,
      image: "/placeholder.svg",
      category: "Dairy & Eggs",
      harvestDate: "2024-01-20",
      quantity: "100 dozen",
      description: "Fresh eggs from free-range chickens fed with organic grain.",
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link to="/">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Button>
          </Link>
          <div className="flex-1">
            <h1 className="text-3xl font-bold">AgriMarketplace</h1>
            <p className="text-muted-foreground">Direct connection between farmers and buyers</p>
          </div>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            List Product
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              placeholder="Search products, farmers, or locations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
        </div>

        {/* Marketplace Tabs */}
        <Tabs defaultValue="browse" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="browse">Browse Products</TabsTrigger>
            <TabsTrigger value="mylistings">My Listings</TabsTrigger>
            <TabsTrigger value="orders">Orders</TabsTrigger>
          </TabsList>

          <TabsContent value="browse" className="space-y-6">
            {/* Categories */}
            <div className="flex flex-wrap gap-2 mb-6">
              {["All", "Vegetables", "Fruits", "Grains", "Dairy & Eggs", "Herbs", "Organic"].map((category) => (
                <Badge key={category} variant={category === "All" ? "default" : "secondary"} className="cursor-pointer">
                  {category}
                </Badge>
              ))}
            </div>

            {/* Featured Products */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Featured Products</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {featuredProducts.map((product) => (
                  <Card key={product.id} className="hover:shadow-lg transition-shadow">
                    <div className="aspect-video bg-muted rounded-t-lg flex items-center justify-center">
                      <img src={product.image} alt={product.name} className="w-full h-full object-cover rounded-t-lg" />
                    </div>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">{product.name}</CardTitle>
                          <CardDescription>{product.description}</CardDescription>
                        </div>
                        <Badge variant="secondary">{product.category}</Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-2xl font-bold text-primary">{product.price}</span>
                          <div className="flex items-center gap-1">
                            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                            <span className="text-sm font-medium">{product.rating}</span>
                          </div>
                        </div>
                        
                        <div className="space-y-2 text-sm text-muted-foreground">
                          <div className="flex items-center gap-2">
                            <MapPin className="h-4 w-4" />
                            <span>{product.farmer} • {product.location}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Available: {product.quantity}</span>
                            <span>Harvest: {product.harvestDate}</span>
                          </div>
                        </div>

                        <div className="flex gap-2 pt-2">
                          <Button className="flex-1">Add to Cart</Button>
                          <Button variant="outline">Contact</Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="mylistings" className="space-y-6">
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                <Plus className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-2">No products listed yet</h3>
              <p className="text-muted-foreground mb-4">Start selling your farm products to the community</p>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create First Listing
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="orders" className="space-y-6">
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-2">No orders yet</h3>
              <p className="text-muted-foreground mb-4">Your purchase and sales orders will appear here</p>
              <Button variant="outline">Browse Products</Button>
            </div>
          </TabsContent>
        </Tabs>

        {/* Marketplace Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-12">
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-primary">1,247</div>
              <div className="text-sm text-muted-foreground">Active Farmers</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-primary">3,892</div>
              <div className="text-sm text-muted-foreground">Products Listed</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-primary">$2.1M</div>
              <div className="text-sm text-muted-foreground">Total Sales</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-2xl font-bold text-primary">98.2%</div>
              <div className="text-sm text-muted-foreground">Satisfaction Rate</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Marketplace;