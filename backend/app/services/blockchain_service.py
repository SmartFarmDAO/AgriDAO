import os
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Minimal ABIs for our contracts
AGRIDAO_ABI = [
    {
        "inputs": [],
        "name": "memberCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "proposalId", "type": "uint256"}],
        "name": "getProposal",
        "outputs": [
            {"internalType": "address", "name": "proposer", "type": "address"},
            {"internalType": "string", "name": "description", "type": "string"},
            {"internalType": "uint256", "name": "forVotes", "type": "uint256"},
            {"internalType": "uint256", "name": "againstVotes", "type": "uint256"},
            {"internalType": "uint256", "name": "endTime", "type": "uint256"},
            {"internalType": "bool", "name": "executed", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "proposalCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "getMember",
        "outputs": [
            {"internalType": "bool", "name": "isMember", "type": "bool"},
            {"internalType": "uint256", "name": "votingPower", "type": "uint256"},
            {"internalType": "uint256", "name": "joinedAt", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    }
]

ESCROW_ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "orderId", "type": "uint256"}],
        "name": "getOrder",
        "outputs": [
            {"internalType": "address", "name": "buyer", "type": "address"},
            {"internalType": "address", "name": "seller", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "bool", "name": "completed", "type": "bool"},
            {"internalType": "bool", "name": "disputed", "type": "bool"},
            {"internalType": "bool", "name": "refunded", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    }
]

class BlockchainService:
    def __init__(self):
        self.rpc_url = os.getenv("SEPOLIA_RPC_URL")
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Inject POA middleware for testnets
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        self.agridao_address = os.getenv("AGRIDAO_ADDRESS")
        self.escrow_address = os.getenv("ESCROW_ADDRESS")
        
        self.agridao = None
        self.escrow = None
        
        if self.agridao_address:
            self.agridao = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.agridao_address),
                abi=AGRIDAO_ABI
            )
            
        if self.escrow_address:
            self.escrow = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.escrow_address),
                abi=ESCROW_ABI
            )

    def is_connected(self) -> bool:
        return self.w3.is_connected()

    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Get summary stats from the blockchain."""
        stats = {
            "total_transactions": 0,
            "total_value": 0.0,
            "active_users": 0,
            "last_block_time": None
        }
        
        try:
            if self.agridao:
                stats["active_users"] = self.agridao.functions.memberCount().call()
                total_proposals = self.agridao.functions.proposalCount().call()
                stats["total_transactions"] = total_proposals
            
            latest_block = self.w3.eth.get_block('latest')
            stats["last_block_time"] = latest_block['timestamp']
            
        except Exception as e:
            logger.error(f"Error fetching blockchain stats: {e}")
            
        return stats

    def get_order_details(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Get order details from escrow contract."""
        if not self.escrow:
            return None
            
        try:
            order = self.escrow.functions.getOrder(order_id).call()
            return {
                "buyer": order[0],
                "seller": order[1],
                "amount": self.w3.from_wei(order[2], 'ether'),
                "completed": order[3],
                "disputed": order[4],
                "refunded": order[5]
            }
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            return None

    def get_proposal_details(self, proposal_id: int) -> Optional[Dict[str, Any]]:
        """Get proposal details from DAO contract."""
        if not self.agridao:
            return None
            
        try:
            prop = self.agridao.functions.getProposal(proposal_id).call()
            return {
                "proposer": prop[0],
                "description": prop[1],
                "forVotes": prop[2],
                "againstVotes": prop[3],
                "endTime": prop[4],
                "executed": prop[5]
            }
        except Exception as e:
            logger.error(f"Error fetching proposal {proposal_id}: {e}")
            return None

    def register_product(self, product_data: Dict[str, Any]) -> Optional[str]:
        """Register product hash on-chain via DAO proposal (as a provenance record)."""
        if not self.agridao or not os.getenv("PRIVATE_KEY"):
            return None
            
        try:
            # Generate stable hash of product data
            product_json = json.dumps(product_data, sort_keys=True)
            product_hash = self.w3.keccak(text=product_json).hex()
            
            # Prepare transaction
            account = self.w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
            
            # Use createProposal as a way to put data on-chain
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            # Simple description containing the hash and name
            description = f"PRODUCT_REGISTRY:{product_data.get('name', 'Unknown')}:{product_hash}"
            
            txn = self.agridao.functions.createProposal(description).build_transaction({
                'chainId': 11155111,  # Sepolia
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=os.getenv("PRIVATE_KEY"))
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return self.w3.to_hex(tx_hash)
            
        except Exception as e:
            logger.error(f"Error registering product on-chain: {e}")
            return None

blockchain_service = BlockchainService()
