import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { listAllUsers, createUser, updateUser, deleteUserById, suspendUser, updateUserRole } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { secureStorage } from "@/lib/security";
import { User } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { Plus, Edit, Trash2, Ban, Shield, AlertTriangle } from "lucide-react";

const UserManagement = () => {
  const { user: currentUser } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [isAddUserOpen, setIsAddUserOpen] = useState(false);
  const [isEditUserOpen, setIsEditUserOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  // Check authentication
  useEffect(() => {
    const token = secureStorage.get<string>("access_token");
    if (!token) {
      toast({
        title: "Authentication Required",
        description: "Please sign in to access this page",
        variant: "destructive",
      });
      navigate("/auth");
    }
  }, [navigate, toast]);

  // Check if user is admin
  if (!currentUser || currentUser.role?.toUpperCase() !== 'ADMIN') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-100 rounded-full">
                <Shield className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <CardTitle>Access Denied</CardTitle>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              You need admin privileges to access user management.
            </p>
            <Button onClick={() => navigate('/dashboard')} className="w-full">
              Go to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { data: users, isLoading, isError, error } = useQuery<User[]>({
    queryKey: ["users"],
    queryFn: listAllUsers,
    retry: 1,
  });

  const createMutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast({ title: "Success", description: "User created successfully." });
      setIsAddUserOpen(false);
    },
    onError: (error) => {
      toast({ title: "Error", description: `Failed to create user: ${error.message}`, variant: "destructive" });
    },
  });

  const updateMutation = useMutation({
    mutationFn: (userData: User) => updateUser(userData.id, userData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast({ title: "Success", description: "User updated successfully." });
      setIsEditUserOpen(false);
    },
    onError: (error) => {
      toast({ title: "Error", description: `Failed to update user: ${error.message}`, variant: "destructive" });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteUserById,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast({ title: "Success", description: "User deleted successfully." });
    },
    onError: (error) => {
      toast({ title: "Error", description: `Failed to delete user: ${error.message}`, variant: "destructive" });
    },
  });

  const suspendMutation = useMutation({
    mutationFn: suspendUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast({ title: "Success", description: "User suspended successfully." });
    },
    onError: (error) => {
      toast({ title: "Error", description: `Failed to suspend user: ${error.message}`, variant: "destructive" });
    },
  });

  const handleAddSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const newUser = Object.fromEntries(formData.entries()) as Omit<User, 'id' | 'created_at'>;
    createMutation.mutate(newUser);
  };

  const handleEditSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedUser) return;
    const formData = new FormData(e.currentTarget);
    const updatedUser = { ...selectedUser, ...Object.fromEntries(formData.entries()) };
    updateMutation.mutate(updatedUser);
  };

  const openEditDialog = (user: User) => {
    setSelectedUser(user);
    setIsEditUserOpen(true);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">User Management</h1>
        <Dialog open={isAddUserOpen} onOpenChange={setIsAddUserOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add User
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New User</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleAddSubmit} className="space-y-4">
              {/* Add User Form Fields */}
              <UserFormFields />
              <DialogFooter>
                <DialogClose asChild>
                  <Button type="button" variant="secondary">Cancel</Button>
                </DialogClose>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? "Creating..." : "Create User"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Loading users...</p>
            </div>
          )}
          {isError && (
            <div className="text-center py-8">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="p-3 bg-red-100 rounded-full">
                  <AlertTriangle className="h-6 w-6 text-red-600" />
                </div>
              </div>
              <h3 className="text-lg font-semibold mb-2">Error Loading Users</h3>
              <p className="text-sm text-muted-foreground mb-4">
                {error instanceof Error ? error.message : "Failed to fetch users. Please try again."}
              </p>
              <Button onClick={() => queryClient.invalidateQueries({ queryKey: ["users"] })}>
                Retry
              </Button>
            </div>
          )}
          {users && users.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No users found
            </div>
          )}
          {users && users.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Joined At</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.id}</TableCell>
                    <TableCell>{user.name}</TableCell>
                    <TableCell>{user.email ?? "N/A"}</TableCell>
                    <TableCell>{user.role}</TableCell>
                    <TableCell>
                      <Badge variant={user.status === 'ACTIVE' ? 'default' : 'destructive'}>
                        {user.status || 'ACTIVE'}
                      </Badge>
                    </TableCell>
                    <TableCell>{new Date(user.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button variant="ghost" size="icon" onClick={() => openEditDialog(user)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          onClick={() => suspendMutation.mutate(user.id)}
                          title="Suspend user"
                        >
                          <Ban className="h-4 w-4 text-orange-500" />
                        </Button>
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <Trash2 className="h-4 w-4 text-red-500" />
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                              <AlertDialogDescription>
                                This action cannot be undone. This will permanently delete the user.
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction onClick={() => deleteMutation.mutate(user.id)}>
                                Delete
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Edit User Dialog */}
      <Dialog open={isEditUserOpen} onOpenChange={setIsEditUserOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit User</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEditSubmit} className="space-y-4">
            <UserFormFields user={selectedUser} />
            <DialogFooter>
              <DialogClose asChild>
                <Button type="button" variant="secondary">Cancel</Button>
              </DialogClose>
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? "Saving..." : "Save Changes"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

const UserFormFields = ({ user }: { user?: User | null }) => (
  <>
    <div>
      <Label htmlFor="name">Name</Label>
      <Input id="name" name="name" defaultValue={user?.name} required />
    </div>
    <div>
      <Label htmlFor="email">Email</Label>
      <Input id="email" name="email" type="email" defaultValue={user?.email} />
    </div>
    <div>
      <Label htmlFor="phone">Phone</Label>
      <Input id="phone" name="phone" defaultValue={user?.phone} />
    </div>
    <div>
      <Label htmlFor="role">Role</Label>
      <Select name="role" defaultValue={user?.role}>
        <SelectTrigger>
          <SelectValue placeholder="Select a role" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="buyer">Buyer</SelectItem>
          <SelectItem value="farmer">Farmer</SelectItem>
          <SelectItem value="admin">Admin</SelectItem>
        </SelectContent>
      </Select>
    </div>
  </>
);

export default UserManagement;
