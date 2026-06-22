"use client";

import * as React from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  api,
  type AgriculturalEvent,
  type CropCycleDetail,
  type EventType,
} from "@/lib/api";
import {
  EVENT_TYPES,
  EVENT_TYPE_LABELS,
  eventStyle,
} from "@/lib/events";
import { useFarmContext } from "@/lib/context";
import { PageHeader } from "@/components/page-header";
import { ErrorBlock, LoadingBlock, Spinner } from "@/components/states";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { formatNumber, formatDateBR, formatBRL } from "@/lib/utils";

function SummaryRow({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs uppercase tracking-wide text-muted-foreground">
        {label}
      </span>
      <span className="text-sm font-medium text-foreground">{value}</span>
    </div>
  );
}

function HubRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium tabular-nums">{value}</span>
    </div>
  );
}

export default function SafraPage() {
  const qc = useQueryClient();
  const ctx = useFarmContext();
  // Safra vem do contexto global (header) — sem digitar ID.
  const cycleId = ctx.cropCycleId;

  const cycleQuery = useQuery<CropCycleDetail>({
    queryKey: ["crop-cycle", cycleId],
    queryFn: () => api.getCropCycle(cycleId as number),
    enabled: cycleId !== null,
  });

  const eventsQuery = useQuery<AgriculturalEvent[]>({
    queryKey: ["crop-cycle-events", cycleId],
    queryFn: () => api.getCropCycleEvents(cycleId as number),
    enabled: cycleId !== null,
  });

  // ---- hub "Minha Lavoura": plano, custos e atenção numa só página ----
  const planQuery = useQuery({
    queryKey: ["plan-vs-actual", cycleId],
    queryFn: () => api.getPlanVsActual(cycleId as number),
    enabled: cycleId !== null,
  });
  const costQuery = useQuery({
    queryKey: ["crop-cycle-cost", cycleId],
    queryFn: () => api.getCropCycleCost(cycleId as number),
    enabled: cycleId !== null,
  });
  const decisionsQuery = useQuery({
    queryKey: ["decisions", ctx.farmId],
    queryFn: () => api.getDecisions(ctx.farmId as number),
    enabled: ctx.farmId !== null,
  });
  const fieldAttention = decisionsQuery.data?.fields.find(
    (f) => f.field_id === cycleQuery.data?.field_id
  );

  // ---- edit form state, seeded from the loaded cycle ----
  const [edit, setEdit] = React.useState({
    area_ha: "",
    cultivar: "",
    actual_planting_date: "",
    harvest_date: "",
    actual_yield_sc_ha: "",
    notes: "",
  });

  React.useEffect(() => {
    const c = cycleQuery.data;
    if (!c) return;
    setEdit({
      area_ha: c.area_ha != null ? String(c.area_ha) : "",
      cultivar: c.cultivar ?? "",
      actual_planting_date: c.actual_planting_date ?? "",
      harvest_date: c.harvest_date ?? "",
      actual_yield_sc_ha:
        c.actual_yield_sc_ha != null ? String(c.actual_yield_sc_ha) : "",
      notes: c.notes ?? "",
    });
  }, [cycleQuery.data]);

  const updateCycle = useMutation({
    mutationFn: () =>
      api.updateCropCycle(cycleId as number, {
        area_ha: edit.area_ha !== "" ? Number(edit.area_ha) : undefined,
        cultivar: edit.cultivar || undefined,
        actual_planting_date: edit.actual_planting_date || undefined,
        harvest_date: edit.harvest_date || undefined,
        actual_yield_sc_ha:
          edit.actual_yield_sc_ha !== ""
            ? Number(edit.actual_yield_sc_ha)
            : undefined,
        notes: edit.notes || undefined,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["crop-cycle", cycleId] });
    },
  });

  // ---- add-event form state ----
  const [ev, setEv] = React.useState({
    event_type: "PLANTING" as EventType,
    event_date: "",
    product_name: "",
    quantity: "",
    unit: "",
    cost: "",
    notes: "",
  });

  const createEvent = useMutation({
    mutationFn: () =>
      api.createCropCycleEvent(cycleId as number, {
        event_type: ev.event_type,
        event_date: ev.event_date,
        product_name: ev.product_name || undefined,
        quantity: ev.quantity !== "" ? Number(ev.quantity) : undefined,
        unit: ev.unit || undefined,
        cost: ev.cost !== "" ? Number(ev.cost) : undefined,
        notes: ev.notes || undefined,
      }),
    onSuccess: () => {
      setEv({
        event_type: "PLANTING",
        event_date: "",
        product_name: "",
        quantity: "",
        unit: "",
        cost: "",
        notes: "",
      });
      qc.invalidateQueries({ queryKey: ["crop-cycle-events", cycleId] });
    },
  });

  const sortedEvents = React.useMemo(() => {
    if (!eventsQuery.data) return [];
    return [...eventsQuery.data].sort((a, b) =>
      a.event_date.localeCompare(b.event_date)
    );
  }, [eventsQuery.data]);

  return (
    <div>
      <PageHeader
        title="Minha Lavoura"
        description="Tudo sobre a safra selecionada numa página: resumo, plano e orçamento, custos, atenção e a linha do tempo das operações."
      />

      {cycleId === null ? (
        <p className="text-sm text-muted-foreground">
          Selecione a <span className="font-medium">Fazenda · Safra</span> no topo da
          página para acompanhar a lavoura. Se ainda não tem dados, comece pela página{" "}
          <span className="font-medium">Início</span>.
        </p>
      ) : (
        <div className="space-y-6">
          {/* SUMMARY */}
          <Card>
            <CardHeader>
              <CardTitle>Resumo da safra</CardTitle>
            </CardHeader>
            <CardContent>
              {cycleQuery.isLoading && (
                <LoadingBlock label="Carregando ciclo..." />
              )}
              {cycleQuery.isError && <ErrorBlock error={cycleQuery.error} />}
              {cycleQuery.data && (
                <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
                  <SummaryRow label="Cultura" value={cycleQuery.data.crop} />
                  <SummaryRow label="Safra" value={cycleQuery.data.season} />
                  <SummaryRow
                    label="Ano de colheita"
                    value={cycleQuery.data.harvest_year}
                  />
                  <SummaryRow
                    label="Área (ha)"
                    value={
                      cycleQuery.data.area_ha != null
                        ? formatNumber(cycleQuery.data.area_ha)
                        : "—"
                    }
                  />
                  <SummaryRow
                    label="Cultivar"
                    value={cycleQuery.data.cultivar ?? "—"}
                  />
                  <SummaryRow
                    label="Plantio planejado"
                    value={formatDateBR(cycleQuery.data.planned_planting_date)}
                  />
                  <SummaryRow
                    label="Plantio real"
                    value={formatDateBR(cycleQuery.data.actual_planting_date)}
                  />
                  <SummaryRow
                    label="Colheita"
                    value={formatDateBR(cycleQuery.data.harvest_date)}
                  />
                  <SummaryRow
                    label="Prod. real (sc/ha)"
                    value={
                      cycleQuery.data.actual_yield_sc_ha != null
                        ? formatNumber(cycleQuery.data.actual_yield_sc_ha)
                        : "—"
                    }
                  />
                  <div className="col-span-2 md:col-span-3">
                    <SummaryRow
                      label="Observações"
                      value={cycleQuery.data.notes ?? "—"}
                    />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* HUB: plano, custos e atenção desta safra numa só página */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Plano & Orçamento</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1 text-sm">
                {planQuery.data && planQuery.data.planned_total_cost > 0 ? (
                  <>
                    <HubRow label="Gasto" value={formatBRL(planQuery.data.actual_total_cost)} />
                    <HubRow label="Planejado" value={formatBRL(planQuery.data.planned_total_cost)} />
                    <HubRow label="Falta investir" value={formatBRL(planQuery.data.remaining_budget)} />
                    <HubRow
                      label="Aplicações"
                      value={`${planQuery.data.actual_applications}/${planQuery.data.planned_applications}`}
                    />
                    <Link href="/planejamento" className="mt-2 inline-block text-xs text-brand-700 underline">
                      Ver plano completo →
                    </Link>
                  </>
                ) : (
                  <p className="text-xs text-muted-foreground">
                    Sem plano. Defina operações em <span className="font-medium">Planejar</span>.
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Custos</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1 text-sm">
                {costQuery.data ? (
                  <>
                    <HubRow label="Total" value={formatBRL(costQuery.data.total_cost)} />
                    <HubRow label="Por hectare" value={formatBRL(costQuery.data.cost_per_hectare)} />
                    <HubRow
                      label="Por saca"
                      value={
                        costQuery.data.cost_per_bag != null
                          ? formatBRL(costQuery.data.cost_per_bag)
                          : "—"
                      }
                    />
                    <HubRow label="Aplicações" value={`${costQuery.data.n_applications}`} />
                    <Link href="/financeiro" className="mt-2 inline-block text-xs text-brand-700 underline">
                      Lucro e cenários →
                    </Link>
                  </>
                ) : (
                  <p className="text-xs text-muted-foreground">Sem custos registrados.</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Atenção</CardTitle>
              </CardHeader>
              <CardContent className="text-sm">
                {!fieldAttention ? (
                  <p className="text-xs text-muted-foreground">
                    Selecione a fazenda para ver alertas.
                  </p>
                ) : fieldAttention.attention_level === "saudável" ? (
                  <p className="text-muted-foreground">Sem alertas neste talhão.</p>
                ) : (
                  <div className="space-y-2">
                    <Badge
                      variant={fieldAttention.attention_level === "alta" ? "danger" : "warning"}
                    >
                      atenção {fieldAttention.attention_level}
                    </Badge>
                    <ul className="list-inside list-disc text-muted-foreground">
                      {fieldAttention.flags.map((fl, i) => (
                        <li key={i}>{fl.title}</li>
                      ))}
                    </ul>
                    <Link href="/decisoes" className="inline-block text-xs text-brand-700 underline">
                      Detalhes →
                    </Link>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* EDIT / PATCH */}
          {cycleQuery.data && (
            <Card>
              <CardHeader>
                <CardTitle>Atualizar safra</CardTitle>
              </CardHeader>
              <CardContent>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    updateCycle.mutate();
                  }}
                  className="grid grid-cols-1 gap-4 md:grid-cols-2"
                >
                  <div className="space-y-2">
                    <Label htmlFor="editArea">Área (ha)</Label>
                    <Input
                      id="editArea"
                      type="number"
                      min="0"
                      step="0.1"
                      value={edit.area_ha}
                      onChange={(e) =>
                        setEdit((s) => ({ ...s, area_ha: e.target.value }))
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="editCultivar">Cultivar</Label>
                    <Input
                      id="editCultivar"
                      value={edit.cultivar}
                      onChange={(e) =>
                        setEdit((s) => ({ ...s, cultivar: e.target.value }))
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="editPlanting">Data de plantio real</Label>
                    <Input
                      id="editPlanting"
                      type="date"
                      value={edit.actual_planting_date}
                      onChange={(e) =>
                        setEdit((s) => ({
                          ...s,
                          actual_planting_date: e.target.value,
                        }))
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="editHarvest">Data de colheita</Label>
                    <Input
                      id="editHarvest"
                      type="date"
                      value={edit.harvest_date}
                      onChange={(e) =>
                        setEdit((s) => ({ ...s, harvest_date: e.target.value }))
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="editYield">Produtividade real (sc/ha)</Label>
                    <Input
                      id="editYield"
                      type="number"
                      min="0"
                      step="0.1"
                      value={edit.actual_yield_sc_ha}
                      onChange={(e) =>
                        setEdit((s) => ({
                          ...s,
                          actual_yield_sc_ha: e.target.value,
                        }))
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="editNotes">Observações</Label>
                    <Input
                      id="editNotes"
                      value={edit.notes}
                      onChange={(e) =>
                        setEdit((s) => ({ ...s, notes: e.target.value }))
                      }
                    />
                  </div>
                  <div className="md:col-span-2 flex items-center gap-3">
                    <Button type="submit" disabled={updateCycle.isPending}>
                      {updateCycle.isPending && <Spinner />}
                      Salvar alterações
                    </Button>
                    {updateCycle.isSuccess && !updateCycle.isPending && (
                      <span className="text-sm text-brand-700">
                        Atualizado.
                      </span>
                    )}
                  </div>
                </form>
                {updateCycle.isError && (
                  <div className="mt-4">
                    <ErrorBlock error={updateCycle.error} />
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* TIMELINE */}
          <Card>
            <CardHeader>
              <CardTitle>Linha do tempo de eventos</CardTitle>
            </CardHeader>
            <CardContent>
              {eventsQuery.isLoading && (
                <LoadingBlock label="Carregando eventos..." />
              )}
              {eventsQuery.isError && <ErrorBlock error={eventsQuery.error} />}
              {eventsQuery.data && sortedEvents.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  Nenhum evento registrado ainda.
                </p>
              )}
              {sortedEvents.length > 0 && (
                <ol className="relative ml-3 border-l border-border">
                  {sortedEvents.map((e) => {
                    const style = eventStyle(e.event_type);
                    return (
                      <li key={e.id} className="mb-6 ml-6 last:mb-0">
                        <span
                          className={
                            "absolute -left-[7px] mt-1.5 h-3.5 w-3.5 rounded-full ring-4 " +
                            style.dot
                          }
                          aria-hidden
                        />
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge className={style.badge}>
                            {EVENT_TYPE_LABELS[e.event_type]}
                          </Badge>
                          <span className="text-sm font-medium text-foreground">
                            {formatDateBR(e.event_date)}
                          </span>
                          {e.cost != null && (
                            <span className="text-sm font-medium tabular-nums text-brand-700">
                              {formatBRL(e.cost)}
                            </span>
                          )}
                        </div>
                        <div className="mt-1 text-sm text-muted-foreground">
                          {e.product_name && (
                            <span className="text-foreground">
                              {e.product_name}
                            </span>
                          )}
                          {e.quantity != null && (
                            <span>
                              {e.product_name ? " · " : ""}
                              {formatNumber(e.quantity)}
                              {e.unit ? ` ${e.unit}` : ""}
                            </span>
                          )}
                          {e.notes && (
                            <span className="block italic">{e.notes}</span>
                          )}
                        </div>
                      </li>
                    );
                  })}
                </ol>
              )}
            </CardContent>
          </Card>

          {/* ADD EVENT */}
          <Card>
            <CardHeader>
              <CardTitle>Registrar evento</CardTitle>
            </CardHeader>
            <CardContent>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (!ev.event_date) return;
                  createEvent.mutate();
                }}
                className="grid grid-cols-1 gap-4 md:grid-cols-2"
              >
                <div className="space-y-2">
                  <Label htmlFor="evType">Tipo de evento</Label>
                  <Select
                    id="evType"
                    value={ev.event_type}
                    onChange={(e) =>
                      setEv((s) => ({
                        ...s,
                        event_type: e.target.value as EventType,
                      }))
                    }
                  >
                    {EVENT_TYPES.map((t) => (
                      <option key={t} value={t}>
                        {EVENT_TYPE_LABELS[t]}
                      </option>
                    ))}
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="evDate">Data do evento</Label>
                  <Input
                    id="evDate"
                    type="date"
                    value={ev.event_date}
                    onChange={(e) =>
                      setEv((s) => ({ ...s, event_date: e.target.value }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="evProduct">Produto</Label>
                  <Input
                    id="evProduct"
                    value={ev.product_name}
                    onChange={(e) =>
                      setEv((s) => ({ ...s, product_name: e.target.value }))
                    }
                    placeholder="Opcional"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="evQty">Quantidade</Label>
                    <Input
                      id="evQty"
                      type="number"
                      min="0"
                      step="0.01"
                      value={ev.quantity}
                      onChange={(e) =>
                        setEv((s) => ({ ...s, quantity: e.target.value }))
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="evUnit">Unidade</Label>
                    <Input
                      id="evUnit"
                      value={ev.unit}
                      onChange={(e) =>
                        setEv((s) => ({ ...s, unit: e.target.value }))
                      }
                      placeholder="kg/ha, L/ha..."
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="evCost">Custo (R$)</Label>
                  <Input
                    id="evCost"
                    type="number"
                    min="0"
                    step="0.01"
                    value={ev.cost}
                    onChange={(e) =>
                      setEv((s) => ({ ...s, cost: e.target.value }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="evNotes">Observações</Label>
                  <Input
                    id="evNotes"
                    value={ev.notes}
                    onChange={(e) =>
                      setEv((s) => ({ ...s, notes: e.target.value }))
                    }
                    placeholder="Opcional"
                  />
                </div>
                <div className="md:col-span-2">
                  <Button
                    type="submit"
                    disabled={!ev.event_date || createEvent.isPending}
                  >
                    {createEvent.isPending && <Spinner />}
                    Adicionar evento
                  </Button>
                </div>
              </form>
              {createEvent.isError && (
                <div className="mt-4">
                  <ErrorBlock error={createEvent.error} />
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
