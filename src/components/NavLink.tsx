import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";

type NavLinkProps = {
  to: string;
  children: React.ReactNode;
  className?: string;
};

export function NavLink({ to, children, className }: NavLinkProps) {
  const { pathname } = useLocation();
  const isActive = pathname === to;
  
  return (
    <Link
      to={to}
      className={cn(
        "px-3 py-2 text-sm font-medium rounded-md transition-colors",
        isActive 
          ? "bg-green-50 text-green-700" 
          : "text-gray-700 hover:bg-gray-100 hover:text-gray-900",
        className
      )}
    >
      {children}
    </Link>
  );
}
