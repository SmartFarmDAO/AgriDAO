import React from "react";
import { WagmiProvider, http } from "wagmi";
import { baseSepolia, polygonAmoy } from "wagmi/chains";
import {
  RainbowKitProvider,
  getDefaultConfig,
} from "@rainbow-me/rainbowkit";
import "@rainbow-me/rainbowkit/styles.css";

const projectId = (import.meta as any).env?.VITE_WALLETCONNECT_PROJECT_ID as string | undefined;

const transports: Record<number, ReturnType<typeof http>> = {
  [baseSepolia.id]: http((import.meta as any).env?.VITE_RPC_BASE_SEPOLIA),
  [polygonAmoy.id]: http((import.meta as any).env?.VITE_RPC_POLYGON_AMOY),
};

const config = getDefaultConfig({
  appName: "AgriDAO",
  projectId: projectId || "demo",
  chains: [baseSepolia, polygonAmoy],
  transports,
  ssr: false,
});

export const WalletProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <WagmiProvider config={config}>
      <RainbowKitProvider>
        {children}
      </RainbowKitProvider>
    </WagmiProvider>
  );
};
