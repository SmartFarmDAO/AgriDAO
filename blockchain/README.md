# AgriDAO Blockchain

Smart contracts for AgriDAO governance and marketplace escrow.

## Contracts

### AgriDAO.sol
Governance contract for decentralized decision-making:
- Member management
- Proposal creation and voting
- 3-day voting period
- Simple majority execution

### MarketplaceEscrow.sol
Escrow contract for secure transactions:
- Order creation with ETH payment
- Buyer confirmation releases funds
- Dispute mechanism
- Refund capability
- 2.5% platform fee

## Quick Start

### 1. Install Dependencies
```bash
cd blockchain
npm install
```

### 2. Compile Contracts
```bash
npm run compile
```

### 3. Start Local Node
```bash
npm run node
```

### 4. Deploy (in new terminal)
```bash
# Local deployment
npm run deploy:local

# Sepolia testnet
npm run deploy:sepolia
```

### 5. Update Frontend Config
Copy contract addresses from `deployed-addresses.json` to `frontend/.env`:
```bash
VITE_AGRIDAO_ADDRESS=0x...
VITE_ESCROW_ADDRESS=0x...
```

## Testing

```bash
npm test
```

## Network Configuration

### Local Development
- Network: Hardhat
- Chain ID: 1337
- RPC: http://127.0.0.1:8545

### Sepolia Testnet
- Chain ID: 11155111
- RPC: Configure in `.env`
- Faucet: https://sepoliafaucet.com

## Environment Variables

Create `.env` file:
```bash
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY
PRIVATE_KEY=your_private_key_here
```

## Contract Addresses

After deployment, addresses are saved to `deployed-addresses.json`.

## Security Notes

- Never commit private keys
- Use testnet for development
- Audit contracts before mainnet deployment
- Test thoroughly with various scenarios
