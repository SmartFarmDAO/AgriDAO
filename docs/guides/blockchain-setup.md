# Blockchain Setup Guide

Complete guide to set up and use AgriDAO blockchain features.

## Prerequisites

- MetaMask browser extension
- Node.js 18+
- ETH for gas fees (testnet or mainnet)

## Step 1: Install MetaMask

1. Visit https://metamask.io
2. Install browser extension
3. Create or import wallet
4. Save your seed phrase securely

## Step 2: Get Testnet ETH

For Sepolia testnet:
1. Visit https://sepoliafaucet.com
2. Enter your wallet address
3. Request test ETH

## Step 3: Deploy Contracts

```bash
# Navigate to blockchain directory
cd blockchain

# Install dependencies
npm install

# Start local node (for development)
npm run node

# Deploy contracts (in new terminal)
npm run deploy:local

# Or deploy to Sepolia
npm run deploy:sepolia
```

## Step 4: Configure Frontend

1. Copy contract addresses from `blockchain/deployed-addresses.json`
2. Update `frontend/.env`:
```bash
VITE_AGRIDAO_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
VITE_ESCROW_ADDRESS=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
```

## Step 5: Connect Wallet

1. Start frontend: `npm run dev`
2. Click "Connect Wallet" button
3. Approve MetaMask connection
4. Select account to connect

## Using DAO Governance

### Join DAO
1. Navigate to DAO Governance page
2. Click "Join DAO"
3. Confirm transaction in MetaMask
4. Wait for confirmation

### Create Proposal
1. Enter proposal description
2. Click "Create Proposal"
3. Confirm transaction
4. Proposal appears in list

### Vote on Proposals
1. View active proposals
2. Click "Vote For" or "Vote Against"
3. Confirm transaction
4. Vote is recorded on-chain

## Using Escrow

### Create Order
```javascript
// Buyer creates order with payment
await escrow.createOrder(orderId, sellerAddress, { value: amount });
```

### Complete Order
```javascript
// Buyer confirms delivery
await escrow.completeOrder(orderId);
```

### Dispute Order
```javascript
// Either party can dispute
await escrow.disputeOrder(orderId);
```

### Withdraw Funds
```javascript
// Seller withdraws earned funds
await escrow.withdraw();
```

## Network Switching

### Add Sepolia to MetaMask
1. Open MetaMask
2. Click network dropdown
3. Click "Add Network"
4. Enter Sepolia details:
   - Network Name: Sepolia
   - RPC URL: https://sepolia.infura.io/v3/YOUR_KEY
   - Chain ID: 11155111
   - Currency: ETH

### Switch Networks
1. Click network dropdown in MetaMask
2. Select desired network
3. Frontend will reload automatically

## Troubleshooting

### Transaction Failed
- Check you have enough ETH for gas
- Verify contract addresses are correct
- Ensure you're on the right network

### Wallet Not Connecting
- Refresh page
- Check MetaMask is unlocked
- Try disconnecting and reconnecting

### Contract Not Found
- Verify contract addresses in `.env`
- Ensure contracts are deployed
- Check you're on correct network

## Gas Optimization Tips

- Batch multiple operations when possible
- Use appropriate gas limits
- Monitor gas prices on testnet
- Test thoroughly before mainnet

## Security Best Practices

- Never share private keys
- Use hardware wallet for mainnet
- Verify contract addresses
- Test on testnet first
- Keep MetaMask updated
- Review transactions before signing

## Next Steps

- Explore DAO governance features
- Test escrow functionality
- Read smart contract code
- Join community discussions
