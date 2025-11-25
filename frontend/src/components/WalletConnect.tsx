import { useWeb3 } from '@/contexts/Web3Context';
import { Button } from '@/components/ui/button';
import { Wallet } from 'lucide-react';

export function WalletConnect() {
  const { account, chainId, connect, disconnect } = useWeb3();

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const getNetworkName = (id: number) => {
    const networks: Record<number, string> = {
      1: 'Ethereum',
      11155111: 'Sepolia',
      1337: 'Localhost'
    };
    return networks[id] || `Chain ${id}`;
  };

  if (account) {
    return (
      <div className="flex items-center gap-2">
        <div className="text-sm">
          <div className="font-medium">{formatAddress(account)}</div>
          {chainId && <div className="text-xs text-muted-foreground">{getNetworkName(chainId)}</div>}
        </div>
        <Button variant="outline" size="sm" onClick={disconnect}>
          Disconnect
        </Button>
      </div>
    );
  }

  return (
    <Button onClick={connect} className="gap-2">
      <Wallet className="h-4 w-4" />
      Connect Wallet
    </Button>
  );
}
