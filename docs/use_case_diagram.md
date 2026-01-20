# AgriDAO System Use Cases

This diagram maps the primary actors to their interactions with the AgriDAO system components (Marketplace/Escrow and Governance).

```mermaid
graph TD
    %% Actors
    Farmer((Farmer/Seller))
    Buyer((Buyer))
    Logistics((Logistics Provider))
    DAOMember((DAO Member))

    %% System Components
    subgraph System ["AgriDAO Platform"]
        subgraph Marketplace ["Marketplace & Escrow"]
            List[List Product (Off-chain/UI)]
            CreateOrder[Create Order (Escrow Deposit)]
            Complete[Complete Order (Release Funds)]
            Dispute[Dispute Order]
            Refund[Refund Buyer]
            Withdraw[Withdraw Funds]
        end

        subgraph Governance ["DAO Governance (AgriDAO.sol)"]
            Join[Join DAO]
            Propose[Create Proposal]
            Vote[Vote on Proposal]
            Execute[Execute Proposal]
        end
    end

    %% Relationships
    Farmer --> List
    Farmer --> Refund
    Farmer --> Withdraw
    Farmer --> Dispute
    Farmer --> Join

    Buyer --> Browse[Browse Marketplace]
    Buyer --> CreateOrder
    Buyer --> Complete
    Buyer --> Dispute
    Buyer --> Withdraw

    Logistics --> Update[Update Tracking Status]

    DAOMember --> Join
    DAOMember --> Propose
    DAOMember --> Vote
    DAOMember --> Execute

    %% Contract Links
    CreateOrder -.-> |"MarketplaceEscrow.sol"| CreateOrder
    Complete -.-> |"MarketplaceEscrow.sol"| Complete
    Propose -.-> |"AgriDAO.sol"| Propose
```

## Use Case Descriptions

### Farmer / Seller
- **List Product**: Publish product availablity to the UI.
- **Refund Buyer**: Can voluntarily refund the buyer if unable to fulfill.
- **Dispute**: Can flag an order if there are issues.
- **Withdraw**: Withdraw earnings from the smart contract.
- **DAO Participation**: Can join the DAO to vote on platform fees/rules.

### Buyer
- **Create Order**: Initiates the transaction by depositing funds into Escrow.
- **Complete Order**: Confirms receipt of goods, releasing funds to Farmer.
- **Dispute**: Can pause payout if goods aren't received/damaged.

### DAO Member
- **Governance**: Participates in decision making (e.g., setting platform fees) via `AgriDAO.sol`.
