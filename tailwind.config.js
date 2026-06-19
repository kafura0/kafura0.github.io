/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        teal: {
          50: '#e0f2f1', 100: '#b2dfdb', 200: '#80cbc4', 300: '#4db6ac',
          400: '#26a69a', 500: '#009688', 600: '#00897b', 700: '#00796b',
          800: '#00695c', 900: '#004d40',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
