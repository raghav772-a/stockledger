import { NavLink } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { APP_NAME, APP_SHORT, NAV_GROUPS } from '../config/branding';
import { setSidebarOpen } from '../context/uiSlice';
import NavIcon from './NavIcon';

export default function Sidebar() {
  const dispatch = useDispatch();
  const open = useSelector((s) => s.ui.sidebarOpen);

  const closeMobile = () => {
    if (window.matchMedia('(max-width: 1023px)').matches) {
      dispatch(setSidebarOpen(false));
    }
  };

  return (
    <>
      {open && (
        <button
          type="button"
          className="fixed inset-0 z-20 bg-slate-900/40 lg:hidden"
          aria-label="Close menu"
          onClick={() => dispatch(setSidebarOpen(false))}
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-30 flex flex-col border-r border-surface-border bg-surface-sidebar shadow-nav transition-all duration-200 dark:border-slate-700 dark:bg-slate-900 ${
          open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        } ${open ? 'w-[240px]' : 'w-[240px] lg:w-[72px]'}`}
      >
        <div className="flex h-14 items-center gap-2 border-b border-surface-border px-3 dark:border-slate-700">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white">
            {APP_SHORT}
          </div>
          {open && (
            <div className="min-w-0">
              <p className="truncate text-sm font-bold text-slate-900 dark:text-white">{APP_NAME}</p>
              <p className="truncate text-[10px] font-medium uppercase tracking-wide text-slate-400">Inventory</p>
            </div>
          )}
        </div>

        <nav className="flex-1 overflow-y-auto px-2 py-2">
          {NAV_GROUPS.map((group) => (
            <div key={group.title}>
              {open && <p className="nav-section-title">{group.title}</p>}
              <ul className="space-y-0.5">
                {group.items.map(({ to, icon, label, end }) => (
                  <li key={to}>
                    <NavLink
                      to={to}
                      end={end}
                      title={label}
                      onClick={closeMobile}
                      className={({ isActive }) =>
                        `flex items-center gap-3 rounded-md px-2 py-2.5 text-sm font-medium transition-colors ${
                          isActive ? 'nav-item-active' : 'nav-item-idle'
                        }`
                      }
                    >
                      <NavIcon name={icon} />
                      {open && <span className="truncate">{label}</span>}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        {open && (
          <div className="border-t border-surface-border p-3 text-[11px] text-slate-400 dark:border-slate-700">
            © {new Date().getFullYear()} {APP_NAME}
          </div>
        )}
      </aside>
    </>
  );
}
