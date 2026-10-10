<script>
	import './layout.css';
	import { page } from '$app/state';
	import { toasts } from '$lib/toast.js';

	let { children } = $props();
	let mobileMenuOpen = $state(false);

	const navLinks = [
		{ href: '/pos', label: 'Caja POS', icon: '⚡', isPrimary: true },
		{ href: '/', label: 'Inicio', icon: '🏠' },
		{ href: '/productos', label: 'Productos', icon: '📦' },
		{ href: '/inventario', label: 'Kárdex & Stock', icon: '📋' },
		{ href: '/ventas', label: 'Ventas del Día', icon: '🧾' },
		{ href: '/clientes', label: 'Libro de Fiados', icon: '👥' },
		{ href: '/categorias', label: 'Categorías', icon: '🏷️' }
	];
</script>

<div class="min-h-screen flex flex-col bg-slate-100 text-slate-800">
	<!-- Barra Superior Comercial -->
	<header class="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-xs">
		<div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
			<!-- Marca de la Tienda de Abarrotes -->
			<a href="/" class="flex items-center gap-3 group">
				<div class="w-11 h-11 rounded-xl bg-emerald-600 text-white flex items-center justify-center text-2xl shadow-sm shadow-emerald-700/20 group-hover:scale-105 transition">
					🏪
				</div>
				<div>
					<div class="flex items-center gap-2">
						<span class="text-xl font-black text-slate-900 tracking-tight">Chino Market</span>
						<span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
							Bodega & Minimarket
						</span>
					</div>
					<p class="text-[11px] text-slate-500 font-medium">Punto de Venta & Control de Mercadería</p>
				</div>
			</a>

			<!-- Navegación de Puntos de Control -->
			<nav class="hidden lg:flex items-center gap-1.5 text-xs font-bold text-slate-600">
				{#each navLinks as link}
					{#if link.isPrimary}
						<a
							href={link.href}
							class="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white transition flex items-center gap-2 shadow-sm font-black text-sm tracking-wide mr-2 hover:scale-[1.02] active:scale-[0.98]"
						>
							<span class="text-base">{link.icon}</span>
							<span>{link.label}</span>
						</a>
					{:else}
						<a
							href={link.href}
							class="px-3 py-2 rounded-xl transition flex items-center gap-1.5 {page.url.pathname === link.href ? 'bg-slate-100 text-emerald-700 font-extrabold border border-slate-200' : 'hover:bg-slate-50 hover:text-slate-900 text-slate-600'}"
						>
							<span>{link.icon}</span>
							<span>{link.label}</span>
						</a>
					{/if}
				{/each}
			</nav>

			<!-- Botones Móvil -->
			<div class="flex items-center gap-2 lg:hidden">
				<a href="/pos" class="px-3.5 py-2 rounded-xl bg-emerald-600 text-white text-xs font-black flex items-center gap-1.5 shadow-sm">
					<span>⚡</span> Caja POS
				</a>
				<button
					onclick={() => (mobileMenuOpen = !mobileMenuOpen)}
					class="p-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200"
					aria-label="Menú"
				>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</button>
			</div>
		</div>

		<!-- Menú Móvil -->
		{#if mobileMenuOpen}
			<div class="lg:hidden border-t border-slate-200 bg-white px-4 py-3 space-y-1 shadow-md">
				{#each navLinks as link}
					<a
						href={link.href}
						onclick={() => (mobileMenuOpen = false)}
						class="block px-3 py-2.5 rounded-xl text-sm font-bold {page.url.pathname === link.href ? 'bg-emerald-50 text-emerald-800' : 'text-slate-700 hover:bg-slate-50'}"
					>
						<span class="mr-2">{link.icon}</span> {link.label}
					</a>
				{/each}
			</div>
		{/if}
	</header>

	<!-- Área de Trabajo -->
	<main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-7">
		{@render children()}
	</main>

	<!-- Pie de Página -->
	<footer class="bg-white border-t border-slate-200 py-5 text-center text-xs text-slate-500">
		<div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
			<span class="font-bold text-slate-700">🏪 Chino Market — Sistema Comercial de Abarrotes</span>
			<span>Atención de Mostrador, Kárdex de Stock y Libro de Fiados © 2026</span>
		</div>
	</footer>

	<!-- Notificaciones Flotantes -->
	<div class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm pointer-events-none">
		{#each $toasts as toast (toast.id)}
			<div
				class="pointer-events-auto px-4 py-3 rounded-xl shadow-lg text-xs font-bold flex items-center gap-3 border transition-all animate-bounce-once {toast.type === 'error' ? 'bg-rose-50 text-rose-800 border-rose-300' : 'bg-emerald-50 text-emerald-800 border-emerald-300'}"
			>
				<span class="text-base">{toast.type === 'error' ? '⚠️' : '✅'}</span>
				<span>{toast.message}</span>
			</div>
		{/each}
	</div>
</div>
