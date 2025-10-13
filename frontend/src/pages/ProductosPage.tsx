import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { api } from "@/lib/api";
import ExportButtons from "@/components/ExportButtons";

type Producto = {
  id: number;
  nombre: string;
  sku?: string;
  categoria?: string;
  precio?: number;
  stock?: number;
  activo?: boolean;
  created_at?: string;
  tiene_movimientos?: boolean;
  puede_eliminar?: boolean;
};

export default function ProductosPage() {
  const [q, setQ] = useState("");
  const [items, setItems] = useState<Producto[]>([]);
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
      const data = await api(`/productos?q=${encodeURIComponent(query)}`, { signal: ctrl.signal as any });
      const list: Producto[] = Array.isArray(data?.items) ? data.items : (Array.isArray(data) ? data : []);
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
    if (!confirm("¿Eliminar el producto seleccionado?")) return;
    try {
      await api(`/productos/${id}`, { method: "DELETE" });
      setItems(prev => prev.filter(p => p.id !== id));
    } catch (e: any) {
      alert(e?.message || "No se pudo eliminar el producto");
    }
  }

  // Si tu backend expone PATCH /productos/:id con { activo: boolean }:
  async function toggleActivo(p: Producto) {
    const next = !p.activo;
    try {
      await api(`/productos/${p.id}`, {
        method: "PATCH",
        body: JSON.stringify({ activo: next }),
      });
      setItems(prev => prev.map(x => (x.id === p.id ? { ...x, activo: next } : x)));
    } catch (e: any) {
      alert(e?.message || "No se pudo cambiar el estado");
    }
  }

  const exportData = useMemo(
    () =>
      items.map(p => ({
        id: p.id,
        nombre: p.nombre,
        sku: p.sku ?? "",
        categoria: p.categoria ?? "",
        precio: p.precio ?? 0,
        stock: p.stock ?? 0,
        activo: p.activo ? "SI" : "NO",
        fecha_creacion: p.created_at ?? "",
      })),
    [items]
  );

  return (
    <div className="p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Productos ({items.length})</h1>
        <div className="flex items-center gap-3">
          <input
            value={q}
            onChange={e => setQ(e.target.value)}
            placeholder="Buscar por nombre, SKU, categoría…"
            className="border rounded px-3 py-1 text-sm"
          />
          <ExportButtons data={exportData} filename="productos" />
          <button
            onClick={() => navigate("/productos/new")}
            className="inline-flex items-center gap-2 border rounded px-3 py-1 text-sm hover:bg-gray-50"
          >
            Nuevo producto
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
                <th className="text-left px-3 py-2">SKU</th>
                <th className="text-left px-3 py-2">Categoría</th>
                <th className="text-left px-3 py-2">Precio</th>
                <th className="text-left px-3 py-2">Stock</th>
                <th className="text-left px-3 py-2">Activo</th>
                <th className="text-left px-3 py-2">Creado</th>
                <th className="text-left px-3 py-2" title="Indica si el producto se puede eliminar o tiene relaciones">💡 Estado</th>
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
                  <td className="px-3 py-2">{p.sku ?? "-"}</td>
                  <td className="px-3 py-2">{p.categoria ?? "-"}</td>
                  <td className="px-3 py-2">{p.precio ?? 0}</td>
                  <td className="px-3 py-2">{p.stock ?? 0}</td>
                  <td className="px-3 py-2">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs ${
                        p.activo ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {p.activo ? "ACTIVO" : "INACTIVO"}
                    </span>
                  </td>
                  <td className="px-3 py-2">{p.created_at?.slice(0, 10) ?? "-"}</td>
                  <td className="px-3 py-2">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs ${
                        esNuevo ? "bg-blue-100 text-blue-800" : "bg-orange-100 text-orange-800"
                      }`}
                      title={esNuevo ? "Producto nuevo, probablemente se puede eliminar" : "Producto con historial, puede tener ventas/compras"}
                    >
                      {esNuevo ? "🆕 NUEVO" : "📦 CON HISTORIAL"}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex gap-2">
                      <button
                        className="border rounded px-2 py-1 text-xs hover:bg-gray-50"
                        onClick={() => navigate(`/productos/${p.id}`)}
                        title="Ver"
                      >
                        Ver
                      </button>
                      <button
                        className="border rounded px-2 py-1 text-xs hover:bg-gray-50"
                        onClick={() => navigate(`/productos/${p.id}/edit`)}
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
                      <button
                        className="border rounded px-2 py-1 text-xs hover:bg-gray-50"
                        onClick={() => toggleActivo(p)}
                        title={p.activo ? "Desactivar" : "Activar"}
                      >
                        {p.activo ? "Desactivar" : "Activar"}
                      </button>
                    </div>
                  </td>
                </tr>
                );
              })}
              {items.length === 0 && (
                <tr>
                  <td className="px-3 py-6 text-center text-gray-500" colSpan={10}>
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