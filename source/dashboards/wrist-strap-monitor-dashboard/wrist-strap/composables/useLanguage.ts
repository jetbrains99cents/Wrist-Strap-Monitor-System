import { ref, readonly } from 'vue'

// Create a reactive variable for the selected language
// 'en' is the default value
const selectedLang = ref<'en' | 'vi'>('en')

export function useLanguage() {
    const setLanguage = (lang: 'en' | 'vi') => {
        selectedLang.value = lang
    }

    return {
        // Provide a readonly version of selectedLang to prevent direct modification outside the composable
        // Components should use setLanguage to change it.
        currentLanguage: readonly(selectedLang),
        setLanguage,
        // You can also expose selectedLang directly if you prefer mutable state from components,
        // but readonly is safer for global state.
        // selectedLang,
    }
}