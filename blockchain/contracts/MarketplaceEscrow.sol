// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MarketplaceEscrow {
    struct Order {
        uint256 orderId;
        address buyer;
        address seller;
        uint256 amount;
        bool completed;
        bool disputed;
        bool refunded;
    }

    mapping(uint256 => Order) public orders;
    mapping(address => uint256) public balances;
    
    uint256 public platformFee = 25; // 2.5%
    address public platformWallet;

    event OrderCreated(uint256 indexed orderId, address indexed buyer, address indexed seller, uint256 amount);
    event OrderCompleted(uint256 indexed orderId);
    event OrderDisputed(uint256 indexed orderId);
    event OrderRefunded(uint256 indexed orderId);
    event FundsWithdrawn(address indexed account, uint256 amount);

    constructor(address _platformWallet) {
        platformWallet = _platformWallet;
    }

    function createOrder(uint256 orderId, address seller) external payable {
        require(msg.value > 0, "Amount must be greater than 0");
        require(orders[orderId].orderId == 0, "Order already exists");
        
        orders[orderId] = Order({
            orderId: orderId,
            buyer: msg.sender,
            seller: seller,
            amount: msg.value,
            completed: false,
            disputed: false,
            refunded: false
        });
        
        emit OrderCreated(orderId, msg.sender, seller, msg.value);
    }

    function completeOrder(uint256 orderId) external {
        Order storage order = orders[orderId];
        require(order.buyer == msg.sender, "Only buyer can complete");
        require(!order.completed, "Already completed");
        require(!order.disputed, "Order is disputed");
        
        order.completed = true;
        
        uint256 fee = (order.amount * platformFee) / 1000;
        uint256 sellerAmount = order.amount - fee;
        
        balances[order.seller] += sellerAmount;
        balances[platformWallet] += fee;
        
        emit OrderCompleted(orderId);
    }

    function disputeOrder(uint256 orderId) external {
        Order storage order = orders[orderId];
        require(order.buyer == msg.sender || order.seller == msg.sender, "Not authorized");
        require(!order.completed, "Already completed");
        require(!order.disputed, "Already disputed");
        
        order.disputed = true;
        emit OrderDisputed(orderId);
    }

    function refundOrder(uint256 orderId) external {
        Order storage order = orders[orderId];
        require(order.seller == msg.sender, "Only seller can refund");
        require(!order.completed, "Already completed");
        require(!order.refunded, "Already refunded");
        
        order.refunded = true;
        balances[order.buyer] += order.amount;
        
        emit OrderRefunded(orderId);
    }

    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance to withdraw");
        
        balances[msg.sender] = 0;
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        emit FundsWithdrawn(msg.sender, amount);
    }

    function getOrder(uint256 orderId) external view returns (
        address buyer,
        address seller,
        uint256 amount,
        bool completed,
        bool disputed,
        bool refunded
    ) {
        Order memory order = orders[orderId];
        return (order.buyer, order.seller, order.amount, order.completed, order.disputed, order.refunded);
    }
}
