import { useCallback, useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import api, { fetchData } from '../services/api';
import { useDataRefresh } from '../context/DataRefreshContext';
import { getErrorMessage } from '../utils/errors';
import DataTable from '../components/DataTable';
import Modal from '../components/Modal';
import Pagination from '../components/Pagination';
import PageHeader from '../components/PageHeader';
import { useAuth } from '../context/AuthContext';

export default function ProductsPage() {
  const { refreshAll } = useDataRefresh();
  const { user } = useAuth();
  const canEdit = !!user;
  const [data, setData] = useState({ items: [], total_pages: 1, total: 0 });
  const [categories, setCategories] = useState([]);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [categoryModal, setCategoryModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm();
  const categoryForm = useForm();

  const loadCategories = useCallback(async () => {
    const cats = await fetchData(api.get('/categories'));
    setCategories(cats);
  }, []);

  const load = useCallback(async () => {
    const result = await fetchData(
      api.get('/products', { params: { page, search: search || undefined, page_size: 20 } })
    );
    setData(result);
  }, [page, search]);

  useEffect(() => {
    loadCategories().catch(() => {});
  }, [loadCategories]);

  useEffect(() => {
    const t = setTimeout(() => {
      setSearch(searchInput);
      setPage(1);
    }, 400);
    return () => clearTimeout(t);
  }, [searchInput]);

  useEffect(() => {
    load().catch((e) => toast.error(getErrorMessage(e, 'Failed to load products')));
  }, [load]);

  const openCreate = () => {
    setEditing(null);
    reset({
      name: '',
      sku: '',
      description: '',
      price: '',
      quantity: 0,
      low_stock_threshold: 10,
      category_id: '',
    });
    setModalOpen(true);
  };

  const openEdit = (row) => {
    setEditing(row);
    reset({
      ...row,
      category_id: row.category_id || '',
      price: row.price,
    });
    setModalOpen(true);
  };

  const onSubmit = async (form) => {
    try {
      const payload = {
        name: form.name.trim(),
        sku: form.sku.trim(),
        description: form.description?.trim() || null,
        price: Number(form.price),
        quantity: Number(form.quantity) || 0,
        low_stock_threshold: Number(form.low_stock_threshold) || 10,
        category_id: form.category_id && form.category_id !== '' ? form.category_id : null,
      };
      if (!payload.name || !payload.sku || payload.price <= 0) {
        toast.error('Name, SKU, and a price greater than 0 are required');
        return;
      }
      if (editing) {
        const { sku, ...rest } = payload;
        await api.patch(`/products/${editing.id}`, { ...rest, ...(form.sku?.trim() ? { sku } : {}) });
        toast.success('Item updated');
      } else {
        await api.post('/products', payload);
        toast.success('Item created');
      }
      setModalOpen(false);
      await load();
      refreshAll();
    } catch (e) {
      toast.error(getErrorMessage(e, 'Save failed'));
    }
  };

  const onDelete = async (id) => {
    if (!confirm('Delete this product?')) return;
    try {
      await api.delete(`/products/${id}`);
      toast.success('Deleted');
      await load();
      refreshAll();
    } catch (e) {
      toast.error(getErrorMessage(e, 'Delete failed'));
    }
  };

  const onAddCategory = async (form) => {
    try {
      await api.post('/categories', { name: form.name.trim(), description: form.description || null });
      toast.success('Category added');
      setCategoryModal(false);
      categoryForm.reset();
      loadCategories();
    } catch (e) {
      toast.error(getErrorMessage(e, 'Category failed'));
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="Items"
        subtitle={`${data.total ?? 0} items in catalog`}
        actions={
          <>
            <input
              className="input-field w-48 !py-1.5"
              placeholder="Search items..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
            {canEdit && (
              <>
                <button type="button" className="btn-secondary" onClick={() => setCategoryModal(true)}>
                  New category
                </button>
                <button type="button" className="btn-primary" onClick={openCreate}>
                  + New item
                </button>
              </>
            )}
          </>
        }
      />
      <div className="card">
        <DataTable
          columns={[
            { key: 'name', label: 'Name' },
            { key: 'sku', label: 'SKU' },
            {
              key: 'category',
              label: 'Category',
              render: (r) => r.category?.name || '—',
            },
            { key: 'price', label: 'Price', render: (r) => `$${Number(r.price).toFixed(2)}` },
            {
              key: 'quantity',
              label: 'Stock',
              render: (r) => (
                <span className={r.quantity <= r.low_stock_threshold ? 'font-medium text-amber-600' : ''}>
                  {r.quantity}
                </span>
              ),
            },
            {
              key: 'actions',
              label: '',
              render: (r) =>
                canEdit && (
                  <div className="flex gap-2">
                    <button type="button" className="text-brand-600 text-sm" onClick={() => openEdit(r)}>
                      Edit
                    </button>
                    <button type="button" className="text-red-500 text-sm" onClick={() => onDelete(r.id)}>
                      Delete
                    </button>
                  </div>
                ),
            },
          ]}
          rows={data.items}
          emptyMessage="No products yet. Click + Product to add your first item."
        />
        <Pagination page={page} totalPages={data.total_pages} onPageChange={setPage} />
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit item' : 'New item'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <input className="input-field" placeholder="Product name *" {...register('name', { required: true })} />
          <input className="input-field" placeholder="SKU *" {...register('sku', { required: true })} />
          <textarea className="input-field" placeholder="Description" rows={2} {...register('description')} />
          <select className="input-field" {...register('category_id')}>
            <option value="">No category</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          <div className="grid grid-cols-2 gap-3">
            <input
              className="input-field"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="Price *"
              {...register('price', { required: true })}
            />
            <input className="input-field" type="number" min="0" placeholder="Quantity" {...register('quantity')} />
          </div>
          <input
            className="input-field"
            type="number"
            min="0"
            placeholder="Low stock alert at"
            {...register('low_stock_threshold')}
          />
          <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : 'Save product'}
          </button>
        </form>
      </Modal>

      <Modal open={categoryModal} onClose={() => setCategoryModal(false)} title="New category">
        <form onSubmit={categoryForm.handleSubmit(onAddCategory)} className="space-y-3">
          <input className="input-field" placeholder="Category name" {...categoryForm.register('name', { required: true })} />
          <input className="input-field" placeholder="Description (optional)" {...categoryForm.register('description')} />
          <button type="submit" className="btn-primary w-full">
            Save category
          </button>
        </form>
      </Modal>
    </div>
  );
}
