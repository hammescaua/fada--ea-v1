"use client";

import { useQuery } from "@tanstack/react-query";
import { api, type SystemStatus } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { ErrorBlock, LoadingBlock } from "@/components/states";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge, type BadgeProps } from "@/components/ui/badge";
import { Stat } from "@/components/stat";

function statusVariant(status: string): BadgeProps["variant"] {
  if (status === "ok") return "success";
  if (status === "degraded") return "warning";
  return "danger";
}

const COUNT_LABELS: Record<string, string> = {
  farms: "Fazendas",
  fields: "Talhões",
  crop_cycles: "Safras",
  events: "Operações",
};

export default function SystemPage() {
  const query = useQuery<SystemStatus>({
    queryKey: ["system-status"],
    queryFn: api.getSystemStatus,
    refetchInterval: 30_000,
    retry: false,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Sistema"
        description="Status da plataforma: backend, banco, modelo e registros."
      />

      {query.isLoading ? (
        <LoadingBlock label="Consultando status…" />
      ) : query.isError ? (
        <ErrorBlock error={query.error} />
      ) : query.data ? (
        <>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <CardTitle>Estado geral</CardTitle>
              <Badge variant={statusVariant(query.data.status)}>
                {query.data.status}
              </Badge>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Versão</span>
                <span className="font-medium tabular-nums">{query.data.version}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">
                  Banco de dados ({query.data.database.url_scheme})
                </span>
                <Badge variant={statusVariant(query.data.database.status)}>
                  {query.data.database.status}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">
                  Modelo ({query.data.model.path})
                </span>
                <Badge variant={statusVariant(query.data.model.status)}>
                  {query.data.model.status}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Relatório de calibração</span>
                <Badge
                  variant={
                    query.data.calibration_report.present ? "success" : "secondary"
                  }
                >
                  {query.data.calibration_report.present ? "presente" : "ausente"}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(query.data.counts).map(([key, value]) => (
              <Stat key={key} label={COUNT_LABELS[key] ?? key} value={`${value}`} />
            ))}
          </div>
        </>
      ) : null}
    </div>
  );
}
