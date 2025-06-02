// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Sophisticated Graphite & Emerald Palette
        'dark-bg': '#161B22',          // Main page background (GitHub dark)
        'dark-surface': '#21262D',    // Cards, headers, footers (GitHub dark surface)
        'dark-border': '#30363D',       // Subtle borders (GitHub dark border)
        'dark-text-primary': '#E6EDF3', // Main text (GitHub dark primary text)
        'dark-text-secondary': '#7D8590',// Secondary text (GitHub dark secondary text)

        'nuxt-green': '#00DC82',         // Your vibrant accent
        'nuxt-green-darker': '#00A36A',  // Darker accent for borders/text
      },
      fontFamily: {
        abeezee: ['ABeeZee', 'sans-serif'],
        roboto: ['Roboto', 'sans-serif'],
        sans: ['Roboto', 'ABeeZee', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}