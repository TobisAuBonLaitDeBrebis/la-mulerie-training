/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [

    '../**/*.js',
    '../**/*.py',
    // Templates within theme app (e.g. base.html)
    '../templates/**/*.html',
    // Templates in other apps
    '../../templates/**/*.html',
    // Ignore files in node_modules
    '!../../**/node_modules',
    // Include JavaScript files that might contain Tailwind CSS classes
    '../../**/*.js',
    // Include Python files that might contain Tailwind CSS classes
    '../../**/*.py'
  ],
  theme: {
    extend: {
      colors: {
        'muletier': '#1d1b18', // ton fond sombre
        'sable': '#edddc6',
        'orange': '#c25514',
        'terre': '#6c361e',
        'brique': '#a6432a',
        'blue': '#1fb6ff',
        'purple': '#7e5bef',
        'pink': '#ff49db',
        'orange-light': '#ff7849',
        'green': '#13ce66',
        'yellow': '#ffc82c',
        'gray-dark': '#273444',
        'gray': '#8492a6',
        'gray-light': '#d3dce6',
      },
      spacing: {
        '8xl': '96rem',
        '9xl': '128rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      fontFamily: {
        sans: ['Graphik', 'sans-serif'],
        serif: ['Merriweather', 'serif'],
      },
    },
  },
  plugins: [],
}
