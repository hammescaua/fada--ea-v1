"use client";

import * as React from "react";
import type { CropCycleListItem, Farm } from "@/lib/api";

/**
 * Contexto global Fazenda · Safra: selecionado uma vez, persiste entre páginas e
 * recarregamentos (localStorage). Elimina re-seleção e digitação de IDs.
 */
type FarmContextValue = {
  farmId: number | null;
  farmName: string | null;
  municipalityCode: number | null;
  cropCycleId: number | null;
  cropCycleLabel: string | null;
  season: string | null;
  ready: boolean; // true após carregar do localStorage (evita flicker)
  setFarm: (farm: Farm | null) => void;
  setCropCycle: (cycle: CropCycleListItem | null) => void;
};

type Persisted = Pick<
  FarmContextValue,
  | "farmId"
  | "farmName"
  | "municipalityCode"
  | "cropCycleId"
  | "cropCycleLabel"
  | "season"
>;

const EMPTY: Persisted = {
  farmId: null,
  farmName: null,
  municipalityCode: null,
  cropCycleId: null,
  cropCycleLabel: null,
  season: null,
};

const STORAGE_KEY = "fada.ctx";
const FarmContext = React.createContext<FarmContextValue | null>(null);

export function FarmContextProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = React.useState<Persisted>(EMPTY);
  const [ready, setReady] = React.useState(false);

  React.useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setState({ ...EMPTY, ...JSON.parse(raw) });
    } catch {
      // ignora localStorage indisponível/corrompido
    }
    setReady(true);
  }, []);

  React.useEffect(() => {
    if (ready) localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state, ready]);

  const setFarm = React.useCallback((farm: Farm | null) => {
    setState(
      farm
        ? {
            ...EMPTY,
            farmId: farm.id,
            farmName: farm.name,
            municipalityCode: farm.municipality_code,
          }
        : EMPTY
    );
  }, []);

  const setCropCycle = React.useCallback((cycle: CropCycleListItem | null) => {
    setState((s) => ({
      ...s,
      cropCycleId: cycle?.id ?? null,
      cropCycleLabel: cycle ? `${cycle.field_name} · ${cycle.season}` : null,
      season: cycle?.season ?? null,
    }));
  }, []);

  return (
    <FarmContext.Provider value={{ ...state, ready, setFarm, setCropCycle }}>
      {children}
    </FarmContext.Provider>
  );
}

export function useFarmContext(): FarmContextValue {
  const ctx = React.useContext(FarmContext);
  if (!ctx) throw new Error("useFarmContext deve ser usado dentro de FarmContextProvider");
  return ctx;
}
