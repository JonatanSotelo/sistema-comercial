import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import SearchInput from "../components/SearchInput";
import ExportButtons from "../components/ExportButtons";
import ActionsMenu from "../components/ActionsMenu";

type ProductoInventario = {
  id: number;
  nombre: string;
  stock: number;
  stock_minimo: number;
  categoria: string;
  precio: number;
  is_active: boolean;
};

export default function InventarioPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<ProductoInventario[]>([]);
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api(`/productos?q=${encodeURIComponent(q)}&page=${page}&limit=${limit}`);
      setItems(data.items || []);
      setTotal(data.total || 0);
    } catch (e: any) {
      setError(e?.message || "Error al cargar inventario");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); /* eslint-disable-next-line */ }, [page, q]);

  async function ajustarStock(id: number, cantidad: number) {
    try {
      await api(`/inventario/ajustar`, {
        method: "POST",
        body: JSON.stringify({
          producto_id: id,
          cantidad: cantidad,
          motivo: "Ajuste manual"
        })
      });
      await load();
    } catch (e: any) {
      alert(e?.message || "No se pudo ajustar el stock");
    }
  }

  const getStockStatus = (stock: number, stockMinimo: number) => {
    if (stock === 0) return { label: 'Agotado', color: 'text-red-600 bg-red-100' };
    if (stock <= stockMinimo) return { label: 'Bajo', color: 'text-orange-600 bg-orange-100' };
    return { label: 'Disponible', color: 'text-green-600 bg-green-100' };
  };

  return (
    <div className="p-4 space-y-3">
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-semibold">Inventario <span className="text-sm opacity-70">({total})</span></h1>
        <ExportButtons resourcePath="/inventario" />
      </div>

      <div className="flex gap-2">
        <SearchInput onSearch={setQ} placeholder="Buscar productos..." />
      </div>

      {error && <div className="text-red-600 text-sm">{error}</div>}

      <table className="w-full border">
        <thead>
          <tr>
            <th className="border p-2">ID</th>
            <th className="border p-2">Producto</th>
            <th className="border p-2">Categoría</th>
            <th className="border p-2">Stock</th>
            <th className="border p-2">Mínimo</th>
            <th className="border p-2">Estado</th>
            <th className="border p-2">Precio</th>
            <th className="border p-2">Acciones</th>
                  </tr>
                </thead>
        <tbody>
          {!loading && items.map((p) => {
            const stockStatus = getStockStatus(p.stock, p.stock_minimo);
            return (
              <tr key={p.id}>
                <td className="border p-2">{p.id}</td>
                <td className="border p-2">{p.nombre}</td>
                <td className="border p-2">{p.categoria}</td>
                <td className="border p-2">{p.stock}</td>
                <td className="border p-2">{p.stock_minimo}</td>
                <td className="border p-2">
                  <span className={`px-2 py-1 rounded text-xs ${stockStatus.color}`}>
                    {stockStatus.label}
                        </span>
                      </td>
                <td className="border p-2">${p.precio}</td>
                <td className="border p-2">
                  <div className="flex gap-2">
                    <ActionsMenu
                      onView={() => navigate(`/productos/${p.id}`)}
                      onEdit={() => navigate(`/productos/${p.id}/editar`)}
                    />
                <button
                      className="border rounded px-2 text-sm"
                        onClick={() => {
                        const cantidad = prompt(`Ajustar stock de ${p.nombre} (actual: ${p.stock}):`);
                        if (cantidad && !isNaN(Number(cantidad))) {
                          ajustarStock(p.id, Number(cantidad));
                        }
                      }}
                    >
                      Ajustar
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
          {loading && (
            <tr><td className="p-3 text-sm opacity-70" colSpan={8}>Cargando...</td></tr>
          )}
          {!loading && items.length === 0 && (
            <tr><td className="p-3 text-sm opacity-70" colSpan={8}>Sin resultados</td></tr>
          )}
        </tbody>
      </table>

      <div className="flex items-center gap-2">
        <button className="border rounded px-3" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Anterior</button>
        <span>Página {page}</span>
        <button className="border rounded px-3" disabled={page * limit >= total} onClick={() => setPage((p) => p + 1)}>Siguiente</button>
        </div>
    </div>
  );
}