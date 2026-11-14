import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Users,
  UserPlus,
  Upload,
  Search,
  Trash2,
  Edit,
  Shield,
  GraduationCap,
  School,
  FileSpreadsheet,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Modal } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { formatDate } from '@/lib/utils';

export const UserManagementPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');

  // Modals state
  const [addUserOpen, setAddUserOpen] = useState(false);
  const [newEmail, setNewEmail] = useState('');
  const [newName, setNewName] = useState('');
  const [newRole, setNewRole] = useState('student');
  const [newStudentId, setNewStudentId] = useState('');

  const [bulkImportOpen, setBulkImportOpen] = useState(false);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [bulkResult, setBulkResult] = useState<{ imported_count: number; errors: string[] } | null>(null);

  const [editUserOpen, setEditUserOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<any>(null);

  // Queries
  const { data: usersData, isLoading } = useQuery({
    queryKey: ['admin-users', page, search, roleFilter],
    queryFn: async () => {
      let url = `/users?page=${page}&per_page=15`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      if (roleFilter) url += `&role=${roleFilter}`;
      const res = await apiClient.get(url);
      return res.data;
    },
  });

  // Mutations
  const createUserMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await apiClient.post('/users', payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      setAddUserOpen(false);
      setNewEmail('');
      setNewName('');
      setNewStudentId('');
    },
  });

  const updateUserMutation = useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: any }) => {
      const res = await apiClient.put(`/users/${id}`, payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      setEditUserOpen(false);
      setEditingUser(null);
    },
  });

  const deleteUserMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/users/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
  });

  const bulkImportMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const res = await apiClient.post('/users/bulk-import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      setBulkResult(data);
    },
  });

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'admin':
        return (
          <Badge variant="destructive" className="gap-1 text-[10px]">
            <Shield className="h-3 w-3" /> Admin
          </Badge>
        );
      case 'teacher':
        return (
          <Badge variant="default" className="gap-1 text-[10px]">
            <GraduationCap className="h-3 w-3" /> Teacher
          </Badge>
        );
      default:
        return (
          <Badge variant="secondary" className="gap-1 text-[10px]">
            <School className="h-3 w-3" /> Student
          </Badge>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight flex items-center gap-2">
            <Users className="h-7 w-7 text-primary" />
            <span>User Management</span>
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Admin oversight: Manage faculty, students, student pool, and bulk CSV uploads.
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setBulkResult(null);
              setBulkImportOpen(true);
            }}
            className="gap-1.5"
          >
            <FileSpreadsheet className="h-4 w-4" />
            <span>Bulk CSV Import</span>
          </Button>
          <Button size="sm" onClick={() => setAddUserOpen(true)} className="gap-1.5">
            <UserPlus className="h-4 w-4" />
            <span>Add User</span>
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name, email, or student ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option value="">All Roles</option>
          <option value="admin">Admin</option>
          <option value="teacher">Teacher</option>
          <option value="student">Student</option>
        </select>
      </div>

      {/* Table */}
      <Card className="overflow-x-auto border">
        {isLoading ? (
          <div className="p-8 text-center text-sm text-muted-foreground">Loading users...</div>
        ) : !usersData?.data || usersData.data.length === 0 ? (
          <div className="p-8 text-center text-sm text-muted-foreground">No users found.</div>
        ) : (
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="border-b bg-muted/50 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                <th className="p-3 pl-4">User</th>
                <th className="p-3">Role</th>
                <th className="p-3">Student ID</th>
                <th className="p-3">Created</th>
                <th className="p-3 pr-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {usersData.data.map((u: any) => (
                <tr key={u.id} className="hover:bg-muted/30">
                  <td className="p-3 pl-4">
                    <div className="flex items-center gap-3">
                      <img
                        src={u.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${u.email}`}
                        alt={u.full_name}
                        className="h-8 w-8 rounded-full border bg-muted"
                      />
                      <div>
                        <div className="font-semibold text-foreground">{u.full_name}</div>
                        <div className="text-xs text-muted-foreground">{u.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="p-3">{getRoleBadge(u.role)}</td>
                  <td className="p-3 font-mono text-xs">{u.student_id || '-'}</td>
                  <td className="p-3 text-xs text-muted-foreground">{formatDate(u.created_at)}</td>
                  <td className="p-3 pr-4 text-right space-x-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setEditingUser(u);
                        setEditUserOpen(true);
                      }}
                      className="h-7 w-7 text-muted-foreground hover:text-foreground"
                    >
                      <Edit className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        if (confirm(`Are you sure you want to delete user ${u.full_name}?`)) {
                          deleteUserMutation.mutate(u.id);
                        }
                      }}
                      className="h-7 w-7 text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      {/* Pagination */}
      {usersData?.meta && (
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>
            Showing page {usersData.meta.page} of {usersData.meta.total_pages} (Total: {usersData.meta.total} users)
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= usersData.meta.total_pages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}

      {/* Add User Modal */}
      <Modal
        isOpen={addUserOpen}
        onClose={() => setAddUserOpen(false)}
        title="Add System User"
        description="Create or pre-register a user with institutional role."
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            createUserMutation.mutate({
              email: newEmail,
              full_name: newName,
              role: newRole,
              student_id: newStudentId || null,
            });
          }}
          className="space-y-4"
        >
          <div className="space-y-1">
            <label className="text-xs font-semibold">Full Name *</label>
            <Input
              required
              placeholder="e.g. Marie Curie"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold">Institutional Email *</label>
            <Input
              type="email"
              required
              placeholder="marie.curie@openlms.edu"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-semibold">Role *</label>
              <select
                value={newRole}
                onChange={(e) => setNewRole(e.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              >
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
                <option value="admin">Administrator</option>
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-semibold">Student ID (optional)</label>
              <Input
                placeholder="e.g. STU1045"
                value={newStudentId}
                onChange={(e) => setNewStudentId(e.target.value)}
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setAddUserOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createUserMutation.isPending}>
              Create User
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit User Modal */}
      <Modal
        isOpen={editUserOpen}
        onClose={() => setEditUserOpen(false)}
        title="Edit User Profile & Role"
        description={`Update role or details for ${editingUser?.email}`}
      >
        {editingUser && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              updateUserMutation.mutate({
                id: editingUser.id,
                payload: {
                  full_name: editingUser.full_name,
                  role: editingUser.role,
                  student_id: editingUser.student_id,
                },
              });
            }}
            className="space-y-4"
          >
            <div className="space-y-1">
              <label className="text-xs font-semibold">Full Name *</label>
              <Input
                required
                value={editingUser.full_name}
                onChange={(e) =>
                  setEditingUser({ ...editingUser, full_name: e.target.value })
                }
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-semibold">Role *</label>
              <select
                value={editingUser.role}
                onChange={(e) =>
                  setEditingUser({ ...editingUser, role: e.target.value })
                }
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              >
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
                <option value="admin">Administrator</option>
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-semibold">Student ID</label>
              <Input
                value={editingUser.student_id || ''}
                onChange={(e) =>
                  setEditingUser({ ...editingUser, student_id: e.target.value })
                }
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={() => setEditUserOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={updateUserMutation.isPending}>
                Save Changes
              </Button>
            </div>
          </form>
        )}
      </Modal>

      {/* Bulk CSV Import Modal (Pathway A) */}
      <Modal
        isOpen={bulkImportOpen}
        onClose={() => setBulkImportOpen(false)}
        title="Bulk Student Pool Import (Pathway A)"
        description="Upload a CSV file to pre-register student records into the pool."
      >
        <div className="space-y-4">
          <div className="p-3 rounded-lg bg-muted text-xs space-y-1">
            <p className="font-semibold">Required CSV format:</p>
            <code className="block bg-background p-2 rounded border font-mono text-[11px]">
              name,email,student_id<br />
              John Doe,john.doe@openlms.edu,STU2001<br />
              Jane Smith,jane.smith@openlms.edu,STU2002
            </code>
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (csvFile) {
                bulkImportMutation.mutate(csvFile);
              }
            }}
            className="space-y-4"
          >
            <div className="space-y-1">
              <label className="text-xs font-semibold">Select CSV File *</label>
              <Input
                type="file"
                accept=".csv"
                required
                onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
              />
            </div>

            {bulkResult && (
              <div className="p-3 rounded-lg border bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 text-xs space-y-1">
                <p className="font-bold">
                  Successfully imported / updated {bulkResult.imported_count} student record(s)!
                </p>
                {bulkResult.errors.length > 0 && (
                  <div className="text-destructive mt-1">
                    <p className="font-semibold">Warnings:</p>
                    <ul className="list-disc pl-4 space-y-0.5">
                      {bulkResult.errors.map((err, i) => (
                        <li key={i}>{err}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={() => setBulkImportOpen(false)}>
                Close
              </Button>
              <Button type="submit" disabled={!csvFile || bulkImportMutation.isPending}>
                {bulkImportMutation.isPending ? 'Importing...' : 'Upload & Import'}
              </Button>
            </div>
          </form>
        </div>
      </Modal>
    </div>
  );
};
