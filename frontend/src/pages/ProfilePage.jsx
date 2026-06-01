import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import api, { fetchData } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { getErrorMessage } from '../utils/errors';
import PageHeader from '../components/PageHeader';
import { APP_NAME } from '../config/branding';

export default function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm({
    defaultValues: { full_name: '', email: '' },
  });

  useEffect(() => {
    if (user) {
      reset({ full_name: user.full_name || '', email: user.email || '' });
    }
  }, [user, reset]);

  const onProfile = async (data) => {
    try {
      await fetchData(api.patch('/auth/me', data));
      toast.success('Profile updated');
      await refreshUser();
    } catch (e) {
      toast.error(getErrorMessage(e, 'Could not update profile'));
    }
  };

  const onPassword = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      await api.post('/auth/change-password', {
        current_password: fd.get('current_password'),
        new_password: fd.get('new_password'),
      });
      toast.success('Password changed');
      e.target.reset();
    } catch (err) {
      toast.error(getErrorMessage(err, 'Could not change password'));
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <PageHeader title="My profile" subtitle={`Your ${APP_NAME} account`} />
      <div className="card">
        <form onSubmit={handleSubmit(onProfile)} className="space-y-3">
          <input className="input-field" {...register('full_name')} />
          <input className="input-field" type="email" {...register('email')} />
          <p className="text-sm text-slate-500">Role: {user?.role}</p>
          <button type="submit" className="btn-primary" disabled={isSubmitting}>
            Save profile
          </button>
        </form>
      </div>
      <div className="card">
        <h2 className="font-semibold">Change password</h2>
        <form onSubmit={onPassword} className="mt-3 space-y-3">
          <input className="input-field" type="password" name="current_password" placeholder="Current password" required />
          <input className="input-field" type="password" name="new_password" placeholder="New password" required minLength={8} />
          <button type="submit" className="btn-primary">Update password</button>
        </form>
      </div>
    </div>
  );
}
