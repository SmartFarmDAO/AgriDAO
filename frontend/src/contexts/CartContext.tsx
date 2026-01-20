
import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { Product } from '@/types';
import { useToast } from "@/components/ui/use-toast";
import { useTranslation } from "@/i18n/config";

export interface CartItem {
    product: Product;
    quantity: number;
}

interface CartContextType {
    cart: CartItem[];
    addToCart: (product: Product) => void;
    removeFromCart: (productId: number) => void;
    updateQuantity: (productId: number, quantity: number) => void;
    clearCart: () => void;
    cartTotal: number;
    formatPrice: (price: string | number) => string;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [cart, setCart] = useState<CartItem[]>([]);
    const { toast } = useToast();
    const { t } = useTranslation();

    // Load cart from localStorage
    useEffect(() => {
        try {
            const savedCart = localStorage.getItem('cart_items');
            if (savedCart) {
                // We might need to fetch full product details if we only stored minimal info earlier,
                // but for now let's assume the stored structure matches or we can adapt.
                // The previous implementation stored a minimal object. 
                // To be safe and compatible with the previous implementation which relied on 
                // fetching products to hydrate the cart, we might want to stick to a simple 
                // structure in local storage, but for this refactor I will store the full product
                // to avoid dependency on the products query for basic cart display, 
                // or we accept that we might need to migrate the storage format.
                // Let's try to parse what's there.
                const parsed = JSON.parse(savedCart);

                // Check if parsed items obey the structure. 
                // Old structure was: { product_id, quantity, name, price }
                // We need 'product' object.
                // If the stored data is the "minimal" version, we might have issues if we expect full Product object.
                // However, for the purpose of the fix, let's implement a robust restoration or just start fresh if schema mismatches.

                // Simplest migration: If it looks like the old minimal format (no 'product' key), 
                // we might verify if we can reconstruct. 
                // But to keep it simple and given this is a dev env fix:
                // Let's assume we will store the { product: Product, quantity: number } structure going forward.
                // If we read the old structure, it won't match.

                if (Array.isArray(parsed)) {
                    // Attempt to normalize
                    const validItems: CartItem[] = parsed.map((item: any) => {
                        if (item.product) return item as CartItem;
                        // If old format, try to adapt if possible, or filter out
                        // Old: { product_id, quantity, name, price }
                        // We can construct a partial Product object to keep it working
                        if (item.product_id) {
                            return {
                                product: {
                                    id: item.product_id,
                                    name: item.name,
                                    price: item.price,
                                    // defaults
                                    created_at: new Date().toISOString()
                                } as Product,
                                quantity: item.quantity
                            };
                        }
                        return null;
                    }).filter(Boolean) as CartItem[];
                    setCart(validItems);
                }
            }
        } catch (e) {
            console.error("Failed to load cart", e);
        }
    }, []);

    // Save to localStorage
    useEffect(() => {
        try {
            localStorage.setItem('cart_items', JSON.stringify(cart));
            // Dispatch event for other listeners if any (though context should replace them)
            window.dispatchEvent(new CustomEvent("cart_updated"));
        } catch (e) {
            console.error("Failed to save cart", e);
        }
    }, [cart]);

    const formatPrice = (price: string | number): string => {
        if (price === undefined || price === null) return "0.00";
        const num = typeof price === 'number' ? price : parseFloat(price);
        return isNaN(num) ? "0.00" : num.toFixed(2);
    };

    const addToCart = (product: Product) => {
        setCart((prev) => {
            const existing = prev.find((item) => item.product.id === product.id);
            const currentQty = existing ? existing.quantity : 0;

            // Stock validation
            if (product.quantity_available !== undefined && currentQty + 1 > product.quantity_available) {
                toast({
                    title: "Stock Limit Reached",
                    description: `Only ${product.quantity_available} units available`,
                    variant: "destructive"
                });
                return prev;
            }

            if (existing) {
                toast({
                    title: t('marketplace.addedToCart') || "Added to cart",
                    description: `${product.name} ${t('marketplace.productAddedToCart') || "added to your cart."}`
                });
                return prev.map((item) =>
                    item.product.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
                );
            }

            toast({
                title: t('marketplace.addedToCart') || "Added to cart",
                description: `${product.name} ${t('marketplace.productAddedToCart') || "added to your cart."}`
            });
            return [...prev, { product, quantity: 1 }];
        });
    };

    const removeFromCart = (productId: number) => {
        setCart((prev) => prev.filter((item) => item.product.id !== productId));
    };

    const updateQuantity = (productId: number, quantity: number) => {
        if (quantity < 1) {
            removeFromCart(productId);
            return;
        }
        setCart((prev) =>
            prev.map((item) => (item.product.id === productId ? { ...item, quantity } : item))
        );
    };

    const clearCart = () => {
        setCart([]);
    };

    const cartTotal = useMemo(() => {
        return cart.reduce((total, item) => {
            const price = typeof item.product.price === 'number' ? item.product.price : parseFloat(item.product.price as string);
            const safePrice = isNaN(price) ? 0 : price;
            return total + (safePrice * item.quantity);
        }, 0);
    }, [cart]);

    return (
        <CartContext.Provider value={{ cart, addToCart, removeFromCart, updateQuantity, clearCart, cartTotal, formatPrice }}>
            {children}
        </CartContext.Provider>
    );
};

export const useCart = () => {
    const context = useContext(CartContext);
    if (context === undefined) {
        throw new Error('useCart must be used within a CartProvider');
    }
    return context;
};
