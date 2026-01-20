import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listProposals, createProposal, closeProposal } from "@/lib/api";
import { Proposal } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { Plus } from "lucide-react";
import { useTranslation } from "@/i18n/config";

const Governance = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const { data: proposals, isLoading, isError } = useQuery<Proposal[]>({
    queryKey: ["proposals"],
    queryFn: listProposals,
  });

  const createMutation = useMutation({
    mutationFn: createProposal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["proposals"] });
      toast({ title: "Success", description: "Proposal created successfully." });
      setIsDialogOpen(false);
    },
    onError: (error) => {
      toast({ title: "Error", description: `Failed to create proposal: ${error.message}`, variant: "destructive" });
    },
  });

  const closeMutation = useMutation({
    mutationFn: ({ proposalId, outcome }: { proposalId: number; outcome: "passed" | "rejected" }) => closeProposal(proposalId, outcome),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["proposals"] });
      toast({ title: "Success", description: "Proposal status updated." });
    },
    onError: (error) => {
      toast({ title: "Error", description: `Failed to update proposal: ${error.message}`, variant: "destructive" });
    },
  });

  const handleCreateSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const newProposal = Object.fromEntries(formData.entries()) as Partial<Proposal>;
    createMutation.mutate(newProposal);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Governance</h1>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Proposal
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>New Proposal</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div>
                <Label htmlFor="title">Title</Label>
                <Input id="title" name="title" required />
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Input id="description" name="description" />
              </div>
              <DialogFooter>
                <DialogClose asChild>
                  <Button type="button" variant="secondary">Cancel</Button>
                </DialogClose>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? "Creating..." : "Submit"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Proposals</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p>Loading proposals...</p>}
          {isError && <p>Error fetching proposals.</p>}
          {proposals && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created At</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {proposals.map((proposal) => (
                  <TableRow key={proposal.id}>
                    <TableCell>{proposal.id}</TableCell>
                    <TableCell>{proposal.title}</TableCell>
                    <TableCell>{proposal.status}</TableCell>
                    <TableCell>{new Date(proposal.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      {proposal.status === 'open' && (
                        <div className="flex gap-2">
                          <Button size="sm" onClick={() => closeMutation.mutate({ proposalId: proposal.id, outcome: 'passed' })}>Pass</Button>
                          <Button size="sm" variant="destructive" onClick={() => closeMutation.mutate({ proposalId: proposal.id, outcome: 'rejected' })}>Reject</Button>
                        </div>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Governance;
