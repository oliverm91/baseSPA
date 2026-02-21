/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./templates/**/*.html",
        "./listings/templates/**/*.html",
        "./users/templates/**/*.html",
        "./core/templates/**/*.html",
    ],
    theme: {
        extend: {
            colors: {
                'accent-color': '#e94560',
            },
        },
    },
    plugins: [],
}
