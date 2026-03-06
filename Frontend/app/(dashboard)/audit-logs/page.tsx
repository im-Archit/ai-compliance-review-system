"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import { ScrollText } from "lucide-react";
import type { AuditLogEntry } from "@/lib/types";
import { safeGetAuditLogs } from "@/lib/api";

const EVENT_TYPE_COLORS: Record<string, string> = {
  COMPLIANCE_FETCHED: "bg-primary/10 text-primary border-primary/20",
  DOCUMENT_UPLOADED: "bg-success/10 text-success border-success/20",
  OCR_COMPLETED: "bg-success/10 text-success border-success/20",
  ANALYSIS_COMPLETED: "bg-success/10 text-success border-success/20",
  COMPLIANCE_STORED: "bg-primary/10 text-primary border-primary/20",
  OCR_FAILED: "bg-destructive/10 text-destructive border-destructive/20",
};

export default function AuditLogsPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "Admin";

  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadLogs = async () => {
      try {
        const res = await safeGetAuditLogs({
          limit: 100,
          offset: 0,
        });

        setLogs(res?.data ?? []);
      } catch (err) {
        console.error("Failed to load audit logs", err);
        setLogs([]);
      } finally {
        setLoading(false);
      }
    };

    loadLogs();
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Audit Logs</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {isAdmin
            ? "Full access to all system audit events."
            : "Read-only view of compliance audit events."}
        </p>
      </div>

      <Card className="glass-card">
        <CardHeader className="pb-0">
          <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <ScrollText className="h-4 w-4" />
            {logs.length} events recorded
          </CardTitle>
        </CardHeader>

        <CardContent className="p-0">
          {loading ? (
            <div className="py-10 text-center text-muted-foreground">
              Loading audit logs...
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead>Event</TableHead>
                    <TableHead>Reference</TableHead>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Details</TableHead>
                  </TableRow>
                </TableHeader>

                <TableBody>
                  {logs.map((log) => (
                    <TableRow
                      key={log.id}
                      className="border-border/50 hover:bg-secondary/30"
                    >
                      <TableCell>
                        <Badge
                          className={cn(
                            "text-xs",
                            EVENT_TYPE_COLORS[log.event_type] ||
                              "bg-secondary text-secondary-foreground"
                          )}
                        >
                          {log.event_type.replace(/_/g, " ")}
                        </Badge>
                      </TableCell>

                      <TableCell className="font-mono text-xs">
                        {log.document_id || log.user_id || "-"}
                      </TableCell>

                      <TableCell className="text-xs text-muted-foreground">
                        {new Date(log.timestamp).toLocaleString()}
                      </TableCell>

                      <TableCell className="max-w-md text-xs text-muted-foreground">
                        {log.details}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}