import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { BrowserProvider, Contract, formatEther, parseEther } from 'ethers';

interface Web3ContextType {
  account: string | null;
  chainId: number | null;
  provider: BrowserProvider | null;
  connect: () => Promise<void>;
  disconnect: () => void;
  agriDAO: Contract | null;
  escrow: Contract | null;
}

const Web3Context = createContext<Web3ContextType | undefined>(undefined);

const AGRIDAO_ABI = [
  "function joinDAO() external",
  "function createProposal(string memory description) external returns (uint256)",
  "function vote(uint256 proposalId, bool support) external",
  "function getProposal(uint256 proposalId) external view returns (address, string, uint256, uint256, uint256, bool)",
  "function getMember(address account) external view returns (bool, uint256, uint256)",
  "function proposalCount() external view returns (uint256)",
  "function memberCount() external view returns (uint256)",
  "function executeProposal(uint256 proposalId) external",
  "event MemberAdded(address indexed member, uint256 votingPower)",
  "event ProposalCreated(uint256 indexed proposalId, address indexed proposer, string description)",
  "event VoteCast(uint256 indexed proposalId, address indexed voter, bool support, uint256 weight)",
  "event ProposalExecuted(uint256 indexed proposalId)"
];

const ESCROW_ABI = [
  "function createOrder(uint256 orderId, address seller) external payable",
  "function completeOrder(uint256 orderId) external",
  "function disputeOrder(uint256 orderId) external",
  "function refundOrder(uint256 orderId) external",
  "function withdraw() external",
  "function getOrder(uint256 orderId) external view returns (address, address, uint256, bool, bool, bool)",
  "function balances(address) external view returns (uint256)",
  "event OrderCreated(uint256 indexed orderId, address indexed buyer, address indexed seller, uint256 amount)",
  "event OrderCompleted(uint256 indexed orderId)"
];

export function Web3Provider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);
  const [provider, setProvider] = useState<BrowserProvider | null>(null);
  const [agriDAO, setAgriDAO] = useState<Contract | null>(null);
  const [escrow, setEscrow] = useState<Contract | null>(null);

  const connect = async () => {
    if (!window.ethereum) {
      alert('Please install MetaMask!');
      return;
    }

    try {
      const browserProvider = new BrowserProvider(window.ethereum);
      const targetChainId = BigInt(11155111); // Sepolia
      let network = await browserProvider.getNetwork();

      if (network.chainId !== targetChainId) {
        try {
          await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: '0xaa36a7' }], // 11155111 in hex
          });
        } catch (switchError: any) {
          // This error code indicates that the chain has not been added to MetaMask.
          if (switchError.code === 4902) {
            try {
              await window.ethereum.request({
                method: 'wallet_addEthereumChain',
                params: [
                  {
                    chainId: '0xaa36a7',
                    chainName: 'Sepolia Test Network',
                    nativeCurrency: {
                      name: 'SepoliaETH',
                      symbol: 'ETH',
                      decimals: 18,
                    },
                    rpcUrls: ['https://sepolia.infura.io/v3/'],
                    blockExplorerUrls: ['https://sepolia.etherscan.io'],
                  },
                ],
              });
            } catch (addError) {
              console.error('Failed to add Sepolia network:', addError);
            }
          } else {
            console.error('Failed to switch network:', switchError);
          }
        }
        // Refresh provider and network after switch
        const newProvider = new BrowserProvider(window.ethereum);
        network = await newProvider.getNetwork();
        setProvider(newProvider);
      } else {
        setProvider(browserProvider);
      }

      const accounts = await browserProvider.send('eth_requestAccounts', []);
      const signer = await browserProvider.getSigner();

      setAccount(accounts[0]);
      setChainId(Number(network.chainId));

      // Load contract addresses from environment
      const agriDAOAddress = import.meta.env.VITE_AGRIDAO_ADDRESS;
      const escrowAddress = import.meta.env.VITE_ESCROW_ADDRESS;

      if (agriDAOAddress) {
        const daoContract = new Contract(agriDAOAddress, AGRIDAO_ABI, signer);
        setAgriDAO(daoContract);
      }

      if (escrowAddress) {
        const escrowContract = new Contract(escrowAddress, ESCROW_ABI, signer);
        setEscrow(escrowContract);
      }
    } catch (error) {
      console.error('Failed to connect:', error);
    }
  };

  const disconnect = () => {
    setAccount(null);
    setChainId(null);
    setProvider(null);
    setAgriDAO(null);
    setEscrow(null);
  };

  useEffect(() => {
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts: string[]) => {
        if (accounts.length === 0) {
          disconnect();
        } else {
          setAccount(accounts[0]);
        }
      });

      window.ethereum.on('chainChanged', () => {
        window.location.reload();
      });
    }

    return () => {
      if (window.ethereum) {
        window.ethereum.removeAllListeners('accountsChanged');
        window.ethereum.removeAllListeners('chainChanged');
      }
    };
  }, []);

  return (
    <Web3Context.Provider value={{ account, chainId, provider, connect, disconnect, agriDAO, escrow }}>
      {children}
    </Web3Context.Provider>
  );
}

export function useWeb3() {
  const context = useContext(Web3Context);
  if (!context) {
    throw new Error('useWeb3 must be used within Web3Provider');
  }
  return context;
}
