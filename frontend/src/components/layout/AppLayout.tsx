import { Outlet } from "react-router-dom";
import AppHeader from "../AppHeader";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader />
      <main className="container mx-auto px-4 py-6">
        <Outlet />
      </main>
      <Toaster />
      <Sonner />
    </div>
  );
}
