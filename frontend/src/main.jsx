import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

const consultas = new QueryClient();

createRoot(document.getElementById("raiz")).render(
  <StrictMode>
    <QueryClientProvider client={consultas}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
);
