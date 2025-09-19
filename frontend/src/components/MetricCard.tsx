import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { clsx } from 'clsx';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon: LucideIcon;
  color: 'primary' | 'success' | 'warning' | 'error' | 'gray';
  trend?: 'creciente' | 'decreciente' | 'estable';
  compact?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeLabel,
  icon: Icon,
  color,
  trend = 'estable',
  compact = false,
}) => {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600',
    success: 'bg-success-50 text-success-600',
    warning: 'bg-warning-50 text-warning-600',
    error: 'bg-error-50 text-error-600',
    gray: 'bg-gray-50 text-gray-600',
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'creciente':
        return <TrendingUp className="h-4 w-4 text-success-500" />;
      case 'decreciente':
        return <TrendingDown className="h-4 w-4 text-error-500" />;
      default:
        return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const getChangeColor = () => {
    if (change === undefined) return 'text-gray-500';
    if (change > 0) return 'text-success-600';
    if (change < 0) return 'text-error-600';
    return 'text-gray-500';
  };

  const formatChange = (change: number) => {
    const sign = change > 0 ? '+' : '';
    return `${sign}${change.toFixed(1)}%`;
  };

  return (
    <div className={clsx(
      'card',
      compact ? 'p-4' : 'p-6'
    )}>
      <div className="flex items-center">
        <div className={clsx(
          'flex-shrink-0 rounded-lg p-2',
          colorClasses[color]
        )}>
          <Icon className={clsx(
            compact ? 'h-5 w-5' : 'h-6 w-6'
          )} />
        </div>
        <div className="ml-4 flex-1">
          <p className={clsx(
            'font-medium text-gray-900',
            compact ? 'text-sm' : 'text-base'
          )}>
            {title}
          </p>
          <p className={clsx(
            'font-semibold text-gray-900',
            compact ? 'text-lg' : 'text-2xl'
          )}>
            {value}
          </p>
          {change !== undefined && changeLabel && (
            <div className="mt-1 flex items-center">
              {getTrendIcon()}
              <span className={clsx(
                'ml-1 text-sm font-medium',
                getChangeColor()
              )}>
                {formatChange(change)}
              </span>
              <span className="ml-1 text-sm text-gray-500">
                {changeLabel}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};














