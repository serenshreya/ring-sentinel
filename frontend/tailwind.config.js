/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sentinel: {
          dark: '#0f172a',
          card: '#1e293b',
          border: '#334155',
          primary: '#6366f1',
          accent: '#06b6d4',
          danger: '#ef4444',
          success: '#10b981',
          warning: '#f59e0b'
        }
      }
    },
  },
  plugins: [],
}
