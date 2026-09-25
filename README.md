# Solicitudes de medicamentos

Alguien se registra, entra y pide un medicamento del catálogo.

Si el medicamento es NO POS, hay que mandar número de orden, dirección, teléfono y correo. Si falta uno, no se guarda. La lista sale por páginas. Sin sesión no se ve.

Para dejarlo andando:

1. En la raíz, crea el entorno con `python -m venv venv`.
2. Actívalo. En PowerShell: `venv\Scripts\Activate.ps1`. En bash: `source venv/bin/activate`.
3. Instala el backend: `pip install -r backend/requirements.txt`.
4. Crea un `.env` en la raíz. Más abajo van los nombres.
5. Crea las tablas: `mysql -u root -p < db/schema.sql`.
6. Prende la API desde la raíz, con el entorno activo: `uvicorn main:app --app-dir backend --reload`. Si ya estás dentro de `backend`, basta con `uvicorn main:app --reload`.
7. Entra a `frontend` y corre `npm install`.
8. En `frontend/.env` pon `VITE_API_URL=http://127.0.0.1:8000`. Si moviste el puerto, cambia esa dirección.
9. Arranca la pantalla con `npm run dev`.

## Entorno de ejecución

La API queda en `http://127.0.0.1:8000`. La pantalla abre en `http://localhost:5173`. También vale `http://127.0.0.1:5173`. La API acepta esos dos orígenes.

El backend usa el entorno virtual de la raíz y lo que está en `backend/requirements.txt`. No instales paquetes de Python por fuera. La pantalla usa Node. Sus paquetes se instalan dentro de `frontend`.

MySQL no va escrito en el código. Va en el `.env` de la raíz: `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME` y `DB_PASSWORD`. El script crea la base `solicitudes_med`. Ese usuario tiene que poder leer y escribir ahí. `JWT_SECRET` firma el token. Si no está, el login no devuelve token.

La pantalla llama a la API con `VITE_API_URL`, en `frontend/.env`. En local es `http://127.0.0.1:8000`.

La lista muestra 10 solicitudes por página. Arranca en la página 1. Anterior y Siguiente piden la página de al lado, también de 10. Si llamas la API a mano, `por_pagina` puede ir de 1 a 50. Si no lo mandas, la API usa 10.

## Endpoints

Los que piden sesión llevan `Authorization: Bearer` y el token. Si falta o no sirve, responden 401. El texto del error va en `detail`. Si el cuerpo viene mal formado, también.

### POST /registro

Crea la cuenta. El cuerpo lleva `correo` y `contrasena`. La contraseña pide 8 caracteres. Si el correo es nuevo, responde 201 con `id` y `correo`. La clave se guarda encriptada y no vuelve. Si el correo ya está, responde 400.

### POST /iniciar-sesion

Entra con el mismo cuerpo: `correo` y `contrasena`. Si coinciden, responde 200 y un `token`. Si no, responde 401.

### GET /medicamentos

Devuelve el catálogo de quien ya entró. Cada ítem trae `id`, `nombre` y `es_no_pos`.

### POST /solicitudes

Crea el pedido de quien inició sesión. El cuerpo lleva `medicamento_id`. Si el medicamento es POS, la entrega queda vacía. Si es NO POS, agrega `numero_orden`, `direccion`, `telefono` y `correo`. Falta uno y responde 400. No existe el medicamento y responde 404. Si sale bien, responde 201 con `id`, `usuario_id`, `medicamento_id`, los datos de entrega y `creado_en`.

### GET /solicitudes

Lista los pedidos de esa misma persona. Acepta `pagina` y `por_pagina`. La página empieza en 1. `por_pagina` va de 1 a 50. Si no los mandas, usa 10. Responde `solicitudes`, `pagina`, `por_pagina` y `total`. La pantalla pide de 10 en 10.
