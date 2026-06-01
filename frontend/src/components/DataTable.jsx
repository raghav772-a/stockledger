export default function DataTable({ columns, rows, emptyMessage = 'No records found' }) {
  if (!rows?.length) {
    return (
      <div className="rounded-md border border-dashed border-surface-border bg-slate-50/50 py-12 text-center dark:border-slate-700 dark:bg-slate-800/30">
        <p className="text-sm text-slate-500">{emptyMessage}</p>
      </div>
    );
  }
  return (
    <div className="overflow-x-auto rounded-md border border-surface-border dark:border-slate-700">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:bg-slate-800">
          <tr>
            {columns.map((col) => (
              <th key={col.key} className="whitespace-nowrap border-b border-surface-border px-4 py-3 dark:border-slate-700">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-border bg-white dark:divide-slate-700 dark:bg-slate-900">
          {rows.map((row, i) => (
            <tr key={row.id || i} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/50">
              {columns.map((col) => (
                <td key={col.key} className="whitespace-nowrap px-4 py-3 text-slate-700 dark:text-slate-200">
                  {col.render ? col.render(row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
