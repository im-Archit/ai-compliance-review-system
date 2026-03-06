"use client";

import { notFound, useParams } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { safeGetDecisionById, safeGetAuditLogs } from "@/lib/api";
import { safeGetSignedUrl } from "@/lib/api";
import type { ComplianceDocument } from "@/lib/types";
import { useState, useEffect } from "react";
import { useAuth } from "@/components/auth-provider";

export default function DocumentDetailPage() {
  const params = useParams<{ documentId: string }>();
  const documentId = params?.documentId as string;

  const [decision, setDecision] = useState<ComplianceDocument | null>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [signedUrl, setSignedUrl] = useState<string | null>(null);
  const [fileMeta, setFileMeta] = useState<{ filename: string; content_type: string } | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const PIPELINE_STAGES = [
    { success: "DOCUMENT_UPLOADED", failure: null },
    { success: "OCR_COMPLETED", failure: "OCR_FAILED" },
    { success: "ANALYSIS_COMPLETED", failure: "ANALYSIS_FAILED" },
    { success: "COMPLIANCE_STORED", failure: "COMPLIANCE_FAILED" },
  ];
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;

    const load = async () => {
      if (!user) {
        setLoading(false);
        return false;
      }

      try {
        const doc = await safeGetDecisionById(documentId);

        if (!doc) {
          notFound();
          return false;
        }

        setDecision(doc as ComplianceDocument);

        const logsResponse: any = await safeGetAuditLogs({
          document_id: documentId,
          limit: 50,
          offset: 0,
        });
        const logs = (logsResponse?.data ?? []) as any[];
        setAuditLogs(logs);

        // Stop polling if pipeline is complete
        const isComplete = logs.some(
          (log: any) => log.event === "COMPLIANCE_STORED"
        );

        return isComplete;
      } catch (error) {
        console.error("Failed to load document", error);
        return false;
      } finally {
        setLoading(false);
      }
    };

    const startPolling = async () => {
      const completed = await load();

      if (!completed) {
        intervalId = setInterval(async () => {
          const done = await load();
          if (done && intervalId) {
            clearInterval(intervalId);
          }
        }, 5000);
      }
    };

    startPolling();

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [documentId, user]);

  if (!user) {
    return (
      <div className="text-muted-foreground">
        You must be logged in to view this document.
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" />
      </div>
    );
  }

  if (!decision) {
    notFound();
  }

  const eventsMap = new Map(
    auditLogs.map((log) => [log.event, log])
  );

  const timeline = PIPELINE_STAGES.map((stageDef) => {
    const successEvent = stageDef.success;
    const failureEvent = stageDef.failure;

    const successLog = eventsMap.get(successEvent);
    const failureLog = failureEvent ? eventsMap.get(failureEvent) : null;

    if (failureLog) {
      return {
        label: successEvent.replace(/_/g, " "),
        status: "failed",
        timestamp: failureLog.created_at,
        error: failureLog.details?.error || null,
      };
    }

    if (successLog) {
      return {
        label: successEvent.replace(/_/g, " "),
        status: "completed",
        timestamp: successLog.created_at,
        error: null,
      };
    }

    return {
      label: successEvent.replace(/_/g, " "),
      status: "pending",
      timestamp: null,
      error: null,
    };
  });

  const handlePreview = async () => {
    try {
      setLoadingPreview(true);
      const data: any = await safeGetSignedUrl(decision.document_id);
      if (!data) return;
      setSignedUrl(data.signed_url);
      setFileMeta({
        filename: data.filename,
        content_type: data.content_type,
      });
      setPreviewOpen(true);
    } catch (error) {
      console.error("Failed to fetch signed URL", error);
    } finally {
      setLoadingPreview(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardContent className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 py-6">
          <div className="flex flex-col gap-2">
            <div className="text-xs uppercase tracking-wide text-muted-foreground">
              Document Identifier
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <div className="px-4 py-2 bg-muted rounded-md text-sm font-medium">
                {fileMeta?.filename || decision.document_id}
              </div>
              <button
                onClick={() => navigator.clipboard.writeText(decision.document_id)}
                className="text-xs text-primary hover:underline"
              >
                Copy ID
              </button>
              <button
                onClick={handlePreview}
                className="text-xs bg-primary text-white px-3 py-1 rounded-md hover:opacity-90"
                disabled={loadingPreview}
              >
                {loadingPreview ? "Loading..." : "View Document"}
              </button>
            </div>
          </div>

          <div className="flex gap-2">
            <Badge
              className={
                decision.risk_level === "HIGH"
                  ? "bg-destructive/10 text-destructive"
                  : "bg-green-100 text-green-700"
              }
            >
              {decision.risk_level}
            </Badge>
            <Badge variant="outline">{decision.status}</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Compliance Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Compliance Overview</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="text-sm text-muted-foreground mb-1">
              Model Confidence
            </div>
            <div className="flex items-center gap-3">
              <div className="w-full bg-muted rounded-full h-3 overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{
                    width: `${(decision.confidence * 100).toFixed(1)}%`,
                  }}
                />
              </div>
              <span className="text-sm font-medium">
                {(decision.confidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Explanation */}
      {decision.explanation && (
        <Card>
          <CardHeader>
            <CardTitle>AI Explanation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="p-4 bg-muted rounded-md text-sm leading-relaxed">
              {decision.explanation}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Triggered Rules */}
      {decision.flags?.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Triggered Rules</CardTitle>
          </CardHeader>
          <CardContent>
            {decision.flags?.map((flag) => (
              <Badge key={flag} variant="destructive" className="mr-2">
                {flag}
              </Badge>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Pipeline Timeline */}
      {timeline.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Pipeline Lifecycle</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {timeline.map((item) => (
              <div key={item.label} className="flex items-start gap-3">
                <div
                  className={`h-3 w-3 mt-1 rounded-full ring-2 ring-background ${
                    item.status === "completed"
                      ? "bg-green-500"
                      : item.status === "failed"
                      ? "bg-red-500"
                      : "bg-gray-300"
                  }`}
                />

                <div className="flex-1">
                  <div className="font-medium">{item.label}</div>

                  {item.status === "completed" && item.timestamp && (
                    <div className="text-xs text-green-600">
                      Completed at {new Date(item.timestamp).toLocaleString()}
                    </div>
                  )}

                  {item.status === "failed" && (
                    <div className="text-xs text-red-600">
                      Failed at {new Date(item.timestamp).toLocaleString()}
                      {item.error && (
                        <div className="mt-1 text-red-500">
                          Error: {item.error}
                        </div>
                      )}
                    </div>
                  )}

                  {item.status === "pending" && (
                    <div className="text-xs text-muted-foreground">
                      Pending...
                    </div>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Audit Trail */}
      {auditLogs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Audit Trail</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {auditLogs.map((log) => (
              <div
                key={log.id}
                className="border rounded-md p-3 text-sm space-y-1"
              >
                <div className="flex justify-between">
                  <span className="font-medium">{log.event}</span>
                  <span className="text-muted-foreground">
                    {new Date(log.created_at).toLocaleString()}
                  </span>
                </div>

                {log.details && Object.keys(log.details).length > 0 && (
  <div className="mt-1 text-xs text-muted-foreground space-y-1">
    {Object.entries(log.details).map(([key, value]) => (
      <div key={key}>
        <span className="font-medium capitalize">
          {key.replace(/_/g, " ")}:
        </span>{" "}
        {String(value)}
      </div>
    ))}
  </div>
)}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {previewOpen && signedUrl && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="bg-white w-[90%] h-[90%] rounded-lg shadow-lg flex flex-col">
            <div className="flex justify-between items-center px-4 py-3 border-b">
              <div className="font-medium">
                {fileMeta?.filename || "Document Preview"}
              </div>
              <button
                onClick={() => setPreviewOpen(false)}
                className="text-sm text-muted-foreground hover:text-black"
              >
                Close
              </button>
            </div>

            <div className="flex-1 overflow-auto">
              {fileMeta?.content_type?.includes("image") && (
                <img
                  src={signedUrl}
                  alt="Document"
                  className="max-w-full max-h-full mx-auto"
                />
              )}

              {fileMeta?.content_type?.includes("pdf") && (
                <iframe
                  src={signedUrl}
                  className="w-full h-full"
                  title="PDF Preview"
                />
              )}

              {!fileMeta?.content_type && (
                <div className="p-4 text-sm text-muted-foreground">
                  Preview not supported for this file type.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}