/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            boxShadow: {
                'sharp': '0 2px 8px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)',
                'sharp-lg': '0 8px 24px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04)',
            },
        },
    },
    plugins: [],
}
