import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { APP_NAME, APP_TAGLINE } from '../config/branding';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const onSubmit = async (data) => {
    try {
      await login(data.email, data.password);
      toast.success(`Welcome to ${APP_NAME}`);
      navigate('/');
    } catch (e) {
      toast.error(e.response?.data?.message || 'Sign in failed');
    }
  };

  return (
    <div className="flex min-h-screen">
      <div className="hidden w-1/2 flex-col justify-between bg-gradient-to-br from-brand-800 via-brand-700 to-brand-600 p-12 text-white lg:flex">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-white/20 text-lg font-bold">SL</div>
          <span className="text-xl font-bold">{APP_NAME}</span>
        </div>
        <div>
          <h2 className="text-3xl font-bold leading-tight">Manage inventory like a pro</h2>
          <p className="mt-3 max-w-md text-brand-100">{APP_TAGLINE}. Track items, sales orders, customers, and reports in one place.</p>
          <ul className="mt-8 space-y-3 text-sm text-brand-50">
            <li>• Real-time stock & low-stock alerts</li>
            <li>• Sales orders with automatic stock deduction</li>
            <li>• Customer & revenue insights</li>
          </ul>
        </div>
        <p className="text-xs text-brand-200">Trusted for small business inventory operations</p>
      </div>
      <div className="flex flex-1 items-center justify-center bg-surface p-6">
        <div className="w-full max-w-md">
          <div className="mb-8 lg:hidden">
            <div className="flex items-center gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 font-bold text-white">SL</div>
              <span className="text-lg font-bold text-slate-900">{APP_NAME}</span>
            </div>
          </div>
          <div className="card !shadow-card">
            <h1 className="text-xl font-semibold text-slate-900">Sign in</h1>
            <p className="mt-1 text-sm text-slate-500">Access your {APP_NAME} organization</p>
            <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
              <div>
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Email</label>
                <input className="input-field" type="email" placeholder="you@company.com" {...register('email', { required: 'Required' })} />
                {errors.email && <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>}
              </div>
              <div>
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Password</label>
                <input className="input-field" type="password" {...register('password', { required: 'Required' })} />
              </div>
              <button type="submit" className="btn-primary w-full !py-2.5" disabled={isSubmitting}>
                {isSubmitting ? 'Signing in...' : 'Sign in'}
              </button>
            </form>
            <p className="mt-5 text-center text-sm text-slate-500">
              New organization? <Link to="/register" className="font-semibold text-brand-600 hover:underline">Create account</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
