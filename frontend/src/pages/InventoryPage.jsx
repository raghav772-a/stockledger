import { useCallback, useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import api, { fetchData } from '../services/api';
import { useDataRefresh } from '../context/DataRefreshContext';
import { getErrorMessage } from '../utils/errors';
import DataTable from '../components/DataTable';
import Pagination from '../components/Pagination';
import PageHeader from '../components/PageHeader';
import SkeletonLoader from '../components/SkeletonLoader';

export default function InventoryPage() {
  const { tick } = useDataRefresh();
  const [data, setData] = useState({ items: [], total_pages: 1, total: 0 });
  const [products, setProducts] = useState([]);
  const [productFilter, setProductFilter] = useState('');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const loadProducts = useCallback(async () => {
    const result = await fetchData(api.get('/products', { params: { page_size: 100 } }));
    setProducts(result.items || []);
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchData(
        api.get('/inventory/logs', {
          params: {
            page,
            page_size: 20,
            product_id: productFilter || undefined,
          },
        })
      );
      setData(result);
    } catch (e) {
      toast.error(getErrorMessage(e, 'Failed to load stock movements'));
    } finally {
      setLoading(false);
    }
  }, [page, productFilter]);

  useEffect(() => {
    loadProducts().catch(() => {});
  }, [loadProducts, tick]);

  useEffect(() => {
    load();
  }, [load, tick]);

  return (
    <div className="space-y-4">
      <PageHeader
        title="Stock movements"
        subtitle={`${data.total ?? 0} inventory transactions`}
        actions={
          <button type="button" className="btn-secondary" onClick={load}>
            Refresh
          </button>
        }
      />

      <div className="card flex flex-wrap items-end gap-3">
        <div className="min-w-[200px] flex-1">
          <label className="mb-1 block text-xs font-semibold uppercase text-slate-500">Filter by item</label>
          <select
            className="input-field"
            value={productFilter}
            onChange={(e) => {
              setProductFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All items</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.sku})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <SkeletonLoader className="h-48 w-full" />
      ) : (
        <div className="card !p-0 overflow-hidden">
          <DataTable
            columns={[
              { key: 'created_at', label: 'Date', render: (r) => new Date(r.created_at).toLocaleString() },
              { key: 'product_name', label: 'Item', render: (r) => r.product_name || r.product_id },
              { key: 'movement_type', label: 'Type', render: (r) => String(r.movement_type).replace(/_/g, ' ') },
              {
                key: 'quantity_change',
                label: 'Change',
                render: (r) => (
                  <span className={r.quantity_change < 0 ? 'text-red-600' : 'text-green-600'}>
                    {r.quantity_change > 0 ? '+' : ''}
                    {r.quantity_change}
                  </span>
                ),
              },
              { key: 'quantity_after', label: 'Stock after' },
              { key: 'reference', label: 'Reference', render: (r) => r.reference || '—' },
            ]}
            rows={data.items}
            emptyMessage="No stock movements yet. Create a sales order or adjust stock to see history."
          />
          <div className="border-t border-surface-border p-4 dark:border-slate-700">
            <Pagination page={page} totalPages={data.total_pages} onPageChange={setPage} />
          </div>
        </div>
      )}
    </div>
  );
}
