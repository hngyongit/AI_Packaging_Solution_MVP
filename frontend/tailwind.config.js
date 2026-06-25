/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                pearl: {
                    50: '#fefdfb',
                    100: '#fdfbf8',
                    200: '#fcf8f0',
                    300: '#f5efe5',
                    400: '#e8dfd0',
                    500: '#d4c4b0',
                    600: '#b8a48a',
                    700: '#9a8568',
                    800: '#7d6b52',
                    900: '#5f5040',
                },
                carton: {
                    50: '#faf6f0',
                    100: '#f0eae0',
                    200: '#e0d5c0',
                    300: '#d0bfa0',
                    400: '#c0a880',
                    500: '#b89570',
                    600: '#a07d58',
                    700: '#8b6b45',
                    800: '#6b5535',
                    900: '#504028',
                },
            },
            boxShadow: {
                'flat': 'none',
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['Fira Code', 'monospace'],
            },
            borderRadius: {
                'none': '0px',
            },
        },
    },
    plugins: [],
}
