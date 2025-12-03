import { useState, useEffect } from 'react';
import { useTranslation } from '@/i18n/config';

interface Transaction {
  id: string;
  type: string;
  amount: number;
  from_address: string;
  to_address: string;
  timestamp: string;
  hash: string;
  status: 'pending' | 'confirmed' | 'failed';
}

interface BlockchainStats {
  total_transactions: number;
  total_value: number;
  active_users: number;
  last_block_time: string;
}

export default function Blockchain() {
  const { t } = useTranslation();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stats, setStats] = useState<BlockchainStats>({
    total_transactions: 0,
    total_value: 0,
    active_users: 0,
    last_block_time: new Date().toISOString(),
  });
  const [showNewTx, setShowNewTx] = useState(false);
  const [newTx, setNewTx] = useState({ to_address: '', amount: '' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [txRes, statsRes] = await Promise.all([
        fetch('http://localhost:8000/blockchain/transactions'),
        fetch('http://localhost:8000/blockchain/stats'),
      ]);
      const txData = await txRes.json();
      const statsData = await statsRes.json();
      setTransactions(txData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch blockchain data:', error);
    }
  };

  const createTransaction = async () => {
    if (!newTx.to_address || !newTx.amount) return;
    
    try {
      const res = await fetch('http://localhost:8000/blockchain/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'payment',
          amount: parseFloat(newTx.amount),
          from_address: '0x1234...5678',
          to_address: newTx.to_address,
        }),
      });

      if (res.ok) {
        setNewTx({ to_address: '', amount: '' });
        setShowNewTx(false);
        fetchData();
      }
    } catch (error) {
      console.error('Failed to create transaction:', error);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Blockchain Transparency</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Transactions</p>
          <p className="text-2xl font-bold">{stats.total_transactions}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Value</p>
          <p className="text-2xl font-bold">৳{stats.total_value.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Active Users</p>
          <p className="text-2xl font-bold">{stats.active_users}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Last Block</p>
          <p className="text-sm font-semibold">
            {new Date(stats.last_block_time).toLocaleTimeString()}
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Transaction History</h2>
          <button
            onClick={() => setShowNewTx(!showNewTx)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            {showNewTx ? 'Cancel' : 'New Transaction'}
          </button>
        </div>

        {showNewTx && (
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Recipient Address"
                value={newTx.to_address}
                onChange={(e) => setNewTx({ ...newTx, to_address: e.target.value })}
                className="p-2 border rounded"
              />
              <input
                type="number"
                placeholder="Amount"
                value={newTx.amount}
                onChange={(e) => setNewTx({ ...newTx, amount: e.target.value })}
                className="p-2 border rounded"
              />
            </div>
            <button
              onClick={createTransaction}
              className="mt-3 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Send Transaction
            </button>
          </div>
        )}

        <div className="space-y-3">
          {transactions.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No transactions yet</p>
          ) : (
            transactions.map((tx) => (
              <div key={tx.id} className="border rounded-lg p-4 hover:border-green-500">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="font-semibold">{tx.type.toUpperCase()}</p>
                    <p className="text-sm text-gray-600">
                      From: <span className="font-mono">{tx.from_address}</span>
                    </p>
                    <p className="text-sm text-gray-600">
                      To: <span className="font-mono">{tx.to_address}</span>
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold">৳{tx.amount}</p>
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        tx.status === 'confirmed'
                          ? 'bg-green-100 text-green-800'
                          : tx.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {tx.status}
                    </span>
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  <p>Hash: <span className="font-mono">{tx.hash}</span></p>
                  <p>{new Date(tx.timestamp).toLocaleString()}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">🔒 Blockchain Benefits</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>✓ Transparent and immutable transaction records</li>
          <li>✓ Decentralized verification of product authenticity</li>
          <li>✓ Secure payment processing with smart contracts</li>
          <li>✓ Traceable supply chain from farm to consumer</li>
        </ul>
      </div>
    </div>
  );
}
