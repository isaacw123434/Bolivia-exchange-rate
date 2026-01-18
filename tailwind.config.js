/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./template.html", "./js/**/*.js"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "primary": "#17b0cf",
        "background-light": "#f6f8f8",
        "background-dark": "#111e21",
        "card-light": "#ffffff",
        "card-dark": "#1a2c30",
        "success": "#4CAF50",
        "warning": "#FFD23F",
        "danger": "#EF4444",
        "method-cash": "#42A5F5",
        "method-app": "#A07EDD",
        "method-card": "#8CC63F",
      },
      fontFamily: {
        "display": ["Plus Jakarta Sans", "sans-serif"]
      },
      borderRadius: {"DEFAULT": "0.5rem", "lg": "1rem", "xl": "1.5rem", "full": "9999px"},
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(0, 0, 0, 0.05)',
        'glow': '0 0 15px rgba(23, 176, 207, 0.3)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries'),
  ],
}
