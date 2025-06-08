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
        https: {
            key: './localhost+2-key.pem', // Path to your key file
            cert: './localhost+2.pem'     // Path to your cert file
        }
    },

    // --- ADDED: Runtime Configuration for API Base URL ---
    runtimeConfig: {
        // Public keys are exposed to the client-side
        public: {
            apiBase: 'https://172.16.9.183:3002',
            // --- ADD THIS NEW LINE ---
            // This will be true when you run `npm run dev` and false for `npm run build`
            loggingEnabled: process.env.NODE_ENV === 'development'
        }
    },
    // --- END ADDED SECTION ---
})