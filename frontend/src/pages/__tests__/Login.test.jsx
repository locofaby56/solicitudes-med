import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { iniciarSesion } from "../../api/client";
import Login from "../Login";

vi.mock("../../api/client", () => ({
  iniciarSesion: vi.fn(),
}));

function renderLogin() {
  const consultas = new QueryClient({
    defaultOptions: { mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={consultas}>
      <Login />
    </QueryClientProvider>,
  );
}

describe("Login", () => {
  it("envía las credenciales", async () => {
    iniciarSesion.mockResolvedValue({ token: "token-prueba" });
    const usuario = userEvent.setup();
    renderLogin();

    await usuario.type(screen.getByLabelText("Correo"), "ana@ejemplo.com");
    await usuario.type(screen.getByLabelText("Contraseña"), "clave-segura");
    await usuario.click(screen.getByRole("button", { name: "Entrar" }));

    await waitFor(() => {
      expect(iniciarSesion).toHaveBeenCalledWith("ana@ejemplo.com", "clave-segura");
    });
  });
});
