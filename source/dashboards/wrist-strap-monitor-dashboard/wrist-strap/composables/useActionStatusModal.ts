import { reactive } from 'vue';

// Define the shape of the modal's state
const state = reactive({
    isOpen: false,
    title: '',
    description: '',
    icon: '',
    color: 'text-primary',
    countdown: 5,
});

let countdownInterval: ReturnType<typeof setInterval> | null = null;

export const useActionStatusModal = () => {
    const show = (options: {
        title: string;
        description: string;
        icon: string;
        color?: string;
        duration?: number;
        onComplete: () => void;
    }) => {
        // Set the modal's content from the provided options
        state.title = options.title;
        state.description = options.description;
        state.icon = options.icon;
        state.color = options.color || 'text-primary';
        state.countdown = options.duration || 5;
        state.isOpen = true;

        // Clear any previous countdowns
        if (countdownInterval) clearInterval(countdownInterval);

        // Start the new countdown
        countdownInterval = setInterval(() => {
            state.countdown--;
            if (state.countdown <= 0) {
                if (countdownInterval) clearInterval(countdownInterval);
                state.isOpen = false;
                // Run the provided callback function when the timer finishes
                options.onComplete();
            }
        }, 1000);
    };

    return { state, show };
};