# AgriDAO Supply Chain Flow

This diagram illustrates the flow of a product from the Farmer to the Buyer, including the role of the Marketplace and the DAO Escrow system.

```mermaid
sequenceDiagram
    participant F as Farmer
    participant M as Marketplace UI
    participant SC as Smart Contract (Escrow)
    participant B as Buyer
    participant L as Logistics/Supply Chain

    Note over F, B: Product Listing & Purchase Phase
    F->>M: Push Product Details (Cost, Qty, Desc)
    M->>M: List Product for Sale
    B->>M: Browse & Select Product
    B->>SC: Initiate Purchase (Send ETH/Tokens)
    SC->>SC: Lock Funds in EscrowOrder(orderId)
    SC-->>M: Emit OrderCreated Event

    Note over F, B: Fulfillment Phase
    M->>F: Notify Order Received
    F->>L: Handover Product for Delivery
    L->>B: Deliver Product
    
    Note over F, B: Settlement Phase
    B->>M: Confirm Receipt
    M->>SC: Call completeOrder(orderId)
    
    rect rgb(200, 255, 200)
    Note right of SC: Verification
    SC->>SC: Verify Caller is Buyer
    SC->>SC: Verify Order Status
    end

    SC->>F: Release Payment (Amount - Fee)
    SC->>SC: Transfer Fee to DAO Treasury
    SC-->>M: Emit OrderCompleted Event
    
    Note over SC: Dispute Handling (if needed)
    opt Dispute
        B->>SC: disputeOrder() (if issues arise)
        SC->>SC: Lock Funds indefinitely until Resolved
    end
```

## Flow Description

1.  **Listing**: Farmer pushes product details to the marketplace.
2.  **Purchase**: Buyer buys the product; funds are sent directly to the `MarketplaceEscrow` smart contract.
3.  **Escrow**: Funds are locked. The contract ensures neither party can access them unilaterally during transit.
4.  **Delivery**: Product moves through the supply chain.
5.  **Completion**: Buyer confirms receipt. The smart contract releases funds to the Farmer (minus platform fee) and sends fees to the DAO.
