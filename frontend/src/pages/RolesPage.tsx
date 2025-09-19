import React, { useState, useEffect } from 'react';
import { Role, RoleCreate, RoleUpdate, Permission } from '@/types';
import { apiService } from '@/services/api';

const RolesPage: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Estados para modales
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);

  // Estados para formularios
  const [formData, setFormData] = useState<RoleCreate>({
    name: '',
    description: '',
    permission_ids: []
  });

  const [editFormData, setEditFormData] = useState<RoleUpdate>({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [rolesData, permissionsData] = await Promise.all([
        apiService.getRoles(),
        apiService.getPermissions()
      ]);
      
      setRoles(rolesData);
      setPermissions(permissionsData);
    } catch (err) {
      setError('Error al cargar los datos');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRole = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.createRole(formData);
      setShowCreateModal(false);
      setFormData({
        name: '',
        description: '',
        permission_ids: []
      });
      loadData();
    } catch (err) {
      setError('Error al crear el rol');
      console.error('Error creating role:', err);
    }
  };

  const handleEditRole = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRole) return;
    
    try {
      await apiService.updateRole(selectedRole.id, editFormData);
      setShowEditModal(false);
      setSelectedRole(null);
      setEditFormData({});
      loadData();
    } catch (err) {
      setError('Error al actualizar el rol');
      console.error('Error updating role:', err);
    }
  };

  const handleDeleteRole = async (roleId: number) => {
    if (!confirm('¿Estás seguro de que quieres eliminar este rol?')) return;
    
    try {
      await apiService.deleteRole(roleId);
      loadData();
    } catch (err) {
      setError('Error al eliminar el rol');
      console.error('Error deleting role:', err);
    }
  };

  const openEditModal = (role: Role) => {
    setSelectedRole(role);
    setEditFormData({
      name: role.name,
      description: role.description,
      permission_ids: role.permissions.map(p => p.id)
    });
    setShowEditModal(true);
  };

  const togglePermission = (permissionId: number, isEdit: boolean = false) => {
    if (isEdit) {
      const currentIds = editFormData.permission_ids || [];
      const newIds = currentIds.includes(permissionId)
        ? currentIds.filter(id => id !== permissionId)
        : [...currentIds, permissionId];
      setEditFormData({...editFormData, permission_ids: newIds});
    } else {
      const currentIds = formData.permission_ids;
      const newIds = currentIds.includes(permissionId)
        ? currentIds.filter(id => id !== permissionId)
        : [...currentIds, permissionId];
      setFormData({...formData, permission_ids: newIds});
    }
  };

  const groupedPermissions = permissions.reduce((acc, permission) => {
    if (!acc[permission.module]) {
      acc[permission.module] = [];
    }
    acc[permission.module].push(permission);
    return acc;
  }, {} as Record<string, Permission[]>);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Gestión de Roles y Permisos</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Nuevo Rol
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Lista de Roles */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Roles</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {roles.map((role) => (
              <div key={role.id} className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{role.name}</h3>
                    <p className="text-sm text-gray-500">{role.description}</p>
                    <div className="mt-2">
                      <span className="text-xs text-gray-500">
                        {role.permissions.length} permisos asignados
                      </span>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => openEditModal(role)}
                      className="text-indigo-600 hover:text-indigo-900 text-sm"
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => handleDeleteRole(role.id)}
                      className="text-red-600 hover:text-red-900 text-sm"
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
                <div className="mt-3">
                  <div className="flex flex-wrap gap-1">
                    {role.permissions.slice(0, 3).map((permission) => (
                      <span
                        key={permission.id}
                        className="inline-flex px-2 py-1 text-xs font-medium text-blue-800 bg-blue-100 rounded-full"
                      >
                        {permission.module}.{permission.action}
                      </span>
                    ))}
                    {role.permissions.length > 3 && (
                      <span className="inline-flex px-2 py-1 text-xs font-medium text-gray-500 bg-gray-100 rounded-full">
                        +{role.permissions.length - 3} más
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Lista de Permisos */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Permisos Disponibles</h2>
          </div>
          <div className="p-6">
            {Object.entries(groupedPermissions).map(([module, modulePermissions]) => (
              <div key={module} className="mb-6">
                <h3 className="text-md font-medium text-gray-900 mb-3 capitalize">{module}</h3>
                <div className="space-y-2">
                  {modulePermissions.map((permission) => (
                    <div
                      key={permission.id}
                      className="flex items-center justify-between p-2 bg-gray-50 rounded-md"
                    >
                      <div>
                        <span className="text-sm font-medium text-gray-900">
                          {permission.action}
                        </span>
                        <p className="text-xs text-gray-500">{permission.description}</p>
                      </div>
                      <span className="text-xs text-gray-400">
                        {permission.name}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Modal para crear rol */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-2/3 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Crear Nuevo Rol</h3>
              <form onSubmit={handleCreateRole}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre del rol
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Descripción
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Permisos
                  </label>
                  <div className="max-h-64 overflow-y-auto border border-gray-300 rounded-md p-4">
                    {Object.entries(groupedPermissions).map(([module, modulePermissions]) => (
                      <div key={module} className="mb-4">
                        <h4 className="text-sm font-medium text-gray-900 mb-2 capitalize">{module}</h4>
                        <div className="space-y-2">
                          {modulePermissions.map((permission) => (
                            <label key={permission.id} className="flex items-center">
                              <input
                                type="checkbox"
                                checked={formData.permission_ids.includes(permission.id)}
                                onChange={() => togglePermission(permission.id)}
                                className="mr-2"
                              />
                              <span className="text-sm text-gray-700">
                                {permission.action} - {permission.description}
                              </span>
                            </label>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                  >
                    Crear Rol
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Modal para editar rol */}
      {showEditModal && selectedRole && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-2/3 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Editar Rol</h3>
              <form onSubmit={handleEditRole}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre del rol
                  </label>
                  <input
                    type="text"
                    required
                    value={editFormData.name || selectedRole.name}
                    onChange={(e) => setEditFormData({...editFormData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Descripción
                  </label>
                  <textarea
                    value={editFormData.description || selectedRole.description || ''}
                    onChange={(e) => setEditFormData({...editFormData, description: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Permisos
                  </label>
                  <div className="max-h-64 overflow-y-auto border border-gray-300 rounded-md p-4">
                    {Object.entries(groupedPermissions).map(([module, modulePermissions]) => (
                      <div key={module} className="mb-4">
                        <h4 className="text-sm font-medium text-gray-900 mb-2 capitalize">{module}</h4>
                        <div className="space-y-2">
                          {modulePermissions.map((permission) => (
                            <label key={permission.id} className="flex items-center">
                              <input
                                type="checkbox"
                                checked={(editFormData.permission_ids || selectedRole.permissions.map(p => p.id)).includes(permission.id)}
                                onChange={() => togglePermission(permission.id, true)}
                                className="mr-2"
                              />
                              <span className="text-sm text-gray-700">
                                {permission.action} - {permission.description}
                              </span>
                            </label>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowEditModal(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                  >
                    Actualizar Rol
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RolesPage;

