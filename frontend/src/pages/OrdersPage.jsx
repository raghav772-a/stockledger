import { useCallback, useEffect, useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import toast from 'react-hot-toast';
import api, { fetchData } from '../services/api';
import { useDataRefresh } from '../context/DataRefreshContext';
import { getErrorMessage } from '../utils/errors';
import DataTable from '../components/DataTable';
import Modal from '../components/Modal';
import Pagination from '../components/Pagination';
import PageHeader from '../components/PageHeader';

const STATUSES = ['pending', 'processing', 'shipped', 'delivered', 'cancelled'];

export default function OrdersPage() {
  const { refreshAll } = useDataRefresh();
  const [data, setData] = useState({ items: [], total_pages: 1, total: 0 });
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [page, setPage] = useState(1);
  const [createOpen, setCreateOpen] = useState(false);
  const [editOrder, setEditOrder] = useState(null);
  const [editNotes, setEditNotes] = useState('');
  const [editStatus, setEditStatus] = useState('pending');
  const [saving, setSaving] = useState(false);

  const { register, handleSubmit, control, reset, formState: { isSubmitting } } = useForm({
    defaultValues: { customer_id: '', tax_rate: 0, items: [{ product_id: '', quantity: 1 }] },
  });
  const { fields, append, remove } = useFieldArray({ control, name: 'items' });

  const load = useCallback(async () => {
    const result = await fetchData(api.get('/orders', { params: { page, page_size: 20 } }));
    setData(result);
  }, [page]);

  const loadFormData = useCallback(async () => {
    const [c, p] = await Promise.all([
      fetchData(api.get('/customers', { params: { page_size: 100 } })),
      fetchData(api.get('/products', { params: { page_size: 100 } })),
    ]);
    setCustomers(c.items || []);
    setProducts(p.items || []);
  }, []);

  useEffect(() => {
    load().catch((e) => toast.error(getErrorMessage(e, 'Failed to load orders')));
    loadFormData().catch(() => {});
  }, [load, loadFormData]);

  const openCreate = () => {
    if (!customers.length) {
      toast.error('Go to Customers and add at least one customer first');
      return;
    }
    if (!products.length) {
      toast.error('Go to Items and add at least one product with stock');
      return;
    }
    reset({
      customer_id: customers[0].id,
      tax_rate: 0,
      items: [{ product_id: products[0].id, quantity: 1 }],
    });
    setCreateOpen(true);
  };

  const onCreate = async (form) => {
    try {
      const items = form.items
        .filter((i) => i.product_id)
        .map((i) => ({ product_id: i.product_id, quantity: Number(i.quantity) }));
      if (!items.length) {
        toast.error('Select at least one product');
        return;
      }
      await api.post('/orders', {
        customer_id: form.customer_id,
        tax_rate: Number(form.tax_rate) || 0,
        notes: form.notes || null,
        items,
      });
      toast.success('Sales order created');
      setCreateOpen(false);
      await load();
      await loadFormData();
      refreshAll();
    } catch (e) {
      toast.error(getErrorMessage(e, 'Could not create order'));
    }
  };

  const openEdit = async (row) => {
    try {
      const full = await fetchData(api.get(`/orders/${row.id}`));
      setEditOrder(full);
      setEditNotes(full.notes || '');
      setEditStatus(full.status);
    } catch (e) {
      toast.error(getErrorMessage(e, 'Could not load order'));
    }
  };

  const saveEdit = async () => {
    if (!editOrder) return;
    setSaving(true);
    try {
      await api.patch(`/orders/${editOrder.id}`, { status: editStatus, notes: editNotes });
      toast.success('Order updated');
      setEditOrder(null);
      await load();
      await loadFormData();
      refreshAll();
    } catch (e) {
      toast.error(getErrorMessage(e, 'Could not update order'));
    } finally {
      setSaving(false);
    }
  };

  const quickStatus = async (id, status, previousStatus) => {
    try {
      await api.patch(`/orders/${id}/status`, { status });
      toast.success('Status updated');
      await load();
      await loadFormData();
      refreshAll();
    } catch (e) {
      toast.error(getErrorMessage(e, 'Update failed'));
      setData((prev) => ({
        ...prev,
        items: prev.items.map((o) => (o.id === id ? { ...o, status: previousStatus } : o)),
      }));
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="Sales orders"
        subtitle={`${data.total ?? 0} orders`}
        actions={
          <>
            <button type="button" className="btn-secondary" onClick={() => { load(); loadFormData(); }}>
              Refresh
            </button>
            <button type="button" className="btn-primary" onClick={openCreate}>
              + New sales order
            </button>
          </>
        }
      />

      <div className="card !p-0 overflow-hidden">
        <DataTable
          columns={[
            { key: 'order_number', label: 'Order #' },
            { key: 'customer', label: 'Customer', render: (r) => r.customer?.name || '—' },
            {
              key: 'status',
              label: 'Status',
              render: (r) => (
                <select
                  className="input-field !py-1 text-xs capitalize"
                  value={r.status}
                  onChange={(e) => quickStatus(r.id, e.target.value, r.status)}
                >
                  {STATUSES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              ),
            },
            { key: 'total', label: 'Total', render: (r) => `$${Number(r.total).toFixed(2)}` },
            {
              key: 'actions',
              label: '',
              render: (r) => (
                <button type="button" className="text-sm font-medium text-brand-600" onClick={() => openEdit(r)}>
                  View / Edit
                </button>
              ),
            },
          ]}
          rows={data.items}
          emptyMessage="No sales orders yet. Click + New sales order to create one."
        />
        <div className="border-t border-surface-border p-4 dark:border-slate-700">
          <Pagination page={page} totalPages={data.total_pages} onPageChange={setPage} />
        </div>
      </div>

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="New sales order" wide>
        <form onSubmit={handleSubmit(onCreate)} className="space-y-3">
          <div>
            <label className="mb-1 block text-xs font-semibold uppercase text-slate-500">Customer *</label>
            <select className="input-field" {...register('customer_id', { required: true })}>
              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.email})
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase text-slate-500">Tax rate</label>
              <input className="input-field" type="number" step="0.01" min="0" max="1" placeholder="0.08" {...register('tax_rate')} />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase text-slate-500">Notes</label>
              <input className="input-field" placeholder="Optional" {...register('notes')} />
            </div>
          </div>
          <p className="text-sm font-semibold text-slate-700">Line items *</p>
          {fields.map((field, index) => (
            <div key={field.id} className="flex gap-2">
              <select className="input-field flex-1" {...register(`items.${index}.product_id`, { required: true })}>
                <option value="">Select item</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id} disabled={p.quantity < 1}>
                    {p.name} — ${Number(p.price).toFixed(2)} (stock: {p.quantity})
                  </option>
                ))}
              </select>
              <input className="input-field w-24" type="number" min="1" {...register(`items.${index}.quantity`, { required: true, min: 1 })} />
              {fields.length > 1 && (
                <button type="button" className="text-red-500 px-2" onClick={() => remove(index)}>
                  ×
                </button>
              )}
            </div>
          ))}
          <button type="button" className="btn-secondary w-full" onClick={() => append({ product_id: '', quantity: 1 })}>
            + Add line item
          </button>
          <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
            {isSubmitting ? 'Creating...' : 'Save sales order'}
          </button>
        </form>
      </Modal>

      <Modal open={!!editOrder} onClose={() => setEditOrder(null)} title={editOrder ? `Order ${editOrder.order_number}` : ''} wide>
        {editOrder && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-slate-500">Customer</p>
                <p className="font-medium">{editOrder.customer?.name}</p>
              </div>
              <div>
                <p className="text-slate-500">Total</p>
                <p className="font-medium">${Number(editOrder.total).toFixed(2)}</p>
              </div>
            </div>
            <div>
              <p className="mb-2 text-sm font-semibold">Items</p>
              <ul className="rounded-md border border-surface-border divide-y text-sm dark:border-slate-700">
                {(editOrder.items || []).map((item) => (
                  <li key={item.id} className="flex justify-between px-3 py-2">
                    <span>{item.product?.name || item.product_id}</span>
                    <span>
                      {item.quantity} × ${Number(item.unit_price).toFixed(2)} = ${Number(item.line_total).toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase text-slate-500">Status</label>
              <select className="input-field capitalize" value={editStatus} onChange={(e) => setEditStatus(e.target.value)}>
                {STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase text-slate-500">Notes</label>
              <textarea className="input-field" rows={3} value={editNotes} onChange={(e) => setEditNotes(e.target.value)} />
            </div>
            <button type="button" className="btn-primary w-full" disabled={saving} onClick={saveEdit}>
              {saving ? 'Saving...' : 'Save changes'}
            </button>
          </div>
        )}
      </Modal>
    </div>
  );
}
