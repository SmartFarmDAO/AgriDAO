import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { http } from 'wagmi';
import { mainnet, polygon, optimism, arbitrum, base } from 'wagmi/chains';

// Read WalletConnect project id from env. Create it at https://cloud.walletconnect.com/
const projectId = import.meta.env.VITE_WALLETCONNECT_PROJECT_ID as string | undefined;

if (!projectId) {
  // Non-fatal in dev; RainbowKit may still warn when attempting to connect.
  // Set VITE_WALLETCONNECT_PROJECT_ID in .env to remove this warning.
  console.warn('[wagmi] Missing VITE_WALLETCONNECT_PROJECT_ID');
}

export const config = getDefaultConfig({
  appName: 'AgriDAO',
  projectId: projectId ?? 'missing-project-id',
  chains: [mainnet, polygon, optimism, arbitrum, base],
  transports: {
    [mainnet.id]: http(),
    [polygon.id]: http(),
    [optimism.id]: http(),
    [arbitrum.id]: http(),
    [base.id]: http(),
  },
  ssr: true,
});
