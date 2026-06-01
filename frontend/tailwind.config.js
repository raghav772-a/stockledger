/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Zoho Puvi"', 'Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#eef6ff',
          100: '#d9ebff',
          200: '#bcdcff',
          500: '#2684ff',
          600: '#0b6bcb',
          700: '#0854a3',
          800: '#0a3d71',
          900: '#0c2d52',
        },
        surface: {
          DEFAULT: '#f4f6f9',
          card: '#ffffff',
          sidebar: '#ffffff',
          border: '#e4e8ee',
        },
      },
      boxShadow: {
        card: '0 1px 2px rgba(16, 24, 40, 0.06), 0 1px 3px rgba(16, 24, 40, 0.1)',
        nav: '0 1px 0 rgba(16, 24, 40, 0.08)',
      },
    },
  },
  plugins: [],
};
