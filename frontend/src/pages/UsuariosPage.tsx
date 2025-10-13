import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import ActionsMenu from "../components/ActionsMenu";

type Usuario = { 
  id: number; 
  username: string; 
  is_admin: boolean; 
  is_active: boolean; 
  created_at?: string 
};

export default function UsuariosPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const d = await api(`/usuarios?page=1&limit=100`);
      setItems(d?.items || d || []);
    } catch (e: any) {
      setError(e?.message || "No se pudieron cargar usuarios");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function toggleAdmin(u: Usuario) {
    try {
      await api(`/usuarios/${u.id}`, { 
        method: "PATCH", 
        body: JSON.stringify({ is_admin: !u.is_admin }) 
      });
      await load();
    } catch (e: any) {
      alert(e?.message || "No se pudo cambiar el rol");
    }
  }

  async function toggleActive(u: Usuario) {
    try {
      await api(`/usuarios/${u.id}`, { 
        method: "PATCH", 
        body: JSON.stringify({ is_active: !u.is_active }) 
      });
      await load();
    } catch (e: any) {
      alert(e?.message || "No se pudo cambiar el estado");
    }
  }

  async function eliminar(id: number) {
    if (!confirm("¿Eliminar usuario?")) return;
    try {
      await api(`/usuarios/${id}`, { method: "DELETE" });
      await load();
    } catch (e: any) {
      alert(e?.message || "No se pudo eliminar");
    }
  }

  return (
    <div className="p-4 space-y-3">
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-semibold">Usuarios <span className="text-sm opacity-70">({items.length})</span></h1>
        <button className="ml-auto border rounded px-3 py-1" onClick={() => navigate("/usuarios/nuevo")}>Nuevo</button>
      </div>

      {error && <div className="text-red-600 text-sm">{error}</div>}

      {loading ? (
        <div className="opacity-70 text-sm">Cargando...</div>
      ) : (
        <div className="border rounded overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="border p-2 text-left">Usuario</th>
                <th className="border p-2 text-left">Admin</th>
                <th className="border p-2 text-left">Activo</th>
                <th className="border p-2 text-left">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.map((u) => (
                <tr key={u.id}>
                  <td className="border p-2">{u.username}</td>
                  <td className="border p-2">
                    <button 
                      className={`border rounded px-2 text-sm ${u.is_admin ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}
                      onClick={() => toggleAdmin(u)}
                    >
                      {u.is_admin ? "Sí" : "No"}
                    </button>
                  </td>
                  <td className="border p-2">
                    <button 
                      className={`border rounded px-2 text-sm ${u.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}
                      onClick={() => toggleActive(u)}
                    >
                      {u.is_active ? "Activo" : "Inactivo"}
                    </button>
                  </td>
                  <td className="border p-2">
                    <ActionsMenu
                      onView={() => navigate(`/usuarios/${u.id}`)}
                      onEdit={() => navigate(`/usuarios/${u.id}/editar`)}
                      onDelete={() => eliminar(u.id)}
                    />
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td className="p-3 text-sm opacity-70" colSpan={4}>
                    No hay usuarios
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