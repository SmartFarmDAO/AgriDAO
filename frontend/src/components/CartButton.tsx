import { Button } from "@/components/ui/button";
import { ShoppingCart, Minus, Plus, Trash2 } from "lucide-react";
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerTrigger, DrawerFooter, DrawerClose } from "@/components/ui/drawer";
import { useNavigate } from "react-router-dom";
import { CartItem } from "@/contexts/CartContext";

type CartButtonProps = {
  cartCount: number;
  cartItems: CartItem[];
  cartTotal: number;
  onCheckout?: () => void;
  onUpdateQuantity: (productId: number, quantity: number) => void;
  onRemoveItem: (productId: number) => void;
};

export function CartButton({
  cartCount,
  cartItems,
  cartTotal,
  onCheckout,
  onUpdateQuantity,
  onRemoveItem
}: CartButtonProps) {
  const navigate = useNavigate();

  const handleCheckout = () => {
    if (onCheckout) {
      onCheckout();
    } else {
      navigate('/marketplace');
    }
  };

  const handleIncrement = (item: CartItem) => {
    onUpdateQuantity(item.product.id, item.quantity + 1);
  };

  const handleDecrement = (item: CartItem) => {
    if (item.quantity > 1) {
      onUpdateQuantity(item.product.id, item.quantity - 1);
    } else {
      onRemoveItem(item.product.id);
    }
  };

  const formatPrice = (price: string | number) => {
    const num = typeof price === 'number' ? price : parseFloat(price);
    return isNaN(num) ? "0.00" : num.toFixed(2);
  };

  return (
    <Drawer>
      <DrawerTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <ShoppingCart className="h-5 w-5 text-gray-600" />
          {cartCount > 0 && (
            <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-gradient-to-r from-green-600 to-blue-600 text-xs font-medium text-white">
              {cartCount}
            </span>
          )}
          <span className="sr-only">Cart</span>
        </Button>
      </DrawerTrigger>
      <DrawerContent className="max-h-[80vh]">
        <DrawerHeader className="border-b">
          <DrawerTitle className="text-lg font-semibold">Your Cart</DrawerTitle>
        </DrawerHeader>
        <div className="overflow-y-auto p-4 space-y-4">
          {cartItems.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <ShoppingCart className="h-12 w-12 text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900">Your cart is empty</h3>
              <p className="mt-1 text-sm text-gray-500">Start adding some products to your cart</p>
              <DrawerClose asChild>
                <Button className="mt-4" variant="outline">
                  Continue Shopping
                </Button>
              </DrawerClose>
            </div>
          ) : (
            <>
              <div className="space-y-4">
                {cartItems.map((item) => (
                  <div key={item.product.id} className="flex items-start justify-between gap-4 p-3 rounded-lg border">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{item.product.name}</h4>
                      <p className="text-sm text-gray-600">৳{formatPrice(item.product.price)} each</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm" className="h-8 w-8 p-0" onClick={() => handleDecrement(item)}>
                        {item.quantity === 1 ? <Trash2 className="h-3 w-3" /> : <Minus className="h-3 w-3" />}
                      </Button>
                      <span className="w-6 text-center text-sm">{item.quantity}</span>
                      <Button variant="outline" size="sm" className="h-8 w-8 p-0" onClick={() => handleIncrement(item)}>
                        <Plus className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
              <div className="border-t pt-4">
                <div className="flex justify-between text-lg font-semibold">
                  <span>Total</span>
                  <span>
                    ৳{cartTotal.toFixed(2)}
                  </span>
                </div>
              </div>
            </>
          )}
        </div>
        {cartItems.length > 0 && (
          <DrawerFooter className="border-t">
            <Button
              className="w-full bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
              onClick={handleCheckout}
            >
              Proceed to Checkout
            </Button>
            <DrawerClose asChild>
              <Button variant="outline" className="w-full">
                Continue Shopping
              </Button>
            </DrawerClose>
          </DrawerFooter>
        )}
      </DrawerContent>
    </Drawer>
  );
}
