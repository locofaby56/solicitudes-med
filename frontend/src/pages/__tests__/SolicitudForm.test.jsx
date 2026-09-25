import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import SolicitudForm from "../SolicitudForm";

const MEDICAMENTOS = [
  { id: 1, nombre: "Acetaminofén", es_no_pos: false },
  { id: 2, nombre: "Medicamento especial", es_no_pos: true },
];

function renderFormulario() {
  const consultas = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={consultas}>
      <SolicitudForm medicamentos={MEDICAMENTOS} />
    </QueryClientProvider>,
  );
}

describe("SolicitudForm", () => {
  it("muestra los campos extra solo si es_no_pos es true", async () => {
    const usuario = userEvent.setup();
    renderFormulario();

    expect(screen.queryByLabelText("Número de orden")).not.toBeInTheDocument();

    await usuario.selectOptions(screen.getByLabelText("Medicamento"), "1");
    expect(screen.queryByLabelText("Número de orden")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Dirección")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Teléfono")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Correo")).not.toBeInTheDocument();

    await usuario.selectOptions(screen.getByLabelText("Medicamento"), "2");
    expect(screen.getByLabelText("Número de orden")).toBeInTheDocument();
    expect(screen.getByLabelText("Dirección")).toBeInTheDocument();
    expect(screen.getByLabelText("Teléfono")).toBeInTheDocument();
    expect(screen.getByLabelText("Correo")).toBeInTheDocument();

    await usuario.selectOptions(screen.getByLabelText("Medicamento"), "1");
    expect(screen.queryByLabelText("Número de orden")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Correo")).not.toBeInTheDocument();
  });
});
