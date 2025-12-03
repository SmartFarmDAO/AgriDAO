import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TrendingUp, Star, Sparkles } from "lucide-react";
import { getTrendingProducts, getPopularProducts } from "@/lib/api";
import type { Product } from "@/types";

interface ProductRecommendationsProps {
  type: "trending" | "popular" | "for-you";
  limit?: number;
  onAddToCart?: (product: Product) => void;
}

export const ProductRecommendations = ({ 
  type, 
  limit = 6,
  onAddToCart 
}: ProductRecommendationsProps) => {
  const { data: products, isLoading } = useQuery<Product[]>({
    queryKey: ["recommendations", type, limit],
    queryFn: () => {
      if (type === "trending") return getTrendingProducts(7, limit);
      if (type === "popular") return getPopularProducts(limit);
      return getPopularProducts(limit); // Default to popular
    },
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </CardHeader>
            <CardContent>
              <div className="h-20 bg-gray-200 rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!products || products.length === 0) return null;

  const icon = type === "trending" ? <TrendingUp className="h-5 w-5" /> : 
               type === "popular" ? <Star className="h-5 w-5" /> : 
               <Sparkles className="h-5 w-5" />;

  const title = type === "trending" ? "Trending Now" : 
                type === "popular" ? "Popular Products" : 
                "Recommended for You";

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        {icon}
        <h2 className="text-2xl font-bold">{title}</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {products.map((product) => (
          <Card key={product.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="p-4">
              <CardTitle className="text-sm line-clamp-2">{product.name}</CardTitle>
              <div className="flex items-center justify-between mt-2">
                <span className="text-lg font-bold text-green-600">
                  ৳{Number(product.price).toFixed(2)}
                </span>
                {product.category && (
                  <Badge variant="secondary" className="text-xs">
                    {product.category}
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              {product.quantity_available > 0 ? (
                <Button 
                  size="sm" 
                  className="w-full"
                  onClick={() => onAddToCart?.(product)}
                >
                  Add to Cart
                </Button>
              ) : (
                <Badge variant="secondary" className="w-full justify-center">
                  Out of Stock
                </Badge>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
