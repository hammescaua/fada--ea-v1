"use client";

import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="mx-auto max-w-md py-16 text-center">
      <h2 className="text-lg font-semibold">Algo deu errado nesta página</h2>
      <p className="mt-2 text-sm text-muted-foreground">
        Um erro inesperado ocorreu. As demais páginas continuam funcionando.
      </p>
      <p className="mt-2 break-words text-xs text-muted-foreground">{error.message}</p>
      <Button className="mt-6" onClick={() => reset()}>
        Tentar novamente
      </Button>
    </div>
  );
}
