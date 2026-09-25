function urlBase() {
  const url = import.meta.env.VITE_API_URL;
  if (!url) {
    throw new Error("Falta VITE_API_URL");
  }
  return String(url).replace(/\/$/, "");
}

function mensajeDeError(datos) {
  if (typeof datos?.detail === "string" && datos.detail) {
    return datos.detail;
  }
  if (Array.isArray(datos?.detail)) {
    const textos = datos.detail.map((item) => item?.msg).filter(Boolean);
    if (textos.length) {
      return textos.join(". ");
    }
  }
  return "No se pudo completar la solicitud";
}

async function pedir(ruta, { metodo = "GET", cuerpo, token } = {}) {
  const respuesta = await fetch(`${urlBase()}${ruta}`, {
    method: metodo,
    headers: {
      Accept: "application/json",
      ...(cuerpo ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  });
  const datos = await respuesta.json().catch(() => ({}));
  if (!respuesta.ok) {
    throw new Error(mensajeDeError(datos));
  }
  return datos;
}

export function registrar(correo, contrasena) {
  return pedir("/registro", { metodo: "POST", cuerpo: { correo, contrasena } });
}

export function iniciarSesion(correo, contrasena) {
  return pedir("/iniciar-sesion", { metodo: "POST", cuerpo: { correo, contrasena } });
}

export function listarMedicamentos(token) {
  return pedir("/medicamentos", { token });
}

export function crearSolicitud(token, datos) {
  return pedir("/solicitudes", { metodo: "POST", token, cuerpo: datos });
}

export function listarSolicitudes(token, pagina, porPagina) {
  const params = new URLSearchParams({
    pagina: String(pagina),
    por_pagina: String(porPagina),
  });
  return pedir(`/solicitudes?${params}`, { token });
}
