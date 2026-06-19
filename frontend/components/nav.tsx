"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const links = [
  { href: "/home", label: "Início" },
  { href: "/", label: "Inteligência Regional" },
  { href: "/planting/simulate", label: "Simular Data de Plantio" },
  { href: "/planting/optimize", label: "Otimizar Janela" },
  { href: "/farms", label: "Captura de Dados" },
  { href: "/safra", label: "Safra" },
  { href: "/planejamento", label: "Plano & Orçamento" },
  { href: "/financeiro", label: "Financeiro" },
  { href: "/insights", label: "Inteligência por Talhão" },
  { href: "/decisoes", label: "Decisões" },
  { href: "/adaptive", label: "Inteligência Adaptativa" },
  { href: "/calibration", label: "Calibração" },
  { href: "/assistant", label: "Assistente" },
  { href: "/system", label: "Sistema" },
];

// Destinos primários do dia a dia (bottom nav mobile).
const primary = [
  { href: "/home", label: "Início" },
  { href: "/planejamento", label: "Plano" },
  { href: "/decisoes", label: "Decisões" },
  { href: "/insights", label: "Talhões" },
  { href: "/assistant", label: "Assistente" },
];

function isActive(pathname: string, href: string): boolean {
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}

/** Sidebar — desktop. */
export function Nav() {
  const pathname = usePathname();
  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-border bg-card md:flex md:h-screen">
      <div className="flex items-center gap-2 px-6 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-brand-600 text-white font-bold">
          F
        </div>
        <div className="leading-tight">
          <div className="text-base font-semibold">FADA</div>
          <div className="text-xs text-muted-foreground">Farm AI Decision Agent</div>
        </div>
      </div>
      <nav className="flex flex-col gap-1 overflow-y-auto px-3 pb-4">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={cn(
              "rounded-md px-3 py-2 text-sm font-medium transition-colors",
              isActive(pathname, link.href)
                ? "bg-brand-50 text-brand-700"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}

/** Bottom nav — mobile (5 destinos primários). */
export function BottomNav() {
  const pathname = usePathname();
  return (
    <nav className="fixed inset-x-0 bottom-0 z-20 grid grid-cols-5 border-t border-border bg-card md:hidden">
      {primary.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className={cn(
            "flex flex-col items-center gap-0.5 py-2 text-[11px] font-medium",
            isActive(pathname, link.href)
              ? "text-brand-700"
              : "text-muted-foreground"
          )}
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
