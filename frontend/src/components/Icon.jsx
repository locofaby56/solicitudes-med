import { List, Lock, Pill, TriangleAlert, User } from "lucide-react";

const ICONOS = {
  candado: Lock,
  usuario: User,
  pastilla: Pill,
  lista: List,
  alerta: TriangleAlert,
};

export default function Icon({ nombre, ...props }) {
  const Dibujo = ICONOS[nombre];
  if (!Dibujo) {
    return null;
  }
  return <Dibujo aria-hidden="true" {...props} />;
}
