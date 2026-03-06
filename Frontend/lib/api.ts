// ============================================================
// SatyamAI – Central API Client (JWT VERSION)
// ============================================================

import type {
  ComplianceDocument,
  DecisionRecord,
  HealthCheckResponse,
} from "./types";

const COMPLIANCE_API_BASE =
  process.env.NEXT_PUBLIC_COMPLIANCE_API_URL || "http://localhost:8003";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const token = getToken();

    const headers: Record<string, string> = {};

    // Preserve existing headers if provided
    if (options?.headers && typeof options.headers === "object") {
      Object.assign(headers, options.headers as Record<string, string>);
    }

    // Attach JWT if present
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    // Automatically set JSON content type for body requests
    if (options?.body && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    const res = await fetch(url, {
      ...options,
      method: options?.method || "GET",
      headers: headers,
    });

    if (!res.ok) {
      throw new Error(`API Error: ${res.status}`);
    }

    return (await res.json()) as T;
  }

  async getComplianceDocument(
    documentId: string
  ): Promise<ComplianceDocument> {
    return this.request(`/compliance/${documentId}`);
  }

  async getDecisions(query?: string): Promise<{
    total: number;
    limit: number;
    offset: number;
    data: DecisionRecord[];
  }> {
    const endpoint = query ? `/decisions?${query}` : "/decisions";
    return this.request(endpoint);
  }

  async getHealth(): Promise<HealthCheckResponse> {
    return this.request("/health");
  }
}

export const complianceApi = new ApiClient(COMPLIANCE_API_BASE);


// ============================================================
// SAFE WRAPPERS
// ============================================================

export async function safeGetDecisions(params?: {
  risk_level?: string;
  status?: string;
  document_id?: string;
  limit?: number;
  offset?: number;
}) {
  try {
    const query = new URLSearchParams();

    if (params?.risk_level) query.append("risk_level", params.risk_level);
    if (params?.status) query.append("status", params.status);
    if (params?.document_id) query.append("document_id", params.document_id);
    if (params?.limit) query.append("limit", params.limit.toString());
    if (params?.offset) query.append("offset", params.offset.toString());

    const qs = query.toString();

    return await complianceApi.getDecisions(qs);
  } catch {
    return { total: 0, limit: 0, offset: 0, data: [] };
  }
}

export async function safeGetDecisionById(documentId: string) {
  try {
    return await complianceApi.getComplianceDocument(documentId);
  } catch {
    return null;
  }
}

export async function safeGetAuditLogs(params?: {
  document_id?: string;
  limit?: number;
  offset?: number;
}) {
  try {
    const query = new URLSearchParams();

    if (params?.document_id) query.append("document_id", params.document_id);
    if (params?.limit) query.append("limit", params.limit.toString());
    if (params?.offset) query.append("offset", params.offset.toString());

    const qs = query.toString();

    return await complianceApi.request(
      `/audit-logs${qs ? `?${qs}` : ""}`
    );
  } catch {
    return { total: 0, limit: 0, offset: 0, data: [] };
  }
}

export async function safeGetSignedUrl(documentId: string) {
  try {
    return await complianceApi.request(
      `/documents/${documentId}/signed-url`
    );
  } catch {
    return null;
  }
}