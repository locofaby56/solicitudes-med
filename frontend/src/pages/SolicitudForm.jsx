import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { crearSolicitud, listarMedicamentos } from "../api/client";
import Icon from "../components/Icon";

export default function SolicitudForm({ medicamentos, token }) {
  const consultas = useQueryClient();
  const catalogo = useQuery({
    queryKey: ["medicamentos", token],
    queryFn: () => listarMedicamentos(token),
    enabled: medicamentos === undefined && Boolean(token),
  });
  const lista = medicamentos ?? catalogo.data ?? [];
  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm({ defaultValues: { medicamento_id: "" } });
  const medicamentoId = watch("medicamento_id");
  const elegido = lista.find((item) => String(item.id) === String(medicamentoId));
  const esNoPos = Boolean(elegido?.es_no_pos);
  const mutacion = useMutation({
    mutationFn: (datos) => crearSolicitud(token, datos),
    onSuccess: () => {
      reset();
      consultas.invalidateQueries({ queryKey: ["solicitudes"] });
    },
  });

  function enviar(datos) {
    const actual = lista.find((item) => String(item.id) === String(datos.medicamento_id));
    const cuerpo = { medicamento_id: Number(datos.medicamento_id) };
    if (actual?.es_no_pos) {
      cuerpo.numero_orden = datos.numero_orden;
      cuerpo.direccion = datos.direccion;
      cuerpo.telefono = datos.telefono;
      cuerpo.correo = datos.correo;
    }
    mutacion.mutate(cuerpo);
  }

  return (
    <form
      className="space-y-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
      onSubmit={handleSubmit(enviar)}
      noValidate
    >
      <h2 className="flex items-center gap-2 text-lg font-semibold">
        <Icon nombre="pastilla" size={20} />
        Nueva solicitud
      </h2>
      {medicamentos === undefined && catalogo.isPending && <p>Cargando medicamentos.</p>}
      {catalogo.isError && (
        <p className="text-sm text-red-700" role="alert">
          {catalogo.error.message}
        </p>
      )}
      {medicamentos === undefined && catalogo.isSuccess && lista.length === 0 && (
        <p>No hay medicamentos en el catálogo.</p>
      )}
      <div>
        <label className="mb-1 block text-sm" htmlFor="medicamento">
          Medicamento
        </label>
        <select
          id="medicamento"
          className="w-full rounded-md border border-slate-300 px-3 py-2"
          {...register("medicamento_id", { required: "Elige un medicamento" })}
        >
          <option value="">Elige un medicamento</option>
          {lista.map((medicamento) => (
            <option key={medicamento.id} value={medicamento.id}>
              {medicamento.nombre}
            </option>
          ))}
        </select>
        {errors.medicamento_id && (
          <p className="mt-1 text-sm text-red-700" role="alert">
            {errors.medicamento_id.message}
          </p>
        )}
      </div>
      {esNoPos && (
        <fieldset className="space-y-3 rounded-md border border-amber-300 bg-amber-50 p-3">
          <legend className="flex items-center gap-2 px-1 text-sm font-medium text-amber-950">
            <Icon nombre="alerta" size={18} />
            Medicamento NO POS
          </legend>
          <p className="text-sm text-amber-950">
            Hacen falta el número de orden, la dirección, el teléfono y el correo de entrega.
          </p>
          <Campo
            id="numero_orden"
            etiqueta="Número de orden"
            error={errors.numero_orden?.message}
            registro={register("numero_orden", { required: "Escribe el número de orden" })}
          />
          <Campo
            id="direccion"
            etiqueta="Dirección"
            error={errors.direccion?.message}
            registro={register("direccion", { required: "Escribe la dirección" })}
          />
          <Campo
            id="telefono"
            etiqueta="Teléfono"
            error={errors.telefono?.message}
            registro={register("telefono", { required: "Escribe el teléfono" })}
          />
          <Campo
            id="correo-entrega"
            etiqueta="Correo"
            tipo="email"
            error={errors.correo?.message}
            registro={register("correo", { required: "Escribe el correo de entrega" })}
          />
        </fieldset>
      )}
      {mutacion.isError && (
        <p className="text-sm text-red-700" role="alert">
          {mutacion.error.message}
        </p>
      )}
      <button
        type="submit"
        className="w-full rounded-md bg-teal-800 px-4 py-2 text-white disabled:opacity-60"
        disabled={mutacion.isPending}
      >
        Enviar solicitud
      </button>
    </form>
  );
}

function Campo({ id, etiqueta, tipo = "text", error, registro }) {
  return (
    <div>
      <label className="mb-1 block text-sm" htmlFor={id}>
        {etiqueta}
      </label>
      <input
        id={id}
        type={tipo}
        className="w-full rounded-md border border-slate-300 bg-white px-3 py-2"
        {...registro}
      />
      {error && (
        <p className="mt-1 text-sm text-red-700" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
