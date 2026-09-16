/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        mab: {
          bg: 'var(--mab-bg)',
          panel: 'var(--mab-panel)',
          border: 'var(--mab-border)',
          primary: 'var(--mab-primary)',
          accent: 'var(--mab-accent)',
          text: 'var(--mab-text)',
          muted: 'var(--mab-muted)',
        },
      },
    },
  },
  plugins: [],
};