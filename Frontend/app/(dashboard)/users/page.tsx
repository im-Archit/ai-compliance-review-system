"use client";

import { useState, useCallback, useEffect } from "react";
import { useAuth } from "@/components/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { Users, Shield, Loader2 } from "lucide-react";
import type { User, UserRole } from "@/lib/types";

const ROLE_COLORS: Record<UserRole, string> = {
  Admin: "bg-primary/10 text-primary border-primary/20",
  Analyst: "bg-warning/10 text-warning border-warning/20",
  Reviewer: "bg-muted text-muted-foreground border-border",
};

export default function UsersPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingUser, setUpdatingUser] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    try {
      const res = await fetch("/api/auth/users");
      if (res.ok) {
        const data = await res.json();
        setUsers(data.users);
      } else {
        toast.error("Failed to fetch users");
      }
    } catch {
      toast.error("Network error fetching users");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  async function handleRoleChange(username: string, newRole: UserRole) {
    setUpdatingUser(username);
    try {
      const res = await fetch("/api/auth/users", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, role: newRole }),
      });
      if (res.ok) {
        toast.success(`Role updated to ${newRole} for ${username}`);
        await fetchUsers();
      } else {
        toast.error("Failed to update role");
      }
    } catch {
      toast.error("Network error");
    } finally {
      setUpdatingUser(null);
    }
  }

  async function handleToggleEnabled(username: string, enabled: boolean) {
    setUpdatingUser(username);
    try {
      const res = await fetch("/api/auth/users", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, enabled }),
      });
      if (res.ok) {
        toast.success(
          `${username} ${enabled ? "enabled" : "disabled"} successfully`
        );
        await fetchUsers();
      } else {
        toast.error("Failed to update user");
      }
    } catch {
      toast.error("Network error");
    } finally {
      setUpdatingUser(null);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">User Management</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage user roles and access permissions. Changes take effect immediately.
        </p>
      </div>

      <Card className="glass-card">
        <CardHeader className="pb-0">
          <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Users className="h-4 w-4" />
            {users.length} user{users.length !== 1 ? "s" : ""} registered
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {users.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Shield className="h-10 w-10 text-muted-foreground/30" />
              <p className="mt-3 text-sm text-muted-foreground">
                No users found. Users will appear once they log in.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead className="text-muted-foreground">Username</TableHead>
                    <TableHead className="text-muted-foreground">Role</TableHead>
                    <TableHead className="text-muted-foreground">Status</TableHead>
                    <TableHead className="text-muted-foreground">Created</TableHead>
                    <TableHead className="text-muted-foreground">Last Login</TableHead>
                    <TableHead className="text-muted-foreground">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.map((u) => {
                    const isSelf = u.username === currentUser?.username;
                    const isUpdating = updatingUser === u.username;

                    return (
                      <TableRow
                        key={u.id}
                        className={cn(
                          "border-border/50 transition-colors",
                          isUpdating
                            ? "opacity-60"
                            : "hover:bg-secondary/30"
                        )}
                      >
                        <TableCell className="font-medium text-foreground">
                          <div className="flex items-center gap-2">
                            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                              {u.username.charAt(0).toUpperCase()}
                            </div>
                            <span>{u.username}</span>
                            {isSelf && (
                              <Badge
                                variant="outline"
                                className="text-xs border-primary/20 text-primary"
                              >
                                You
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          {isSelf ? (
                            <Badge className={cn("text-xs", ROLE_COLORS[u.role])}>
                              {u.role}
                            </Badge>
                          ) : (
                            <Select
                              value={u.role}
                              onValueChange={(v) =>
                                handleRoleChange(u.username, v as UserRole)
                              }
                              disabled={isUpdating}
                            >
                              <SelectTrigger className="w-28 h-8 bg-secondary/50 text-foreground text-xs">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent className="bg-popover text-popover-foreground">
                                <SelectItem value="Admin">Admin</SelectItem>
                                <SelectItem value="Analyst">Analyst</SelectItem>
                                <SelectItem value="Reviewer">Reviewer</SelectItem>
                              </SelectContent>
                            </Select>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge
                            className={cn(
                              "text-xs",
                              u.enabled
                                ? "bg-success/10 text-success border-success/20"
                                : "bg-destructive/10 text-destructive border-destructive/20"
                            )}
                          >
                            {u.enabled ? "Active" : "Disabled"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground">
                          {new Date(u.createdAt).toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                          })}
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground">
                          {u.lastLogin
                            ? new Date(u.lastLogin).toLocaleString("en-US", {
                                month: "short",
                                day: "numeric",
                                hour: "2-digit",
                                minute: "2-digit",
                              })
                            : "Never"}
                        </TableCell>
                        <TableCell>
                          {isSelf ? (
                            <span className="text-xs text-muted-foreground">-</span>
                          ) : (
                            <div className="flex items-center gap-2">
                              <Switch
                                checked={u.enabled}
                                onCheckedChange={(checked) =>
                                  handleToggleEnabled(u.username, checked)
                                }
                                disabled={isUpdating}
                              />
                              <span className="text-xs text-muted-foreground">
                                {u.enabled ? "Enabled" : "Disabled"}
                              </span>
                            </div>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
