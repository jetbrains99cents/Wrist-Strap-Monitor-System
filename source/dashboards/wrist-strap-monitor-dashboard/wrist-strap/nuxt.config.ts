// nuxt.config.ts for wrist-strap-dashboard
export default defineNuxtConfig({
    compatibilityDate: '2025-05-27',
    devtools: {enabled: false}, // Enabled here, which is fine
    ssr: false, // As per your setting

    css: ['~/assets/css/main.css'],

    modules: [
        '@nuxt/ui',             // Nuxt UI first
        '@nuxtjs/tailwindcss',
        '@nuxtjs/color-mode', // @nuxt/ui should handle this
    ],

    // Configuration for @nuxtjs/tailwindcss
    tailwindcss: {
        exposeConfig: true
    },

    // Configuration for @nuxtjs/color-mode (if needed explicitly, or configure via ui key)
    colorMode: {
        classSuffix: '',
        preference: 'dark', // Tries to use OS/browser setting first
        fallback: 'dark',
    },
    // Example of configuring colorMode fallback via @nuxt/ui
    // ui: {
    //   colorMode: {
    //     preference: 'light'
    //   }
    // },

    devServer: {
        port: 3001, // **** DIFFERENT PORT ****
        host: '0.0.0.0'
    },
    // No vite.server.allowedHosts needed here unless you also funnel this specific app
})