import { useCallback, useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import api, { fetchData } from '../services/api';
import { useDataRefresh } from '../context/DataRefreshContext';
import { getErrorMessage } from '../utils/errors';
import DataTable from '../components/DataTable';
import SkeletonLoader from '../components/SkeletonLoader';
import PageHeader from '../components/PageHeader';
import toast from 'react-hot-toast';

export default function AnalyticsPage() {
  const { tick } = useDataRefresh();
  const [monthly, setMonthly] = useState([]);
  const [top, setTop] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const [m, t, s] = await Promise.all([
        fetchData(api.get('/dashboard/monthly-sales')),
        fetchData(api.get('/dashboard/top-products')),
        fetchData(api.get('/dashboard/stats')),
      ]);
      setMonthly(m);
      setTop(t);
      setStats(s);
    } catch (e) {
      toast.error(getErrorMessage(e, 'Failed to load analytics'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setLoading(true);
    load();
  }, [load, tick]);

  if (loading) return <SkeletonLoader className="h-64 w-full" />;

  return (
    <div className="space-y-6">
      <PageHeader title="Reports" subtitle="Sales performance and product insights" />
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="card">
          <p className="text-sm text-slate-500">Total revenue</p>
          <p className="text-2xl font-bold">${Number(stats?.total_revenue || 0).toLocaleString()}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-500">Orders</p>
          <p className="text-2xl font-bold">{stats?.total_orders ?? 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-500">Low stock items</p>
          <p className="text-2xl font-bold text-amber-600">{stats?.low_stock_count ?? 0}</p>
        </div>
      </div>
      <div className="card">
        <h2 className="mb-4 font-semibold">Revenue by month</h2>
        {monthly.length === 0 ? (
          <p className="text-sm text-slate-500">No sales data yet. Create orders to see charts.</p>
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(v) => [`$${Number(v).toFixed(2)}`, 'Revenue']} />
              <Bar dataKey="revenue" fill="#4f46e5" name="Revenue" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
      <div className="card">
        <h2 className="mb-4 font-semibold">Top products</h2>
        <DataTable
          columns={[
            { key: 'product_name', label: 'Product' },
            { key: 'total_sold', label: 'Units sold' },
            { key: 'revenue', label: 'Revenue', render: (r) => `$${Number(r.revenue).toFixed(2)}` },
          ]}
          rows={top}
          emptyMessage="No sales yet."
        />
      </div>
    </div>
  );
}
