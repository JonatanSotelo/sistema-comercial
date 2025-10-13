import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { api } from "@/lib/api";
import ExportButtons from "@/components/ExportButtons";

type Cliente = {
  id: number;
  nombre: string;
  email?: string;
  cuit?: string;
  is_active?: boolean;
  created_at?: string;
};

export default function ClientesPage() {
  const [q, setQ] = useState("");
  const [items, setItems] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const abortRef = useRef<AbortController | null>(null);

  async function load(query = "") {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setLoading(true);
    try {
      const data = await api(`/clientes?q=${encodeURIComponent(query)}`, { signal: ctrl.signal as any });
      const list: Cliente[] = Array.isArray(data?.items) ? data.items : (Array.isArray(data) ? data : []);
      setItems(list);
    } finally {
      setLoading(false);
    }
  }

  // Cargar datos iniciales
  useEffect(() => { 
    load(""); 
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  // Búsqueda con debounce
  useEffect(() => {
    if (!q) return; // Solo ejecutar si hay texto de búsqueda
    const t = setTimeout(() => load(q), 400);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  async function onDelete(id: number) {
    if (!confirm("¿Eliminar el cliente seleccionado?")) return;
    try {
      await api(`/clientes/${id}`, { method: "DELETE" });
      setItems(prev => prev.filter(c => c.id !== id));
    } catch (e: any) {
      alert(e?.message || "No se pudo eliminar el cliente");
    }
  }


  const exportData = useMemo(
    () =>
      items.map(c => ({
        id: c.id,
        nombre: c.nombre,
        email: c.email ?? "",
        cuit: c.cuit ?? "",
        fecha_creacion: c.created_at ?? "",
      })),
    [items]
  );

  return (
    <div className="p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Clientes ({items.length})</h1>
        <div className="flex items-center gap-3">
          <input
            value={q}
            onChange={e => setQ(e.target.value)}
            placeholder="Buscar por nombre, email, CUIT…"
            className="border rounded px-3 py-1 text-sm"
          />
          <ExportButtons data={exportData} filename="clientes" />
          <button
            onClick={() => navigate("/clientes/nuevo")}
            className="inline-flex items-center gap-2 border rounded px-3 py-1 text-sm hover:bg-gray-50"
          >
            Nuevo cliente
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-sm text-gray-500">Cargando…</div>
      ) : (
        <div className="overflow-auto border rounded">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-3 py-2">ID</th>
                <th className="text-left px-3 py-2">Nombre</th>
                <th className="text-left px-3 py-2">Email</th>
                <th className="text-left px-3 py-2">CUIT</th>
                <th className="text-left px-3 py-2">Creado</th>
                <th className="text-left px-3 py-2">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.map(c => (
                <tr key={c.id} className="border-t">
                  <td className="px-3 py-2">{c.id}</td>
                  <td className="px-3 py-2">{c.nombre}</td>
                  <td className="px-3 py-2">{c.email ?? "-"}</td>
                  <td className="px-3 py-2">{c.cuit ?? "-"}</td>
                  <td className="px-3 py-2">{c.created_at?.slice(0, 10) ?? "-"}</td>
                  <td className="px-3 py-2">
                    <div className="flex gap-2">
                      <button
                        className="border rounded px-2 py-1 text-xs hover:bg-gray-50"
                        onClick={() => navigate(`/clientes/${c.id}`)}
                        title="Ver"
                      >
                        Ver
                      </button>
                      <button
                        className="border rounded px-2 py-1 text-xs hover:bg-gray-50"
                        onClick={() => navigate(`/clientes/${c.id}/editar`)}
                        title="Editar"
                      >
                        Editar
                      </button>
                      <button
                        className="border rounded px-2 py-1 text-xs hover:bg-red-50 text-red-600"
                        onClick={() => onDelete(c.id)}
                        title="Eliminar"
                      >
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td className="px-3 py-6 text-center text-gray-500" colSpan={6}>
                    Sin resultados
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}