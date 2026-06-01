import { Link } from 'react-router-dom';
import { Bell, LogOut, Menu, Search, User } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { toggleSidebar } from '../context/uiSlice';
import { useAuth } from '../context/AuthContext';
import { APP_NAME } from '../config/branding';
import { useState } from 'react';

export default function Navbar() {
  const dispatch = useDispatch();
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-surface-border bg-white px-4 shadow-nav dark:border-slate-700 dark:bg-slate-900">
      <button
        type="button"
        onClick={() => dispatch(toggleSidebar())}
        className="btn-ghost !p-2"
        aria-label="Toggle menu"
      >
        <Menu size={20} />
      </button>

      <div className="hidden min-w-0 flex-1 md:block">
        <p className="truncate text-sm font-semibold text-slate-800 dark:text-slate-100">{APP_NAME}</p>
        <p className="truncate text-xs text-slate-500">Organization · Main warehouse</p>
      </div>

      <div className="ml-auto flex max-w-md flex-1 items-center gap-2 md:ml-0 md:max-w-xs lg:max-w-sm">
        <div className="relative hidden w-full sm:block">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search in StockLedger..."
            className="input-field !py-1.5 !pl-9 text-xs"
            readOnly
          />
        </div>
        <button type="button" className="btn-ghost !p-2 text-slate-500" aria-label="Notifications">
          <Bell size={18} />
        </button>
        <div className="relative">
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex items-center gap-2 rounded-md border border-surface-border bg-slate-50 py-1 pl-1 pr-2 hover:bg-slate-100 dark:border-slate-600 dark:bg-slate-800"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-md bg-brand-600 text-xs font-bold text-white">
              {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
            </span>
            <span className="hidden max-w-[120px] truncate text-xs font-medium md:inline">{user?.full_name}</span>
          </button>
          {menuOpen && (
            <div className="absolute right-0 mt-2 w-52 rounded-lg border border-surface-border bg-white py-1 shadow-lg dark:border-slate-600 dark:bg-slate-800">
              <div className="border-b border-surface-border px-4 py-2 dark:border-slate-600">
                <p className="text-sm font-medium">{user?.full_name}</p>
                <p className="truncate text-xs text-slate-500">{user?.email}</p>
                <p className="mt-1 text-[10px] font-semibold uppercase text-brand-600">{user?.role}</p>
              </div>
              <Link
                to="/profile"
                className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-700"
                onClick={() => setMenuOpen(false)}
              >
                <User size={16} /> My profile
              </Link>
              <button
                type="button"
                onClick={logout}
                className="flex w-full items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-slate-50 dark:hover:bg-slate-700"
              >
                <LogOut size={16} /> Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
