export default function StatCard({ title, value, icon: Icon, trend }) {
  return (
    <div className="card flex flex-col gap-3 !p-4">
      <div className="flex items-start justify-between">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</p>
        {Icon && (
          <span className="rounded-md bg-brand-50 p-2 text-brand-600">
            <Icon size={18} strokeWidth={2} />
          </span>
        )}
      </div>
      <p className="text-2xl font-bold tabular-nums text-slate-900 dark:text-white">{value ?? '—'}</p>
      {trend && <p className="text-xs text-slate-500">{trend}</p>}
    </div>
  );
}
