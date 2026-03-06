"use client";

import { useMemo, useEffect, useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { safeGetDecisions } from "@/lib/api";
import { KPICard } from "@/components/kpi-card";
import { RiskDistributionChart } from "@/components/risk-distribution-chart";
import { ComplianceStatusChart } from "@/components/compliance-status-chart";
import { RecentActivity } from "@/components/recent-activity";
import {
  FileText,
  AlertTriangle,
  ShieldCheck,
  Activity,
} from "lucide-react";
import type { DashboardKPIs } from "@/lib/types";

export default function DashboardPage() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await safeGetDecisions({ limit: 100 });
        setDocuments(res?.data ?? []);
      } catch (e) {
        console.error("Failed to load dashboard documents", e);
        setDocuments([]);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const kpis: DashboardKPIs = useMemo(() => {
    const totalDocuments = documents.length;
    const highRiskCount = documents.filter((d) => d.risk_level === "HIGH").length;
    const lowRiskCount = documents.filter((d) => d.risk_level === "LOW").length;
    const avgConfidence =
      totalDocuments > 0
        ? documents.reduce((sum, d) => sum + d.confidence, 0) / totalDocuments
        : 0;
    const compliantCount = documents.filter(
      (d) => d.status === "COMPLIANT"
    ).length;
    const nonCompliantCount = documents.filter(
      (d) => d.status === "NON_COMPLIANT"
    ).length;

    return {
      totalDocuments,
      highRiskCount,
      lowRiskCount,
      avgConfidence,
      compliantCount,
      nonCompliantCount,
    };
  }, [documents]);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground text-balance">
          Welcome back, {user?.username || "User"}
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Here is your compliance intelligence overview.
        </p>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Total Documents"
          value={kpis.totalDocuments}
          subtitle={`${kpis.compliantCount} compliant`}
          icon={FileText}
          accentColor="text-primary"
        />
        <KPICard
          title="High Risk"
          value={kpis.highRiskCount}
          subtitle="Requires attention"
          icon={AlertTriangle}
          accentColor="text-destructive"
        />
        <KPICard
          title="Low Risk"
          value={kpis.lowRiskCount}
          subtitle="Within tolerance"
          icon={ShieldCheck}
          accentColor="text-success"
        />
        <KPICard
          title="Avg Confidence"
          value={`${(kpis.avgConfidence * 100).toFixed(1)}%`}
          subtitle="AI model accuracy"
          icon={Activity}
          accentColor="text-primary"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <RiskDistributionChart
          highRisk={kpis.highRiskCount}
          lowRisk={kpis.lowRiskCount}
        />
        <ComplianceStatusChart documents={documents} />
      </div>

      {/* Recent Activity */}
      <RecentActivity documents={documents} />
    </div>
  );
}
