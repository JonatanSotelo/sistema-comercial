import React from 'react';
import { LucideIcon } from 'lucide-react';
import { clsx } from 'clsx';

interface ChartCardProps {
  title: string;
  subtitle?: string;
  icon?: LucideIcon;
  children: React.ReactNode;
  className?: string;
}

export const ChartCard: React.FC<ChartCardProps> = ({
  title,
  subtitle,
  icon: Icon,
  children,
  className,
}) => {
  return (
    <div className={clsx('card', className)}>
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            {subtitle && (
              <p className="text-sm text-gray-500">{subtitle}</p>
            )}
          </div>
          {Icon && (
            <div className="flex-shrink-0 rounded-lg bg-primary-50 p-2">
              <Icon className="h-5 w-5 text-primary-600" />
            </div>
          )}
        </div>
      </div>
      <div className="card-content">
        {children}
      </div>
    </div>
  );
};














