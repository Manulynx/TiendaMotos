/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js}"], // Ajusta esto a tu estructura de archivos
  theme: {
    extend: {
      colors: {
        // Tus variables de color convertidas
        'blue-dark': '#0F172A',
        'red-accent': '#C52233',
        'grey-bg': '#F8F9FA',
      },
      fontFamily: {
        // Tus variables de fuentes
        sans: ['Roboto', 'sans-serif'],      // Para el cuerpo (body)
        heading: ['Montserrat', 'sans-serif'], // Para h1-h3 y logo
      },
      // Definimos el padding del contenedor personalizado aquí si quieres estandarizarlo
      spacing: {
        'container-mobile': '1.5rem',
        'container-desktop': '5rem',
      }
    },
  },
  plugins: [],
}