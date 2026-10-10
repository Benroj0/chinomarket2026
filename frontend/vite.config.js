import tailwindcss from '@tailwindcss/vite';
import adapter from '@sveltejs/adapter-auto';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit({
			adapter: adapter()
		})
	],
	server: {
		allowedHosts: true,
		watch: {
			usePolling: true
		},
		proxy: {
			'/api': {
				target: process.env.BACKEND_URL || 'http://localhost:8002',
				changeOrigin: true
			}
		}
	},
	envPrefix: ['VITE_', 'PUBLIC_']
});
