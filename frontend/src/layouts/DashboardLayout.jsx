import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import { useSelector } from 'react-redux';

export default function DashboardLayout() {
  const sidebarOpen = useSelector((s) => s.ui.sidebarOpen);

  return (
    <div className="min-h-screen bg-surface dark:bg-slate-950">
      <Sidebar />
      <div
        className={`flex min-h-screen flex-col transition-[margin] duration-200 ${
          sidebarOpen ? 'lg:ml-[240px]' : 'lg:ml-[72px]'
        }`}
      >
        <Navbar />
        <main className="flex-1 p-4 md:p-6 lg:p-8">
          <div className="mx-auto max-w-[1400px]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
