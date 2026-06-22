"use client";

import * as React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useFarmContext } from "@/lib/context";
import { Select } from "@/components/ui/select";

/** Seletor global Fazenda · Safra (header). Selecione uma vez; persiste. */
export function ContextBar() {
  const ctx = useFarmContext();
  const farmsQuery = useQuery({ queryKey: ["farms"], queryFn: api.getFarms });
  const cyclesQuery = useQuery({
    queryKey: ["farm-cycles", ctx.farmId],
    queryFn: () => api.getFarmCropCycles(ctx.farmId as number),
    enabled: ctx.farmId !== null,
  });

  const farms = farmsQuery.data;
  const cycles = cyclesQuery.data;

  // Auto-seleciona a primeira fazenda/safra para o contexto nunca ficar vazio.
  React.useEffect(() => {
    if (ctx.ready && ctx.farmId === null && farms && farms.length > 0) {
      ctx.setFarm(farms[0]);
    }
  }, [ctx, farms]);

  React.useEffect(() => {
    if (ctx.farmId !== null && ctx.cropCycleId === null && cycles && cycles.length > 0) {
      ctx.setCropCycle(cycles[0]);
    }
  }, [ctx, cycles]);

  if (!ctx.ready) return null;

  if (farms && farms.length === 0) {
    return (
      <div className="border-b border-border bg-card px-5 py-2 text-sm text-muted-foreground md:px-10">
        Nenhuma fazenda ainda —{" "}
        <Link href="/home" className="text-brand-700 underline">
          comece aqui
        </Link>
        .
      </div>
    );
  }

  return (
    <div className="sticky top-0 z-10 flex flex-wrap items-center gap-3 border-b border-border bg-card/95 px-5 py-2 backdrop-blur md:px-10">
      <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        Contexto
      </span>
      <Select
        aria-label="Fazenda"
        className="h-8 w-auto min-w-[10rem] text-sm"
        value={ctx.farmId ?? ""}
        onChange={(e) => {
          const f = farms?.find((x) => x.id === Number(e.target.value)) ?? null;
          ctx.setFarm(f);
        }}
      >
        {!ctx.farmId && <option value="">Selecione a fazenda…</option>}
        {farms?.map((f) => (
          <option key={f.id} value={f.id}>
            {f.name}
          </option>
        ))}
      </Select>

      {ctx.farmId !== null && (
        <Select
          aria-label="Safra"
          className="h-8 w-auto min-w-[12rem] text-sm"
          value={ctx.cropCycleId ?? ""}
          onChange={(e) => {
            const c = cycles?.find((x) => x.id === Number(e.target.value)) ?? null;
            ctx.setCropCycle(c);
          }}
          disabled={cyclesQuery.isLoading}
        >
          {(!cycles || cycles.length === 0) && (
            <option value="">{cyclesQuery.isLoading ? "Carregando…" : "Sem safras"}</option>
          )}
          {cycles?.map((c) => (
            <option key={c.id} value={c.id}>
              {c.field_name} · {c.season}
            </option>
          ))}
        </Select>
      )}
    </div>
  );
}
