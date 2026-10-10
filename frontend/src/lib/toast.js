import { writable } from 'svelte/store';

export const toasts = writable([]);

export function showToast(message, type = 'success', duration = 3500) {
	const id = Date.now() + Math.random();
	toasts.update((current) => [...current, { id, message, type }]);

	setTimeout(() => {
		toasts.update((current) => current.filter((t) => t.id !== id));
	}, duration);
}
