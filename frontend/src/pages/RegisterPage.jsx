import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { APP_NAME } from '../config/branding';

export default function RegisterPage() {
  const { register: signup } = useAuth();
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { isSubmitting } } = useForm();

  const onSubmit = async (data) => {
    try {
      await signup(data);
      toast.success(`Welcome to ${APP_NAME}`);
      navigate('/');
    } catch (e) {
      toast.error(e.response?.data?.message || 'Registration failed');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface p-6">
      <div className="card w-full max-w-md !shadow-card">
        <div className="mb-6 flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 font-bold text-white">SL</div>
          <div>
            <h1 className="text-lg font-bold">Create your account</h1>
            <p className="text-xs text-slate-500">Start using {APP_NAME}</p>
          </div>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <input className="input-field" placeholder="Full name" {...register('full_name', { required: true })} />
          <input className="input-field" type="email" placeholder="Work email" {...register('email', { required: true })} />
          <input className="input-field" type="password" placeholder="Password (min 8 characters)" {...register('password', { required: true, minLength: 8 })} />
          <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
            Create account
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-slate-500">
          <Link to="/login" className="font-semibold text-brand-600 hover:underline">Back to sign in</Link>
        </p>
      </div>
    </div>
  );
}
