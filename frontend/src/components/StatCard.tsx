import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: string;
  trendType?: 'positive' | 'negative' | 'neutral';
  color?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  trendType = 'neutral',
  color = 'from-indigo-500/20 to-blue-500/20 border-indigo-500/30'
}) => {
  return (
    <div className={`relative overflow-hidden rounded-xl border bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm transition-all duration-200 hover:border-slate-600 hover:shadow-indigo-500/5 ${color}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</p>
          <h3 className="mt-1 text-2xl font-bold tracking-tight text-white">{value}</h3>
          {subtitle && <p className="mt-0.5 text-xs text-slate-400">{subtitle}</p>}
        </div>
        <div className="rounded-lg bg-slate-800/80 p-2.5 text-indigo-400 ring-1 ring-white/10">
          {icon}
        </div>
      </div>
      {trend && (
        <div className="mt-3 flex items-center text-xs">
          <span
            className={`font-semibold ${
              trendType === 'positive'
                ? 'text-emerald-400'
                : trendType === 'negative'
                ? 'text-rose-400'
                : 'text-slate-400'
            }`}
          >
            {trend}
          </span>
          <span className="ml-1 text-slate-400">vs prev period</span>
        </div>
      )}
    </div>
  );
};
