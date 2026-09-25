import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { registrar } from "../api/client";
import Icon from "../components/Icon";

export default function Register({ alCrear, volver }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();
  const mutacion = useMutation({
    mutationFn: ({ correo, contrasena }) => registrar(correo, contrasena),
    onSuccess: () => alCrear?.(),
  });

  return (
    <form
      className="space-y-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
      onSubmit={handleSubmit((datos) => mutacion.mutate(datos))}
      noValidate
    >
      <h2 className="flex items-center gap-2 text-lg font-semibold">
        <Icon nombre="usuario" size={20} />
        Crear cuenta
      </h2>
      <div>
        <label className="mb-1 block text-sm" htmlFor="registro-correo">
          Correo
        </label>
        <input
          id="registro-correo"
          type="email"
          autoComplete="email"
          className="w-full rounded-md border border-slate-300 px-3 py-2"
          {...register("correo", { required: "Escribe tu correo" })}
        />
        {errors.correo && (
          <p className="mt-1 text-sm text-red-700" role="alert">
            {errors.correo.message}
          </p>
        )}
      </div>
      <div>
        <label className="mb-1 block text-sm" htmlFor="registro-contrasena">
          Contraseña
        </label>
        <input
          id="registro-contrasena"
          type="password"
          autoComplete="new-password"
          className="w-full rounded-md border border-slate-300 px-3 py-2"
          {...register("contrasena", {
            required: "Escribe una contraseña",
            minLength: { value: 8, message: "Usa al menos 8 caracteres" },
          })}
        />
        {errors.contrasena && (
          <p className="mt-1 text-sm text-red-700" role="alert">
            {errors.contrasena.message}
          </p>
        )}
      </div>
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
        Registrarme
      </button>
      <button type="button" className="text-sm text-teal-800 underline" onClick={volver}>
        Ya tengo cuenta
      </button>
    </form>
  );
}
