import React from 'react';
import { LucideIcon, AlertTriangle, AlertCircle, Info, CheckCircle } from 'lucide-react';
import { clsx } from 'clsx';

interface AlertCardProps {
  type: 'error' | 'warning' | 'info' | 'success';
  title: string;
  message: string;
  icon?: LucideIcon;
  onDismiss?: () => void;
}

export const AlertCard: React.FC<AlertCardProps> = ({
  type,
  title,
  message,
  icon,
  onDismiss,
}) => {
  const getTypeStyles = () => {
    switch (type) {
      case 'error':
        return {
          container: 'bg-error-50 border-error-200',
          icon: 'text-error-500',
          title: 'text-error-800',
          message: 'text-error-700',
        };
      case 'warning':
        return {
          container: 'bg-warning-50 border-warning-200',
          icon: 'text-warning-500',
          title: 'text-warning-800',
          message: 'text-warning-700',
        };
      case 'info':
        return {
          container: 'bg-primary-50 border-primary-200',
          icon: 'text-primary-500',
          title: 'text-primary-800',
          message: 'text-primary-700',
        };
      case 'success':
        return {
          container: 'bg-success-50 border-success-200',
          icon: 'text-success-500',
          title: 'text-success-800',
          message: 'text-success-700',
        };
      default:
        return {
          container: 'bg-gray-50 border-gray-200',
          icon: 'text-gray-500',
          title: 'text-gray-800',
          message: 'text-gray-700',
        };
    }
  };

  const getDefaultIcon = (): LucideIcon => {
    switch (type) {
      case 'error':
        return AlertCircle;
      case 'warning':
        return AlertTriangle;
      case 'info':
        return Info;
      case 'success':
        return CheckCircle;
      default:
        return Info;
    }
  };

  const styles = getTypeStyles();
  const Icon = icon || getDefaultIcon();

  return (
    <div className={clsx(
      'rounded-lg border p-4',
      styles.container
    )}>
      <div className="flex">
        <div className="flex-shrink-0">
          <Icon className={clsx('h-5 w-5', styles.icon)} />
        </div>
        <div className="ml-3 flex-1">
          <h3 className={clsx('text-sm font-medium', styles.title)}>
            {title}
          </h3>
          <p className={clsx('mt-1 text-sm', styles.message)}>
            {message}
          </p>
        </div>
        {onDismiss && (
          <div className="ml-auto pl-3">
            <button
              type="button"
              className={clsx(
                'inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2',
                styles.icon,
                'hover:bg-black hover:bg-opacity-10'
              )}
              onClick={onDismiss}
            >
              <span className="sr-only">Cerrar</span>
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};



