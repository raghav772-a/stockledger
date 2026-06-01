import {
  ArrowLeftRight,
  BarChart3,
  Home,
  Package,
  Settings,
  ShoppingCart,
  Users,
} from 'lucide-react';

const icons = {
  home: Home,
  items: Package,
  inventory: ArrowLeftRight,
  sales: ShoppingCart,
  contacts: Users,
  reports: BarChart3,
  settings: Settings,
};

const colors = {
  home: 'bg-violet-100 text-violet-700',
  items: 'bg-sky-100 text-sky-700',
  inventory: 'bg-indigo-100 text-indigo-700',
  sales: 'bg-emerald-100 text-emerald-700',
  contacts: 'bg-amber-100 text-amber-700',
  reports: 'bg-rose-100 text-rose-700',
  settings: 'bg-slate-100 text-slate-700',
};

export default function NavIcon({ name, size = 18 }) {
  const Icon = icons[name] || Package;
  return (
    <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-md ${colors[name] || colors.items}`}>
      <Icon size={size} strokeWidth={2} />
    </span>
  );
}
