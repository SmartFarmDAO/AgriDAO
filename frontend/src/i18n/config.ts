import { createContext, useContext } from 'react';

export type Language = 'en' | 'bn';

export interface Translations {
  [key: string]: string | Translations;
}

export const translations: Record<Language, Translations> = {
  en: {
    common: {
      welcome: 'Welcome to AgriDAO',
      marketplace: 'Marketplace',
      dashboard: 'Dashboard',
      profile: 'Profile',
      logout: 'Logout',
      login: 'Login',
      signup: 'Sign Up',
      search: 'Search',
      filter: 'Filter',
      addToCart: 'Add to Cart',
      checkout: 'Checkout',
      viewDetails: 'View Details',
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      finance: 'Finance',
      supplyChain: 'Supply Chain',
      governance: 'Governance',
      aiAssistant: 'AI Assistant',
      signIn: 'Sign In',
    },
    home: {
      hero: 'Empowering Farmers Through Blockchain',
      subtitle: 'Direct marketplace connecting farmers with buyers',
      getStarted: 'Get Started',
      learnMore: 'Learn More',
    },
    products: {
      title: 'Products',
      price: 'Price',
      quantity: 'Quantity',
      category: 'Category',
      outOfStock: 'Out of Stock',
      inStock: 'In Stock',
    },
    cart: {
      title: 'Shopping Cart',
      empty: 'Your cart is empty',
      total: 'Total',
      subtotal: 'Subtotal',
      platformFee: 'Platform Fee',
    },
  },
  bn: {
    common: {
      welcome: 'AgriDAO তে স্বাগতম',
      marketplace: 'বাজার',
      dashboard: 'ড্যাশবোর্ড',
      profile: 'প্রোফাইল',
      logout: 'লগআউট',
      login: 'লগইন',
      signup: 'সাইন আপ',
      search: 'খুঁজুন',
      filter: 'ফিল্টার',
      addToCart: 'কার্টে যোগ করুন',
      checkout: 'চেকআউট',
      viewDetails: 'বিস্তারিত দেখুন',
      loading: 'লোড হচ্ছে...',
      error: 'ত্রুটি',
      success: 'সফল',
      finance: 'অর্থায়ন',
      supplyChain: 'সরবরাহ চেইন',
      governance: 'সুশাসন',
      aiAssistant: 'এআই সহকারী',
      signIn: 'সাইন ইন',
    },
    home: {
      hero: 'ব্লকচেইনের মাধ্যমে কৃষকদের ক্ষমতায়ন',
      subtitle: 'কৃষক এবং ক্রেতাদের সংযোগকারী সরাসরি বাজার',
      getStarted: 'শুরু করুন',
      learnMore: 'আরও জানুন',
    },
    products: {
      title: 'পণ্য',
      price: 'মূল্য',
      quantity: 'পরিমাণ',
      category: 'বিভাগ',
      outOfStock: 'স্টক শেষ',
      inStock: 'স্টকে আছে',
    },
    cart: {
      title: 'শপিং কার্ট',
      empty: 'আপনার কার্ট খালি',
      total: 'মোট',
      subtotal: 'উপমোট',
      platformFee: 'প্ল্যাটফর্ম ফি',
    },
  },
};

export const LanguageContext = createContext<{
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}>({
  language: 'en',
  setLanguage: () => {},
  t: (key: string) => key,
});

export const useTranslation = () => useContext(LanguageContext);
