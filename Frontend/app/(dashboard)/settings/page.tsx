"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Settings, Server, Shield, Database } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Platform configuration and system settings. Admin access only.
        </p>
      </div>

      {/* API Configuration */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-foreground">
            <Server className="h-4 w-4 text-primary" />
            API Configuration
          </CardTitle>
          <CardDescription className="text-muted-foreground">
            Configure backend API endpoints for compliance analysis.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            {/* 🔧 BACKEND_URL TO BE CONFIGURED HERE */}
            <Label htmlFor="api-url" className="text-sm text-foreground">
              Compliance API Base URL
            </Label>
            <Input
              id="api-url"
              value={process.env.NEXT_PUBLIC_COMPLIANCE_API_URL || "http://127.0.0.1:8003"}
              readOnly
              className="bg-secondary/50 font-mono text-sm text-foreground"
            />
            <p className="text-xs text-muted-foreground">
              Set via <code className="font-mono text-primary">NEXT_PUBLIC_COMPLIANCE_API_URL</code>{" "}
              environment variable.
            </p>
          </div>

          <Separator className="bg-border" />

          <div className="flex flex-col gap-3">
            <Label className="text-sm text-foreground">API Endpoints</Label>
            <div className="flex flex-col gap-2">
              {[
                { method: "GET", path: "/compliance/{document_id}", desc: "Get compliance result for a document" },
                { method: "GET", path: "/decisions", desc: "List all compliance decisions" },
                { method: "GET", path: "/health", desc: "API health check" },
              ].map((endpoint) => (
                <div
                  key={endpoint.path}
                  className="flex items-center gap-3 rounded-lg bg-secondary/30 px-3 py-2"
                >
                  <Badge
                    variant="outline"
                    className="border-success/20 bg-success/5 text-success font-mono text-xs shrink-0"
                  >
                    {endpoint.method}
                  </Badge>
                  <span className="font-mono text-xs text-foreground">{endpoint.path}</span>
                  <span className="hidden text-xs text-muted-foreground sm:inline">
                    - {endpoint.desc}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-foreground">
            <Shield className="h-4 w-4 text-primary" />
            Security Configuration
          </CardTitle>
          <CardDescription className="text-muted-foreground">
            Authentication and session management settings.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3">
            {[
              { label: "Authentication", value: "Session-based (Cookie)", status: "Active" },
              { label: "Session Duration", value: "24 hours", status: "Default" },
              { label: "Role Enforcement", value: "Middleware + API", status: "Active" },
              { label: "Cookie Security", value: "HttpOnly, SameSite", status: "Active" },
            ].map((item) => (
              <div
                key={item.label}
                className="flex items-center justify-between rounded-lg bg-secondary/30 px-3 py-2"
              >
                <div>
                  <p className="text-sm text-foreground">{item.label}</p>
                  <p className="text-xs text-muted-foreground">{item.value}</p>
                </div>
                <Badge
                  className={
                    item.status === "Active"
                      ? "bg-success/10 text-success border-success/20"
                      : "bg-muted text-muted-foreground"
                  }
                >
                  {item.status}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* System Info */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-foreground">
            <Database className="h-4 w-4 text-primary" />
            System Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {[
              { label: "Platform", value: "SatyamAI v1.0" },
              { label: "Framework", value: "Next.js 16 (App Router)" },
              { label: "Auth Provider", value: "Built-in (SSO-ready)" },
              { label: "Environment", value: process.env.NODE_ENV || "development" },
            ].map((item) => (
              <div key={item.label} className="rounded-lg bg-secondary/30 px-3 py-2">
                <dt className="text-xs text-muted-foreground">{item.label}</dt>
                <dd className="text-sm font-medium text-foreground">{item.value}</dd>
              </div>
            ))}
          </dl>
        </CardContent>
      </Card>

      <p className="text-xs text-muted-foreground/60 text-center">
        Auth logic: <code className="font-mono">lib/auth.ts</code> | Role config:{" "}
        <code className="font-mono">lib/auth.ts ROUTE_ACCESS</code> | AI display:{" "}
        <code className="font-mono">components/ai-explanation-card.tsx</code>
      </p>
    </div>
  );
}
