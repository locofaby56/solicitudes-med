import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { listarMedicamentos, listarSolicitudes } from "../../api/client";
import SolicitudesList from "../SolicitudesList";

vi.mock("../../api/client", () => ({
  listarSolicitudes: vi.fn(),
  listarMedicamentos: vi.fn(),
}));

function renderListado() {
  const consultas = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={consultas}>
      <SolicitudesList token="token-prueba" porPagina={2} />
    </QueryClientProvider>,
  );
}

describe("SolicitudesList", () => {
  it("pasa a la página siguiente", async () => {
    listarMedicamentos.mockResolvedValue([
      { id: 1, nombre: "Acetaminofén", es_no_pos: false },
      { id: 4, nombre: "Medicamento especial", es_no_pos: true },
    ]);
    listarSolicitudes.mockImplementation(async (_token, pagina) => {
      if (pagina === 1) {
        return {
          solicitudes: [
            { id: 1, medicamento_id: 1, numero_orden: null },
            { id: 2, medicamento_id: 1, numero_orden: null },
          ],
          pagina: 1,
          por_pagina: 2,
          total: 3,
        };
      }
      return {
        solicitudes: [
          {
            id: 3,
            usuario_id: 9,
            medicamento_id: 4,
            numero_orden: "ORD-3",
            direccion: "Cra 10",
            telefono: "3001234567",
            correo: "entrega@ejemplo.com",
            creado_en: "2026-09-24 10:00:00",
          },
        ],
        pagina: 2,
        por_pagina: 2,
        total: 3,
      };
    });
    const usuario = userEvent.setup();
    renderListado();

    expect(await screen.findByText("Solicitud 1")).toBeInTheDocument();
    expect(screen.getByText("Solicitud 2")).toBeInTheDocument();
    expect(await screen.findAllByText("Acetaminofén")).toHaveLength(2);
    expect(screen.getAllByText("POS")).toHaveLength(2);
    expect(screen.queryByText("Número de orden")).not.toBeInTheDocument();
    expect(screen.getByText("Página 1 de 2")).toBeInTheDocument();
    expect(listarSolicitudes).toHaveBeenCalledWith("token-prueba", 1, 2);

    await usuario.click(screen.getByRole("button", { name: "Siguiente" }));

    await waitFor(() => {
      expect(listarSolicitudes).toHaveBeenCalledWith("token-prueba", 2, 2);
    });
    expect(await screen.findByText("Solicitud 3")).toBeInTheDocument();
    expect(screen.getByText("NO POS")).toBeInTheDocument();
    expect(screen.getByText("Medicamento especial")).toBeInTheDocument();
    expect(screen.getByText("ORD-3")).toBeInTheDocument();
    expect(screen.getByText("Cra 10")).toBeInTheDocument();
    expect(screen.getByText("3001234567")).toBeInTheDocument();
    expect(screen.getByText("entrega@ejemplo.com")).toBeInTheDocument();
    expect(screen.queryByText("2026-09-24 10:00:00")).not.toBeInTheDocument();
    expect(screen.queryByText("Solicitud 1")).not.toBeInTheDocument();
    expect(screen.getByText("Página 2 de 2")).toBeInTheDocument();
  });
});
