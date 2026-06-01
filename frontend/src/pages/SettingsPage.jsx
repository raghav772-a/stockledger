import { useTheme } from '../context/ThemeContext';
import PageHeader from '../components/PageHeader';
import { APP_NAME } from '../config/branding';

export default function SettingsPage() {
  const { dark, toggle } = useTheme();

  return (
    <div className="space-y-6">
      <PageHeader title="Settings" subtitle={`Configure your ${APP_NAME} organization`} />
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card">
          <h2 className="font-semibold text-slate-900 dark:text-white">Organization</h2>
          <p className="mt-1 text-sm text-slate-500">Main warehouse · Default currency USD</p>
        </div>
        <div className="card">
          <h2 className="font-semibold">Appearance</h2>
          <p className="mt-2 text-sm text-slate-500">Switch between light and dark interface.</p>
          <button type="button" className="btn-secondary mt-4" onClick={toggle}>
            {dark ? 'Use light mode' : 'Use dark mode'}
          </button>
        </div>
      </div>
    </div>
  );
}
