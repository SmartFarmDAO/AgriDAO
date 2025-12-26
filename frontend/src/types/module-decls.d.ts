// Ambient module declarations to satisfy TypeScript when type packages are missing.
// These are minimal and intended to unblock diagnostics; they do not affect runtime.

declare module 'react' {
  export type ReactNode = any;
  export type FC<P = {}> = (props: P & { children?: ReactNode }) => any;
  export function useState<T = any>(initial: T): [T, (v: T) => void];
  export function useEffect(effect: (...args: any[]) => any, deps?: any[]): void;
  export function useRef<T = any>(initial?: T): { current: T };
  const React: any;
  export default React;
}

declare module 'react/jsx-runtime' {
  export const jsx: any;
  export const jsxs: any;
  export const Fragment: any;
}

declare module 'react-router-dom' {
  export const useNavigate: any;
  export const useParams: any;
  export const BrowserRouter: any;
  export const Routes: any;
  export const Route: any;
  export const Navigate: any;
  export const useLocation: any;
  export const Outlet: any;
}

declare module '@tanstack/react-query' {
  export const useQueryClient: any;
  export const QueryClient: any;
  export const QueryClientProvider: any;
  export const useQuery: any;
}

declare module 'lucide-react' {
  export const ArrowLeft: any;
  export const Loader2: any;
  export const Upload: any;
  export const X: any;
  export const Crop: any;
}

