export interface Farmer {
  id: number;
  name: string;
  phone?: string;
  email?: string;
  location?: string;
  created_at: string;
}

export interface Product {
  id: number;
  name: string;
  description?: string;
  category?: string;
  price: number;
  quantity: string;
  farmer_id?: number;
  created_at: string;
}

export interface FundingRequest {
  id: number;
  farmer_name: string;
  purpose: string;
  amount_needed: number;
  amount_raised: number;
  days_left: number;
  category?: string;
  location?: string;
  description?: string;
  status?: string;
  created_at: string;
}

export interface OrderItem {
  product_id: number;
  product_name: string | null;
  quantity: number;
  unit_price: number;
}

export interface Order {
  id: number;
  status: "pending" | "confirmed" | "fulfilled" | "cancelled";
  subtotal: number;
  platform_fee: number;
  total: number;
  payment_status: "unpaid" | "paid" | "refunded";
  created_at: string;
  items: OrderItem[];
}

export interface User {
  id: number;
  role: "buyer" | "farmer" | "admin";
  name: string;
  email?: string;
  phone?: string;
  created_at: string;
}

export interface ProvenanceAsset {
  id: number;
  name: string;
  origin?: string;
  current_location?: string;
  qr_code?: string;
  notes?: string;
  created_at: string;
}

export interface Proposal {
  id: number;
  title: string;
  description?: string;
  status: "open" | "passed" | "rejected";
  created_at: string;
}
