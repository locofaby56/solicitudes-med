import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import Login from "./pages/Login";
import Register from "./pages/Register";
import SolicitudForm from "./pages/SolicitudForm";
import SolicitudesList from "./pages/SolicitudesList";

export default function App() {
  const consultas = useQueryClient();
  const [token, setToken] = useState(null);
  const [vista, setVista] = useState("login");
  const [aviso, setAviso] = useState("");

  function salir() {
    setToken(null);
    setVista("login");
    setAviso("");
    consultas.clear();
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-lg flex-col gap-6 bg-slate-50 px-4 py-10 text-slate-900">
      <header>
        <h1 className="text-2xl font-semibold">Solicitudes de medicamentos</h1>
        <p className="mt-1 text-sm text-slate-600">Pide un medicamento del catálogo.</p>
      </header>
      {!token && aviso && <p role="status">{aviso}</p>}
      {!token && vista === "registro" && (
        <Register
          alCrear={() => {
            setAviso("Cuenta creada. Ya puedes entrar.");
            setVista("login");
          }}
          volver={() => setVista("login")}
        />
      )}
      {!token && vista === "login" && (
        <Login
          alEntrar={(datos) => {
            setAviso("");
            setToken(datos.token);
          }}
          irARegistro={() => {
            setAviso("");
            setVista("registro");
          }}
        />
      )}
      {token && (
        <>
          <SolicitudForm token={token} />
          <SolicitudesList token={token} />
          <button type="button" className="self-start text-sm text-slate-600 underline" onClick={salir}>
            Salir
          </button>
        </>
      )}
    </main>
  );
}
