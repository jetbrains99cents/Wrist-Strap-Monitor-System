// file: types/nuxt.d.ts

import { $Fetch } from 'ofetch';

declare module '#app' {
    interface NuxtApp {
        $api: $Fetch
    }
}

declare module 'vue' {
    interface ComponentCustomProperties {
        $api: $Fetch
    }
}

export {}