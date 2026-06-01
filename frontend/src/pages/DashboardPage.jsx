import { useCallback, useEffect, useState } from 'react';
import { Package, Users, ShoppingCart, DollarSign } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import api, { fetchData } from '../services/api';
import { useDataRefresh } from '../context/DataRefreshContext';
import { getErrorMessage } from '../utils/errors';
import StatCard from '../components/StatCard';
import DataTable from '../components/DataTable';
import PageHeader from '../components/PageHeader';
import SkeletonLoader from '../components/SkeletonLoader';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const { tick } = useDataRefresh();
  const [stats, setStats] = useState(null);
  const [monthly, setMonthly] = useState([]);
  const [recent, setRecent] = useState([]);
  const [lowStock, setLowStock] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const [s, m, r, l] = await Promise.all([
        fetchData(api.get('/dashboard/stats')),
        fetchData(api.get('/dashboard/monthly-sales')),
        fetchData(api.get('/dashboard/recent-orders')),
        fetchData(api.get('/dashboard/low-stock')),
      ]);
      setStats(s);
      setMonthly(m);
      setRecent(r);
      setLowStock(l);
    } catch (e) {
      setError(getErrorMessage(e, 'Failed to load dashboard'));
      toast.error(getErrorMessage(e, 'Failed to load dashboard'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setLoading(true);
    load();
  }, [load, tick]);

  if (loading) return <SkeletonLoader className="h-64 w-full" />;

  if (error && !stats) {
    return (
      <div className="card text-center">
        <p className="text-red-600">{error}</p>
        <button type="button" className="btn-primary mt-4" onClick={() => load()}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Home" subtitle="Overview of your inventory and sales performance" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Total revenue" value={`$${Number(stats?.total_revenue || 0).toLocaleString()}`} icon={DollarSign} />
        <StatCard title="Active items" value={stats?.total_products ?? 0} icon={Package} />
        <StatCard title="Customers" value={stats?.total_customers ?? 0} icon={Users} />
        <StatCard title="Sales orders" value={stats?.total_orders ?? 0} icon={ShoppingCart} />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card">
          <h2 className="mb-4 font-semibold">Monthly sales</h2>
          {monthly.length === 0 ? (
            <p className="text-sm text-slate-500">No sales yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={monthly}>
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(v) => `$${Number(v).toFixed(2)}`} />
                <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="card">
          <h2 className="mb-4 font-semibold text-amber-600">Low stock ({stats?.low_stock_count ?? 0})</h2>
          <DataTable
            columns={[
              { key: 'name', label: 'Product' },
              { key: 'sku', label: 'SKU' },
              { key: 'quantity', label: 'Qty' },
            ]}
            rows={lowStock}
            emptyMessage="All products are well stocked"
          />
        </div>
      </div>
      <div className="card">
        <h2 className="mb-4 font-semibold">Recent orders</h2>
        <DataTable
          columns={[
            { key: 'order_number', label: 'Order #' },
            { key: 'status', label: 'Status' },
            { key: 'total', label: 'Total', render: (r) => `$${Number(r.total).toFixed(2)}` },
          ]}
          rows={recent}
          emptyMessage="No orders yet"
        />
      </div>
    </div>
  );
}
