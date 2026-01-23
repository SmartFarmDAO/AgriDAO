---
description: Plan for implementing Cart functionality and Blockchain transactions on Testnet
---

# Cart and Blockchain Integration Plan

This workflow outlines the steps to verify the Cart functionality and integrate Blockchain transactions using the deployed Sepolia contracts.

## Phase 1: Cart Functionality Verification

1.  **Verify Frontend Cart Logic**:
    -   Ensure `CartContext.tsx` handles `addToCart`, `removeFromCart`, `updateQuantity` correctly.
    -   Verify products are persisted in `localStorage`.
    -   Verify "Checkout" button triggers the flow.

2.  **Verify Cart UI**:
    -   Check `Marketplace.tsx` and Cart drawer/page.
    -   Ensure prices and totals act correctly (already checked previously, but verify with new context).

## Phase 2: Blockchain Integration (Sepolia Testnet)

1.  **Frontend Configuration**:
    -   We have set `frontend/.env` with Sepolia addresses:
        -   `VITE_AGRIDAO_ADDRESS=0x00A188...`
        -   `VITE_ESCROW_ADDRESS=0x1E3c00...`
    -   Verify `Web3Context.tsx` reads these values.
    -   Verify `WalletConnect.tsx` allows connecting Metamask (Testnet).

2.  **Checkout & Escrow Integration**:
    -   **Task**: Connect the "Checkout" button in Cart to `MarketplaceEscrow.createOrder`.
    -   **Flow**:
        1.  User clicks "Checkout".
        2.  App checks if Wallet is connected. If not, prompt connection.
        3.  App calls `createOrder(orderId, sellerAddress)` on the Smart Contract.
            -   *Note*: `createOrder` requires `msg.value` equal to the price + fee.
            -   We need to calculate the correct ETH amount (convert BDT to ETH? Or assume price is ETH?).
            -   *Critical Decision*: The current marketplace uses BDT. Smart contract usually expects ETH. We might need a conversion rate or a mock rate (e.g. 1 BDT = 0.00001 ETH) for the testnet demo.
        4.  User confirms transaction in Metamask.
        5.  On success (`tx.wait()`), clear cart and create Order in Backend (via API).

3.  **Backend Order Creation**:
    -   Ensure Backend API `/api/orders` exists to record the order details (product, quantity, buyer) AFTER the blockchain transaction is confirmed (or in parallel with status "Pending Payment").

## Phase 3: Testing

1.  **Get Sepolia ETH**:
    -   Ensure the testing wallet has Sepolia ETH.
2.  **Run Full Flow**:
    -   Add item -> Cart -> Checkout -> Metamask -> Confirm -> Success.

## Next Step
-   Start by verifying `Web3Context` and the "Checkout" button connection.
