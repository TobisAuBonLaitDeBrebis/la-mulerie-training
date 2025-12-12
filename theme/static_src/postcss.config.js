module.exports = {
  plugins: {
    "@tailwindcss/postcss": {},
    "postcss-simple-vars": {},
    "postcss-nested": {}
  },
  corePlugins: {
    preflight: false, // désactive certaines resets si besoin
  }
}