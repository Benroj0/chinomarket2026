<script>
	import { onMount } from 'svelte';
	import { dashboardApi, inventoryApi, salesApi } from '$lib/api/client.js';

	let stats = $state({
		total_products: 0,
		low_stock_alerts: 0,
		today_sales_count: 0,
		today_sales_total: 0.0,
		total_receivable_debt: 0.0
	});

	let lowStockProducts = $state([]);
	let recentSales = $state([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			const [sData, alerts, sales] = await Promise.all([
				dashboardApi.getStats(),
				inventoryApi.getAlerts(),
				salesApi.list()
			]);
			stats = sData;
			lowStockProducts = alerts || [];
			recentSales = (sales || []).slice(0, 5);
		} catch (e) {
			console.error('Error dashboard:', e);
		} finally {
			loading = false;
		}
	});

	const modules = [
		{
			title: 'Caja POS (Mostrador)',
			desc: 'Cobro rápido, lector de códigos, efectivo con cálculo de vuelto, Yape y fiados.',
			href: '/pos',
			icon: '⚡',
			color: 'emerald',
			badge: 'Caja Rápida'
		},
		{
			title: 'Catálogo de Productos',
			desc: 'Registra nuevos productos, cambia precios de venta y ajusta stock.',
			href: '/productos',
			icon: '📦',
			color: 'blue',
			badge: 'Mercadería'
		},
		{
			title: 'Kárdex & Control de Stock',
			desc: 'Registra compras a distribuidores, mermas por vencimiento y revisa el kárdex.',
			href: '/inventario',
			icon: '📋',
			color: 'amber',
			badge: 'Inventario'
		},
		{
			title: 'Ventas del Día & Arqueo',
			desc: 'Controla el dinero en caja, boletas emitidas y pagos por Yape/Plin.',
			href: '/ventas',
			icon: '🧾',
			color: 'purple',
			badge: 'Arqueo de Caja'
		},
		{
			title: 'Libro de Fiados',
			desc: 'Anota fiados a vecinos, controla límites de crédito y registra pagos de deuda.',
			href: '/clientes',
			icon: '👥',
			color: 'cyan',
			badge: 'Créditos'
		},
		{
			title: 'Categorías de la Tienda',
			desc: 'Lácteos, Granos, Bebidas, Limpieza, Snacks, Conservas y Panadería.',
			href: '/categorias',
			icon: '🏷️',
			color: 'rose',
			badge: 'Abarrotes'
		}
	];
</script>

