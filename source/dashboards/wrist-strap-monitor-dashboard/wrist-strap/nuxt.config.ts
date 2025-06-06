// nuxt.config.ts for wrist-strap-dashboard
export default defineNuxtConfig({
    compatibilityDate: '2025-05-27',
    devtools: {enabled: false},
    ssr: false,

    css: ['~/assets/css/main.css'],

    modules: [
        '@nuxt/ui',
        '@pinia/nuxt',
        '@nuxtjs/tailwindcss',
        '@nuxtjs/color-mode',
    ],

    tailwindcss: {
        exposeConfig: true
    },

    colorMode: {
        classSuffix: '',
        preference: 'dark',
        fallback: 'dark',
    },

    devServer: {
        port: 3001,
        host: '0.0.0.0',
        https: true // <--- ADD THIS LINE
    },

    // --- ADDED: Runtime Configuration for API Base URL ---
    runtimeConfig: {
        // Public keys are exposed to the client-side
        public: {
            apiBase: 'https://172.16.9.183:3003' // Your FastAPI backend API URL
        }
    },
    // --- END ADDED SECTION ---
})