/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./App.tsx",
    "./index.tsx",
  ],
  theme: {
    extend: {
      colors: {
        'sky-blue': '#40A7E3',
        'nature-green': '#27AE60',
        'pure-white': '#FFFFFF',
        'alert-red': '#EB5757',
        'text-dark': '#1F2937',
        'text-body': '#4B5563',
        'bg-color': '#F3F4F6',
        'stroke': '#E5E7EB',
      },
      borderRadius: {
        'card': '20px',
        'btn': '12px',
      },
    },
  },
  plugins: [],
}
