/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#060A14',
        card: '#0D1526',
        cardInner: '#111E35',
        accent: '#00D4FF',
        success: '#00FF9C',
        orange: '#FF6B35',
        fault: '#FF3B5C',
        warning: '#FFD166',
        muted: '#4A6080',
        lightText: '#E2E8F0',
        border: '#1A2E4A',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'monospace'],
        heading: ['Syne', 'sans-serif'],
      },
      animation: {
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
};
