import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { api } from "@/lib/api";
import ExportButtons from "@/components/ExportButtons";

type Proveedor = {
  id: number;
  nombre: string;
  email?: string;
  telefono?: string;
  is_active?: boolean;
  created_at?: string;
};

export default function ProveedoresPage() {
  const [q, setQ] = useState("");
  const [items, setItems] = useState<Proveedor[]>([]);
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
      const data = await api(`/proveedores?q=${encodeURIComponent(query)}`, { signal: ctrl.signal as any });
      const list: Proveedor[] = Array.isArray(data?.items) ? data.items : (Array.isArray(data) ? data : []);
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
    if (!confirm("¿Eliminar el proveedor seleccionado?")) return;
    try {
      await api(`/proveedores/${id}`, { method: "DELETE" });
      setItems(prev => prev.filter(p => p.id !== id));
    } catch (e: any) {
      alert(e?.message || "No se pudo eliminar el proveedor");
    }
  }

  const exportData = useMemo(
    () =>
      items.map(p => ({
        id: p.id,
        nombre: p.nombre,
        email: p.email ?? "",
        telefono: p.telefono ?? "",
        fecha_creacion: p.created_at ?? "",
      })),
    [items]
  );

  return (
    <div className="p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Proveedores ({items.length})</h1>
      <div className="flex items-center gap-3">
          <input
            value={q}
            onChange={e => setQ(e.target.value)}
            placeholder="Buscar por nombre, email…"
            className="border rounded px-3 py-1 text-sm"
          />
          <ExportButtons data={exportData} filename="proveedores" />
          <button
            onClick={() => navigate("/proveedores/nuevo")}
            className="inline-flex items-center gap-2 border rounded px-3 py-1 text-sm hover:bg-gray-50"
          >
            Nuevo proveedor
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
                <th className="text-left px-3 py-2">Teléfono</th>
                <th className="text-left px-3 py-2">Creado</th>
                <th className="text-left px-3 py-2" title="Indica si el proveedor se puede eliminar">💡 Estado</th>
                <th className="text-left px-3 py-2">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.map(p => {
                const esNuevo = p.created_at ? (new Date().getTime() - new Date(p.created_at).getTime()) < 86400000 : false;
                return (
                <tr key={p.id} className="border-t">
                  <td className="px-3 py-2">{p.id}</td>
                  <td className="px-3 py-2">{p.nombre}</td>
                  <td className="px-3 py-2">{p.email ?? "-"}</td>
                  <td className="px-3 py-2">{p.telefono ?? "-"}</td>
                  <td className="px-3 py-2">{p.created_at?.slice(0, 10) ?? "-"}</td>
                  <td className="px-3 py-2">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs ${
                        esNuevo ? "bg-blue-100 text-blue-800" : "bg-orange-100 text-orange-800"
                      }`}
                      title={esNuevo ? "Proveedor nuevo, probablemente se puede eliminar" : "Proveedor con historial, puede tener compras"}
                    >
                      {esNuevo ? "🆕 NUEVO" : "📦 CON HISTORIAL"}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex gap-2">
                      <button
                        className="border rounded px-2 py-1 text-xs hover:bg-gray-50"
                        onClick={() => navigate(`/proveedores/${p.id}`)}
                        title="Ver"
                      >
                        Ver
                      </button>
                      <button
                        className="border rounded px-2 py-1 text-xs hover:bg-gray-50"
                        onClick={() => navigate(`/proveedores/${p.id}/editar`)}
                        title="Editar"
                      >
                        Editar
                      </button>
                      <button
                        className="border rounded px-2 py-1 text-xs hover:bg-red-50 text-red-600"
                        onClick={() => onDelete(p.id)}
                        title="Eliminar"
                      >
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
                );
              })}
              {items.length === 0 && (
                <tr>
                  <td className="px-3 py-6 text-center text-gray-500" colSpan={7}>
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