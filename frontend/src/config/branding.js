export const APP_NAME = 'StockLedger';
export const APP_TAGLINE = 'Inventory & order management';
export const APP_SHORT = 'SL';

export const NAV_GROUPS = [
  {
    title: 'General',
    items: [{ to: '/', icon: 'home', label: 'Home', end: true }],
  },
  {
    title: 'Inventory',
    items: [
      { to: '/products', icon: 'items', label: 'Items' },
      { to: '/inventory', icon: 'inventory', label: 'Stock movements' },
    ],
  },
  {
    title: 'Sales',
    items: [{ to: '/orders', icon: 'sales', label: 'Sales Orders' }],
  },
  {
    title: 'Contacts',
    items: [{ to: '/customers', icon: 'contacts', label: 'Customers' }],
  },
  {
    title: 'Insights',
    items: [{ to: '/analytics', icon: 'reports', label: 'Reports' }],
  },
  {
    title: 'Setup',
    items: [{ to: '/settings', icon: 'settings', label: 'Settings' }],
  },
];
