import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  Home, 
  Package, 
  Users, 
  Truck, 
  ShoppingCart, 
  ShoppingBag, 
  Warehouse,
  BarChart3, 
  FileText, 
  Settings,
  Building2,
  UserCog,
  Shield
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { clsx } from 'clsx';

interface SidebarProps {
  onClose?: () => void;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Productos', href: '/productos', icon: Package },
  { name: 'Clientes', href: '/clientes', icon: Users },
  { name: 'Proveedores', href: '/proveedores', icon: Truck },
  { name: 'Ventas', href: '/ventas', icon: ShoppingCart },
  { name: 'Compras', href: '/compras', icon: ShoppingBag },
  { name: 'Inventario', href: '/inventario', icon: Warehouse },
  { name: 'Métricas', href: '/metricas', icon: BarChart3 },
  { name: 'Reportes', href: '/reportes', icon: FileText },
  { name: 'Usuarios', href: '/usuarios', icon: UserCog, adminOnly: true },
  { name: 'Roles', href: '/roles', icon: Shield, adminOnly: true },
  { name: 'Configuración', href: '/configuracion', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ onClose }) => {
  const location = useLocation();
  const { user } = useAuth();

  return (
    <div className="flex h-full flex-col bg-white shadow-lg">
      {/* Logo y nombre de la empresa */}
      <div className="flex h-16 items-center px-6 border-b border-gray-200">
        <div className="flex items-center">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600">
            <Building2 className="h-5 w-5 text-white" />
          </div>
          <div className="ml-3">
            <h1 className="text-lg font-semibold text-gray-900">Sistema Comercial</h1>
            <p className="text-xs text-gray-500">Gestión Empresarial</p>
          </div>
        </div>
      </div>

      {/* Navegación */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          // Verificar si el usuario puede ver este elemento
          if (item.adminOnly && user?.role !== 'admin') {
            return null;
          }
          
          const isActive = location.pathname === item.href;
          const Icon = item.icon;
          
          return (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={onClose}
              className={clsx(
                'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                isActive
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              )}
            >
              <Icon
                className={clsx(
                  'mr-3 h-5 w-5 flex-shrink-0',
                  isActive ? 'text-primary-700' : 'text-gray-400 group-hover:text-gray-500'
                )}
              />
              {item.name}
            </NavLink>
          );
        })}
      </nav>

      {/* Información del usuario */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-300">
              <span className="text-sm font-medium text-gray-700">
                {user?.username?.charAt(0).toUpperCase()}
              </span>
            </div>
          </div>
          <div className="ml-3 min-w-0 flex-1">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.username}
            </p>
            <p className="text-xs text-gray-500 capitalize">
              {user?.role === 'admin' ? 'Administrador' : 'Usuario'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};










