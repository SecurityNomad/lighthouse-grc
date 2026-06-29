/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'neu':         '6px 6px 14px #c5ccd6, -6px -6px 14px #ffffff',
        'neu-sm':      '4px 4px 8px  #c5ccd6, -4px -4px 8px  #ffffff',
        'neu-xs':      '2px 2px 5px  #c5ccd6, -2px -2px 5px  #ffffff',
        'neu-inset':   'inset 3px 3px 7px #c5ccd6, inset -3px -3px 7px #ffffff',
        'neu-inset-sm':'inset 2px 2px 5px #c5ccd6, inset -2px -2px 5px #ffffff',
        'neu-dark':         '6px 6px 14px #090d17, -6px -6px 14px #192236',
        'neu-dark-sm':      '4px 4px 8px  #090d17, -4px -4px 8px  #192236',
        'neu-dark-xs':      '2px 2px 5px  #090d17, -2px -2px 5px  #192236',
        'neu-dark-inset':   'inset 3px 3px 7px #090d17, inset -3px -3px 7px #192236',
        'neu-dark-inset-sm':'inset 2px 2px 5px #090d17, inset -2px -2px 5px #192236',
      },
      colors: {
        surface: {
          light: '#f1f5f9',
          dark:  '#0f172a',
        },
      },
      borderRadius: {
        '2.5xl': '20px',
      },
    },
  },
  plugins: [],
}
