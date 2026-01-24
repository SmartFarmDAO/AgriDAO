import { useState, useEffect } from 'react';
import { useWeb3 } from '@/contexts/Web3Context';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'react-hot-toast';

interface Proposal {
  id: number;
  proposer: string;
  description: string;
  forVotes: bigint;
  againstVotes: bigint;
  endTime: bigint;
  executed: boolean;
}

export default function DAOGovernance() {
  console.log("DAOGovernance Component Loaded");
  const { account, agriDAO } = useWeb3();
  const [isMember, setIsMember] = useState(false);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [newProposal, setNewProposal] = useState('');
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (account && agriDAO) {
      checkMembership();
      loadProposals();
    }
  }, [account, agriDAO]);

  const checkMembership = async () => {
    if (!agriDAO || !account) return;
    try {
      const [member] = await agriDAO.getMember(account);
      setIsMember(member);
    } catch (error) {
      console.error('Failed to check membership:', error);
    }
  };

  const loadProposals = async () => {
    if (!agriDAO) return;
    try {
      const count = await agriDAO.proposalCount();
      const loadedProposals: Proposal[] = [];

      for (let i = 0; i < Number(count); i++) {
        const [proposer, description, forVotes, againstVotes, endTime, executed] =
          await agriDAO.getProposal(i);
        loadedProposals.push({
          id: i,
          proposer,
          description,
          forVotes,
          againstVotes,
          endTime,
          executed
        });
      }

      setProposals(loadedProposals.reverse());
    } catch (error) {
      console.error('Failed to load proposals:', error);
    }
  };

  const joinDAO = async () => {
    if (!agriDAO) return;
    setLoading(true);
    try {
      const tx = await agriDAO.joinDAO();
      await tx.wait();
      toast.success('Successfully joined DAO!');
      setIsMember(true);
    } catch (error: any) {
      toast.error(error.message || 'Failed to join DAO');
    } finally {
      setLoading(false);
    }
  };

  const createProposal = async () => {
    if (!agriDAO || !newProposal.trim() || !title.trim()) return;
    setLoading(true);
    try {
      const fullDescription = `# ${title}\n\n${newProposal}`;
      const tx = await agriDAO.createProposal(fullDescription);
      await tx.wait();
      toast.success('Proposal created!');
      setNewProposal('');
      setTitle('');
      loadProposals();
    } catch (error: any) {
      toast.error(error.message || 'Failed to create proposal');
    } finally {
      setLoading(false);
    }
  };

  const vote = async (proposalId: number, support: boolean) => {
    if (!agriDAO) return;
    setLoading(true);
    try {
      const tx = await agriDAO.vote(proposalId, support);
      await tx.wait();
      toast.success('Vote cast!');
      loadProposals();
    } catch (error: any) {
      toast.error(error.message || 'Failed to vote');
    } finally {
      setLoading(false);
    }
  };

  const executeProposal = async (proposalId: number) => {
    if (!agriDAO) return;
    setLoading(true);
    try {
      const tx = await agriDAO.executeProposal(proposalId);
      await tx.wait();
      toast.success('Proposal executed!');
      loadProposals();
    } catch (error: any) {
      toast.error(error.message || 'Failed to execute proposal');
    } finally {
      setLoading(false);
    }
  };

  if (!account) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="p-6 text-center">
            <p>Please connect your wallet to access DAO governance</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!isMember) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Join AgriDAO</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">Join the DAO to participate in governance and voting.</p>
            <Button onClick={joinDAO} disabled={loading}>
              {loading ? 'Joining...' : 'Join DAO'}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Create Proposal</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder="Proposal Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="mb-2"
          />
          <Textarea
            placeholder="Describe your proposal..."
            value={newProposal}
            onChange={(e) => setNewProposal(e.target.value)}
            rows={4}
          />
          <Button onClick={createProposal} disabled={loading || !newProposal.trim() || !title.trim()}>
            {loading ? 'Creating...' : 'Create Proposal (Web3)'}
          </Button>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Proposals</h2>
        {proposals.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-center text-muted-foreground">
              No proposals yet
            </CardContent>
          </Card>
        ) : (
          proposals.map((proposal) => (
            <Card key={proposal.id}>
              <CardHeader>
                <CardTitle className="text-lg">Proposal #{proposal.id}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>{proposal.description}</p>
                <div className="flex gap-4 text-sm">
                  <div className="text-green-600">For: {proposal.forVotes.toString()}</div>
                  <div className="text-red-600">Against: {proposal.againstVotes.toString()}</div>
                </div>
                <div className="text-sm text-muted-foreground">
                  {proposal.executed ? (
                    <span className="text-green-600">Executed</span>
                  ) : Date.now() / 1000 > Number(proposal.endTime) ? (
                    <span className="text-gray-600">Voting Ended</span>
                  ) : (
                    <span>Ends: {new Date(Number(proposal.endTime) * 1000).toLocaleString()}</span>
                  )}
                </div>
                {!proposal.executed && Date.now() / 1000 < Number(proposal.endTime) && (
                  <div className="flex gap-2">
                    <Button onClick={() => vote(proposal.id, true)} disabled={loading} size="sm">
                      Vote For
                    </Button>
                    <Button onClick={() => vote(proposal.id, false)} disabled={loading} size="sm" variant="outline">
                      Vote Against
                    </Button>
                  </div>
                )}
                {!proposal.executed && Date.now() / 1000 > Number(proposal.endTime) && proposal.forVotes > proposal.againstVotes && (
                  <Button
                    onClick={() => executeProposal(proposal.id)}
                    disabled={loading}
                    size="sm"
                    className="w-full bg-green-600 hover:bg-green-700"
                  >
                    Execute Proposal
                  </Button>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
