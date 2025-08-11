const BASE_URL = (import.meta as any).env?.VITE_API_URL || "http://127.0.0.1:8000";
import { secureStorage } from "@/lib/security";

function authHeaders(): HeadersInit {
  const token = secureStorage.get<string>("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { ...authHeaders() },
  });
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(body ?? {}),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`POST ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

async function apiPut<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(body ?? {}),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`PUT ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

async function apiDelete<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "DELETE",
    headers: { ...authHeaders() },
  });
  if (!res.ok) {
    throw new Error(`DELETE ${path} failed: ${res.status}`);
  }
  if (res.status === 204) {
    return {} as T;
  }
  return res.json();
}


// Marketplace
export const listProducts = () => apiGet<import("@/types").Product[]>("/marketplace/products");

// Finance
export const listFundingRequests = () => apiGet<import("@/types").FundingRequest[]>("/finance/requests");
export const donateToRequest = (id: number, amount: number) =>
  apiPost<import("@/types").FundingRequest>(`/finance/requests/${id}/donate`, { amount });

// Auth (OTP)
export const requestOtp = (email: string) => apiPost<{ sent: boolean; dev_code?: string }>(
  "/auth/otp/request",
  { email }
);

export const verifyOtp = async (email: string, code: string) => {
  const result = await apiPost<{ access_token: string; token_type: string; user: { id: number; email: string; role: string } }>(
    "/auth/otp/verify",
    { email, code }
  );
  secureStorage.set("access_token", result.access_token);
  secureStorage.set("current_user", result.user);
  return result;
};

// Farmers
export const getMyFarmerProfile = () => apiGet<import("@/types").Farmer>("/farmers/me");
export const createMyFarmerProfile = (payload: Partial<import("@/types").Farmer>) =>
  apiPost<import("@/types").Farmer>("/farmers/", payload);

// Commerce
export const createCheckoutSession = (payload: {
  items: { product_id: number; quantity: number }[];
  success_url: string;
  cancel_url: string;
}) => apiPost<{ checkout_url: string; order_id: number }>("/commerce/checkout_session", payload);

export const listMyOrders = () => apiGet<import("@/types").Order[]>("/commerce/orders");

export const getOrder = (orderId: number) =>
  apiGet<import("@/types").Order>(`/commerce/orders/${orderId}`);

// User Management API
export const listUsers = () => apiGet<import("@/types").User[]>("/users/");

export const getUser = (userId: string) => apiGet<import("@/types").User>(`/users/${userId}`);

export const createUser = (userData: Partial<import("@/types").User>) => apiPost<import("@/types").User>("/users/", userData);

export const updateUser = (userId: number, userData: Partial<import("@/types").User>) =>
  apiPut<import("@/types").User>(`/users/${userId}`, userData);

export const deleteUser = (userId: number) => apiDelete<void>(`/users/${userId}`);

// Supply Chain API
export const listAssets = () => apiGet<import("@/types").ProvenanceAsset[]>("/supplychain/assets");

export const getAsset = (assetId: number) => apiGet<import("@/types").ProvenanceAsset>(`/supplychain/assets/${assetId}`);

export const createAsset = (assetData: Partial<import("@/types").ProvenanceAsset>) => apiPost<import("@/types").ProvenanceAsset>("/supplychain/assets", assetData);

export const updateAsset = (assetId: number, assetData: Partial<import("@/types").ProvenanceAsset>) => apiPut<import("@/types").ProvenanceAsset>(`/supplychain/assets/${assetId}`, assetData);

export const deleteAsset = (assetId: number) => apiDelete<void>(`/supplychain/assets/${assetId}`);

// Governance API
export const listProposals = () => apiGet<import("@/types").Proposal[]>("/governance/proposals");

export const createProposal = (proposalData: Partial<import("@/types").Proposal>) => apiPost<import("@/types").Proposal>("/governance/proposals", proposalData);

export const closeProposal = (proposalId: number, outcome: "passed" | "rejected") => apiPost<import("@/types").Proposal>(`/governance/proposals/${proposalId}/close`, { outcome });

// AI API
export const getAdvice = (crop: string, location: string) => apiPost<{ advice: string[] }>("/ai/advice", { crop, location });
