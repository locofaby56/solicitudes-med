import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { listarMedicamentos, listarSolicitudes } from "../api/client";
import Icon from "../components/Icon";

const CAMPOS_ENTREGA = [
  ["numero_orden", "Número de orden"],
  ["direccion", "Dirección"],
  ["telefono", "Teléfono"],
  ["correo", "Correo"],
];

function medicamentoDe(solicitud, medicamentos) {
  return medicamentos.find((item) => item.id === solicitud.medicamento_id);
}

function esNoPos(solicitud, medicamentos) {
  const medicamento = medicamentoDe(solicitud, medicamentos);
  if (medicamento) {
    return Boolean(medicamento.es_no_pos);
  }
  return Boolean(solicitud.numero_orden);
}

export default function SolicitudesList({ token, porPagina = 10 }) {
  const [pagina, setPagina] = useState(1);
  const consulta = useQuery({
    queryKey: ["solicitudes", token, pagina, porPagina],
    queryFn: () => listarSolicitudes(token, pagina, porPagina),
    enabled: Boolean(token),
    placeholderData: keepPreviousData,
  });
  const catalogo = useQuery({
    queryKey: ["medicamentos", token],
    queryFn: () => listarMedicamentos(token),
    enabled: Boolean(token),
  });
  const medicamentos = catalogo.data ?? [];
  const total = consulta.data?.total ?? 0;
  const paginas = Math.max(1, Math.ceil(total / porPagina) || 1);
  const solicitudes = consulta.data?.solicitudes ?? [];

  return (
    <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="flex items-center gap-2 text-lg font-semibold">
        <Icon nombre="lista" size={20} />
        Tus solicitudes
      </h2>
      {consulta.isPending && <p>Cargando solicitudes.</p>}
      {consulta.isError && (
        <p className="text-sm text-red-700" role="alert">
          {consulta.error.message}
        </p>
      )}
      {consulta.isSuccess && solicitudes.length === 0 && <p>Todavía no tienes solicitudes.</p>}
      <ul className="space-y-2">
        {solicitudes.map((solicitud) => {
          const noPos = esNoPos(solicitud, medicamentos);
          const medicamento = medicamentoDe(solicitud, medicamentos);
          return (
            <li key={solicitud.id} className="rounded-md border border-slate-200 px-3 py-2 text-sm">
              <div className="flex items-center justify-between gap-2">
                <p className="font-medium">Solicitud {solicitud.id}</p>
                {noPos ? (
                  <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-950">
                    <Icon nombre="alerta" size={14} />
                    NO POS
                  </span>
                ) : (
                  <span className="rounded-full bg-teal-50 px-2 py-0.5 text-xs font-medium text-teal-800">
                    POS
                  </span>
                )}
              </div>
              <dl className="mt-2 space-y-1">
                <div className="flex gap-2">
                  <dt className="text-slate-500">Medicamento</dt>
                  <dd>{medicamento?.nombre ?? "—"}</dd>
                </div>
                {noPos &&
                  CAMPOS_ENTREGA.map(([clave, etiqueta]) => (
                    <div key={clave} className="flex gap-2">
                      <dt className="text-slate-500">{etiqueta}</dt>
                      <dd>{solicitud[clave] ?? "—"}</dd>
                    </div>
                  ))}
              </dl>
            </li>
          );
        })}
      </ul>
      <div className="flex items-center justify-between gap-3 text-sm">
        <button
          type="button"
          className="rounded-md border border-slate-300 px-3 py-1 disabled:opacity-40"
          onClick={() => setPagina((actual) => actual - 1)}
          disabled={pagina <= 1}
        >
          Anterior
        </button>
        <span>
          Página {pagina} de {paginas}
        </span>
        <button
          type="button"
          className="rounded-md border border-slate-300 px-3 py-1 disabled:opacity-40"
          onClick={() => setPagina((actual) => actual + 1)}
          disabled={pagina >= paginas}
        >
          Siguiente
        </button>
      </div>
    </section>
  );
}
