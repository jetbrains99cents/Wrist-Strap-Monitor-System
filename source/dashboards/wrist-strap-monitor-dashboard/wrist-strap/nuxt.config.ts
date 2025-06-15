// nuxt.config.ts for wrist-strap-dashboard
import { LOG_STATUSES, EVENT_TYPES } from './config/constants'

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
            key: './localhost+2-key.pem',
            cert: './localhost+2.pem'
        }
    },

    runtimeConfig: {
        public: {
            apiBase: 'https://172.16.9.183:3002',
            loggingEnabled: process.env.NODE_ENV === 'development',

            // --- MODIFICATION: Create mutable copies using spread syntax (...) ---
            logStatuses: [...LOG_STATUSES],
            eventTypes: [...EVENT_TYPES],

            installationAreas: [
                "POL",
                "FLW",
                "CG",
                "OQC Lighting",
                "D Inspection",
                "Warehouse Z",
                "Logistics",
                "Packaging",
            ],

            statusColors: {
                "Connected": "green",
                "Voltage reading ok": "green",
                "Info": "blue",
                "Configured": "blue",
                "Reset": "blue",
                "System": "blue",
                "User action": "blue",
                "Warning": "yellow",
                "Voltage reading failed": "amber",
                "Error": "orange",
                "Disconnected": "red",
                "Critical": "red",
                "Fault": "red",
                "Unknown": "slate"
            }
        }
    },
})