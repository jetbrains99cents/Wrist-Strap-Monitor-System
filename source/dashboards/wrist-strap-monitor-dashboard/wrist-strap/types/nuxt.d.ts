// file: types/nuxt.d.ts

import { $Fetch } from 'ofetch';

// Define the shape of the toast object's add method
interface Toast {
    add: (notification: {
        id?: string;
        title?: string;
        description?: string;
        icon?: string;
        color?: string;
        timeout?: number;
        actions?: any[];
        callbacks?: any;
    }) => void;
}

declare module '#app' {
    interface NuxtApp {
        $api: $Fetch
        $toast: Toast // ADD THIS
    }
}

declare module 'vue' {
    interface ComponentCustomProperties {
        $api: $Fetch
        $toast: Toast // ADD THIS
    }
}

export {}