<div class="space-y-6">
	<!-- Banner Principal de Bienvenida para el Bodeguero -->
	<div class="bg-white rounded-3xl p-6 sm:p-7 border border-slate-200 shadow-xs flex flex-col md:flex-row items-center justify-between gap-6">
		<div class="space-y-2 text-center md:text-left">
			<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
				<span>🏪</span> Tienda de Abarrotes Chino Market
			</span>
			<h1 class="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
				Panel de Control de la Bodega
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 max-w-xl">
				Administra las ventas del mostrador, mantén al día tus precios y controla el stock de tus productos de forma sencilla.
			</p>
		</div>

		<div class="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto">
			<a
				href="/pos"
				class="w-full sm:w-auto px-6 py-3.5 rounded-2xl text-sm font-black bg-emerald-600 hover:bg-emerald-700 text-white transition flex items-center justify-center gap-2 shadow-sm active:scale-95"
			>
				<span class="text-lg">⚡</span> Abrir Caja POS
			</a>
			<a
				href="/productos"
				class="w-full sm:w-auto px-5 py-3.5 rounded-2xl text-xs sm:text-sm font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 transition flex items-center justify-center gap-1.5 border border-slate-300"
			>
				<span>+</span> Registrar Producto
			</a>
		</div>
	</div>

	<!-- Indicadores Comerciales Claros -->
	<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
		<!-- Ventas de Hoy -->
		<div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-1">
			<div class="flex items-center justify-between">
				<span class="text-xs font-bold text-slate-500 uppercase">Ventas de Hoy</span>
				<span class="text-lg">💵</span>
			</div>
			<p class="text-2xl sm:text-3xl font-black text-emerald-700 font-mono">
				S/ {stats.today_sales_total.toFixed(2)}
			</p>
			<span class="text-xs text-slate-500 font-medium">{stats.today_sales_count} boletas cobradas</span>
		</div>

		<!-- Fiados por Cobrar -->
		<div class="bg-white rounded-2xl p-5 border border-rose-200 shadow-xs space-y-1 bg-rose-50/30">
			<div class="flex items-center justify-between">
				<span class="text-xs font-bold text-rose-700 uppercase">Fiados por Cobrar</span>
				<span class="text-lg">👥</span>
			</div>
			<p class="text-2xl sm:text-3xl font-black text-rose-600 font-mono">
				S/ {stats.total_receivable_debt.toFixed(2)}
			</p>
			<a href="/clientes" class="text-xs text-rose-700 font-bold hover:underline block">
				Ver libro de fiados →
			</a>
		</div>

		<!-- Alerta Stock Bajo -->
		<div class="bg-white rounded-2xl p-5 border border-amber-200 shadow-xs space-y-1 bg-amber-50/30">
			<div class="flex items-center justify-between">
				<span class="text-xs font-bold text-amber-800 uppercase">Stock Crítico</span>
				<span class="text-lg">⚠️</span>
			</div>
			<p class="text-2xl sm:text-3xl font-black text-amber-700 font-mono">
				{stats.low_stock_alerts}
			</p>
			<a href="/inventario" class="text-xs text-amber-800 font-bold hover:underline block">
				{stats.low_stock_alerts > 0 ? 'Reabastecer mercadería →' : 'Stock en orden'}
			</a>
		</div>

		<!-- Total Productos -->
		<div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-1">
			<div class="flex items-center justify-between">
				<span class="text-xs font-bold text-slate-500 uppercase">Productos Activos</span>
				<span class="text-lg">📦</span>
			</div>
			<p class="text-2xl sm:text-3xl font-black text-slate-900 font-mono">
				{stats.total_products}
			</p>
			<a href="/productos" class="text-xs text-slate-500 font-medium hover:underline block">
				Ver catálogo completo →
			</a>
		</div>
	</div>

	<!-- Paneles de Acción Rápida -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
		<!-- Alertas de Stock Bajo en la Tienda -->
		<div class="bg-white rounded-2xl border border-slate-200 shadow-xs p-5 space-y-3">
			<div class="flex items-center justify-between border-b border-slate-100 pb-3">
				<h2 class="text-sm font-black text-slate-900 flex items-center gap-2">
					<span class="text-amber-500">⚠️</span> Abarrotes con Poco Stock (Por Reabastecer)
				</h2>
				<a href="/inventario" class="text-xs font-bold text-amber-700 hover:underline">Ir a Kárdex →</a>
			</div>

			{#if lowStockProducts.length === 0}
				<p class="text-xs text-slate-400 py-6 text-center">✅ No hay productos con stock bajo en este momento.</p>
			{:else}
				<div class="space-y-2">
					{#each lowStockProducts as prod}
						<div class="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
							<div>
								<p class="text-xs font-bold text-slate-900">{prod.name}</p>
								<p class="text-[11px] text-slate-500 font-mono">Mínimo sugerido: {prod.min_stock} {prod.unit}</p>
							</div>
							<span class="px-2.5 py-1 rounded-lg bg-amber-100 text-amber-800 font-black text-xs font-mono">
								Quedan: {prod.current_stock} {prod.unit}
							</span>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Últimas Boletas Cobradas -->
		<div class="bg-white rounded-2xl border border-slate-200 shadow-xs p-5 space-y-3">
			<div class="flex items-center justify-between border-b border-slate-100 pb-3">
				<h2 class="text-sm font-black text-slate-900 flex items-center gap-2">
					<span class="text-emerald-600">🧾</span> Últimas Ventas en Mostrador
				</h2>
				<a href="/ventas" class="text-xs font-bold text-emerald-700 hover:underline">Ver todas →</a>
			</div>

			{#if recentSales.length === 0}
				<p class="text-xs text-slate-400 py-6 text-center">
					Aún no se han cobrado boletas. <a href="/pos" class="text-emerald-700 font-bold underline">¡Haz una venta en el POS!</a>
				</p>
			{:else}
				<div class="space-y-2">
					{#each recentSales as sale}
						<div class="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
							<div>
								<div class="flex items-center gap-2">
									<span class="text-xs font-black text-slate-900 font-mono">
										{sale.receipt_series}-{String(sale.receipt_number).padStart(6, '0')}
									</span>
									<span class="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-white text-slate-600 border border-slate-200">
										{sale.payment_method}
									</span>
								</div>
								<p class="text-[11px] text-slate-500">{sale.customer_name} • {sale.items?.length || 0} ítems</p>
							</div>
							<span class="text-sm font-black text-emerald-700 font-mono">
								S/ {sale.total.toFixed(2)}
							</span>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>

	<!-- Accesos a los Módulos de la Tienda -->
	<div class="space-y-3">
		<h2 class="text-base font-black text-slate-900">Módulos de la Tienda</h2>
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
			{#each modules as mod}
				<a
					href={mod.href}
					class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs hover:border-emerald-500 hover:shadow-md transition group flex flex-col justify-between gap-3"
				>
					<div class="space-y-1.5">
						<div class="flex items-center justify-between">
							<span class="text-2xl p-2 rounded-xl bg-slate-100">{mod.icon}</span>
							<span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
								{mod.badge}
							</span>
						</div>
						<h3 class="text-sm font-black text-slate-900 group-hover:text-emerald-700 transition">
							{mod.title}
						</h3>
						<p class="text-xs text-slate-500 leading-relaxed">{mod.desc}</p>
					</div>
					<span class="text-xs font-bold text-emerald-700 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
						Entrar →
					</span>
				</a>
			{/each}
		</div>
	</div>
</div>
