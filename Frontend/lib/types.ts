// ============================================================
// SatyamAI – Enterprise Compliance Intelligence Platform
// Core TypeScript types
// ============================================================

export type UserRole = "Admin" | "Analyst" | "Reviewer";

export interface User {
  id: string;
  username: string;
  role: UserRole;
  enabled: boolean;
  createdAt: string;
  lastLogin: string | null;
}

export interface SessionPayload {
  userId: string;
  username: string;
  role: UserRole;
  expiresAt: number;
}

// Compliance API response shape
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";

export type ComplianceStatus =
  | "COMPLIANT"
  | "REVIEW_REQUIRED"
  | "REJECTED";
export type DocumentType = "INFORMATIONAL" | "REGULATORY" | "FINANCIAL" | "LEGAL" | "OPERATIONAL";

export interface ComplianceDocument {
  document_id: string;
  document_type: DocumentType;
  risk_level: RiskLevel;
  status: ComplianceStatus;
  flags: string[];
  confidence: number;
  explanation: string;
  timestamp?: string;
  rules_triggered?: string[];
  recommendations?: string[];
  timeline?: TimelineEvent[];
}

export interface TimelineEvent {
  stage: string;
  status: "completed" | "in_progress" | "pending";
  timestamp: string;
  description?: string;
}

export interface DecisionRecord {
  document_id: string;
  document_type: DocumentType;
  risk_level: RiskLevel;
  status: ComplianceStatus;
  confidence: number;
  explanation: string;
  timestamp: string;
}

export interface AuditLogEntry {
  id: string;
  event_type: "DOCUMENT_REVIEWED" | "ROLE_CHANGED" | "USER_DISABLED" | "USER_ENABLED" | "LOGIN" | "LOGOUT" | "COMPLIANCE_CHECK";
  document_id?: string;
  user_id?: string;
  timestamp: string;
  details: string;
}

export interface HealthCheckResponse {
  status: "ok" | "error";
  timestamp: string;
}

// Dashboard KPIs
export interface DashboardKPIs {
  totalDocuments: number;
  highRiskCount: number;
  lowRiskCount: number;
  avgConfidence: number;
  compliantCount: number;
  nonCompliantCount: number;
}
