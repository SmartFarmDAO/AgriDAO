import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { http } from 'wagmi';
import { mainnet, polygon, optimism, arbitrum, base } from 'wagmi/chains';

// Read WalletConnect project id from env. Create it at https://cloud.walletconnect.com/
const projectId = import.meta.env.VITE_WALLETCONNECT_PROJECT_ID as string | undefined;

if (!projectId || projectId === '') {
  console.error('[wagmi] Missing VITE_WALLETCONNECT_PROJECT_ID - Get one from https://cloud.walletconnect.com/');
}

// Use a valid UUID format for development if projectId is missing
const validProjectId = projectId && projectId !== '' 
  ? projectId 
  : '00000000-0000-0000-0000-000000000000';

export const config = getDefaultConfig({
  appName: 'AgriDAO',
  projectId: validProjectId,
  chains: [mainnet, polygon, optimism, arbitrum, base],
  transports: {
    [mainnet.id]: http(),
    [polygon.id]: http(),
    [optimism.id]: http(),
    [arbitrum.id]: http(),
    [base.id]: http(),
  },
  ssr: false,
});
