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

export default function CustomersPage() {
  const { refreshAll } = useDataRefresh();
  const { user } = useAuth();
  const canEdit = !!user;
  const [data, setData] = useState({ items: [], total_pages: 1 });
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm();

  const load = useCallback(async () => {
    const result = await fetchData(
      api.get('/customers', { params: { page, search: search || undefined } })
    );
    setData(result);
  }, [page, search]);

  useEffect(() => {
    const t = setTimeout(() => {
      setSearch(searchInput);
      setPage(1);
    }, 400);
    return () => clearTimeout(t);
  }, [searchInput]);

  useEffect(() => {
    load().catch((e) => toast.error(getErrorMessage(e, 'Failed to load customers')));
  }, [load]);

  const onSubmit = async (form) => {
    try {
      const payload = {
        name: form.name.trim(),
        email: form.email.trim().toLowerCase(),
        phone: form.phone || null,
        address: form.address || null,
      };
      if (editing) {
        await api.patch(`/customers/${editing.id}`, payload);
      } else {
        await api.post('/customers', payload);
      }
      toast.success('Customer saved');
      setModalOpen(false);
      await load();
      refreshAll();
    } catch (e) {
      toast.error(getErrorMessage(e, 'Save failed'));
    }
  };

  const onDelete = async (id) => {
    if (!confirm('Delete this customer?')) return;
    try {
      await api.delete(`/customers/${id}`);
      toast.success('Deleted');
      await load();
      refreshAll();
    } catch (e) {
      toast.error(getErrorMessage(e, 'Delete failed'));
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="Customers"
        subtitle="Contacts for your sales orders"
        actions={
          <>
            <input
              className="input-field w-48 !py-1.5"
              placeholder="Search customers..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
            {canEdit && (
              <button
                type="button"
                className="btn-primary"
                onClick={() => {
                  setEditing(null);
                  reset({ name: '', email: '', phone: '', address: '' });
                  setModalOpen(true);
                }}
              >
                + New customer
              </button>
            )}
          </>
        }
      />
      <div className="card">
        <DataTable
          columns={[
            { key: 'name', label: 'Name' },
            { key: 'email', label: 'Email' },
            { key: 'phone', label: 'Phone' },
            {
              key: 'actions',
              label: '',
              render: (r) =>
                canEdit && (
                  <div className="flex gap-2">
                    <button
                      type="button"
                      className="text-brand-600 text-sm"
                      onClick={() => {
                        setEditing(r);
                        reset(r);
                        setModalOpen(true);
                      }}
                    >
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
          emptyMessage="No customers yet. Add a customer before creating orders."
        />
        <Pagination page={page} totalPages={data.total_pages} onPageChange={setPage} />
      </div>
      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Customer' : 'New Customer'}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <input className="input-field" placeholder="Full name *" {...register('name', { required: true })} />
          <input className="input-field" type="email" placeholder="Email *" {...register('email', { required: true })} />
          <input className="input-field" placeholder="Phone" {...register('phone')} />
          <textarea className="input-field" placeholder="Address" rows={2} {...register('address')} />
          <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
            Save customer
          </button>
        </form>
      </Modal>
    </div>
  );
}
