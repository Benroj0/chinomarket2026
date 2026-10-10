<script>
	import { onMount } from 'svelte';
	import { salesApi } from '$lib/api/client.js';
	import { showToast } from '$lib/toast.js';

	let sales = $state([]);
	let loading = $state(true);

	// Modal Detalle
	let selectedSale = $state(null);
	let showDetailModal = $state(false);

	onMount(async () => {
		await loadSales();
	});

	async function loadSales() {
		loading = true;
		try {
			const data = await salesApi.list();
			sales = data || [];
		} catch (err) {
			showToast('Error cargando ventas: ' + err.message, 'error');
		} finally {
			loading = false;
		}
	}

	function viewSaleDetails(sale) {
		selectedSale = sale;
		showDetailModal = true;
	}

	const totalRevenue = $derived(sales.reduce((sum, s) => sum + s.total, 0));
	const cashTotal = $derived(
		sales.filter((s) => s.payment_method === 'efectivo').reduce((sum, s) => sum + s.total, 0)
	);
	const yapeTotal = $derived(
		sales.filter((s) => s.payment_method === 'yape' || s.payment_method === 'plin').reduce((sum, s) => sum + s.total, 0)
	);
	const cardTotal = $derived(
		sales.filter((s) => s.payment_method === 'tarjeta').reduce((sum, s) => sum + s.total, 0)
	);
	const creditTotal = $derived(
		sales.filter((s) => s.payment_method === 'credito').reduce((sum, s) => sum + s.total, 0)
	);
</script>

<div class="space-y-5">
	<!-- Encabezado -->
	<div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
		<div class="flex items-center gap-3">
			<span class="w-12 h-12 rounded-2xl bg-purple-100 text-purple-800 flex items-center justify-center text-2xl font-bold">
				🧾
			</span>
			<div>
				<h1 class="text-xl font-black text-slate-900">Historial de Ventas & Dinero en Caja</h1>
				<p class="text-xs text-slate-500">Comprobantes emitidos y balance del día desglosado por método de pago</p>
			</div>
		</div>

		<a
			href="/pos"
			class="px-5 py-2.5 rounded-xl text-xs font-black bg-emerald-600 hover:bg-emerald-700 text-white transition flex items-center gap-2 shadow-sm"
		>
			<span>⚡</span> Cobrar en POS
		</a>
	</div>

	<!-- Arqueo de Caja Diario -->
	<div class="grid grid-cols-2 lg:grid-cols-5 gap-3.5">
		<div class="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs space-y-1 col-span-2 lg:col-span-1">
			<span class="text-[11px] font-bold text-slate-500 uppercase">Total Vendido</span>
			<p class="text-2xl font-black text-slate-900 font-mono">S/ {totalRevenue.toFixed(2)}</p>
			<span class="text-[11px] text-slate-500">{sales.length} boletas</span>
		</div>

		<div class="bg-white rounded-2xl p-4 border border-emerald-200 shadow-xs space-y-1 bg-emerald-50/40">
			<span class="text-[11px] font-bold text-emerald-800 uppercase">💵 Efectivo en Caja</span>
			<p class="text-xl font-black text-emerald-700 font-mono">S/ {cashTotal.toFixed(2)}</p>
			<span class="text-[10px] text-emerald-600 font-medium">Billetes y monedas</span>
		</div>

		<div class="bg-white rounded-2xl p-4 border border-purple-200 shadow-xs space-y-1 bg-purple-50/40">
			<span class="text-[11px] font-bold text-purple-800 uppercase">🟣 Yape / Plin</span>
			<p class="text-xl font-black text-purple-700 font-mono">S/ {yapeTotal.toFixed(2)}</p>
			<span class="text-[10px] text-purple-600 font-medium">En cuenta bancaria</span>
		</div>

		<div class="bg-white rounded-2xl p-4 border border-blue-200 shadow-xs space-y-1 bg-blue-50/40">
			<span class="text-[11px] font-bold text-blue-800 uppercase">💳 Tarjetas</span>
			<p class="text-xl font-black text-blue-700 font-mono">S/ {cardTotal.toFixed(2)}</p>
			<span class="text-[10px] text-blue-600 font-medium">POS electrónico</span>
		</div>

		<div class="bg-white rounded-2xl p-4 border border-amber-200 shadow-xs space-y-1 bg-amber-50/40">
			<span class="text-[11px] font-bold text-amber-800 uppercase">📝 Fiados (Crédito)</span>
			<p class="text-xl font-black text-amber-700 font-mono">S/ {creditTotal.toFixed(2)}</p>
			<span class="text-[10px] text-amber-600 font-medium">Por cobrar a vecinos</span>
		</div>
	</div>

	<!-- Tabla de Comprobantes -->
	<div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
		<div class="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
			<h2 class="text-xs font-black uppercase text-slate-700 flex items-center gap-2">
				<span>📋</span> Registro de Boletas de Venta
			</h2>
			<span class="text-xs text-slate-500 font-medium">{sales.length} comprobantes emitidos</span>
		</div>

		{#if loading}
			<div class="p-12 text-center text-slate-400 text-sm font-medium">Cargando ventas...</div>
		{:else if sales.length === 0}
			<div class="p-12 text-center text-slate-500 text-sm space-y-3 font-medium">
				<p>Aún no se ha realizado ninguna venta hoy.</p>
				<a href="/pos" class="text-xs font-bold text-emerald-700 underline">
					Ir a la caja POS para cobrar →
				</a>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full text-left text-xs">
					<thead class="bg-white text-slate-600 uppercase tracking-wider text-[11px] font-bold border-b border-slate-200">
						<tr>
							<th class="p-4">Boleta</th>
							<th class="p-4">Fecha y Hora</th>
							<th class="p-4">Cliente</th>
							<th class="p-4">Forma de Pago</th>
							<th class="p-4">Productos</th>
							<th class="p-4">Total Cobrado</th>
							<th class="p-4 text-right">Opciones</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-100 font-medium">
						{#each sales as sale}
							<tr class="hover:bg-slate-50/80 transition">
								<td class="p-4 font-black font-mono text-emerald-700 text-sm">
									{sale.receipt_series}-{String(sale.receipt_number).padStart(6, '0')}
								</td>
								<td class="p-4 text-slate-500 font-mono text-[11px]">
									{new Date(sale.created_at).toLocaleString('es-PE', { dateStyle: 'short', timeStyle: 'short' })}
								</td>
								<td class="p-4 text-slate-800 font-bold">
									{sale.customer_name}
								</td>
								<td class="p-4">
									<span class="px-2.5 py-1 rounded-full text-[10px] font-black uppercase border {sale.payment_method === 'efectivo' ? 'bg-emerald-100 text-emerald-800 border-emerald-200' : sale.payment_method === 'yape' ? 'bg-purple-100 text-purple-800 border-purple-200' : sale.payment_method === 'credito' ? 'bg-amber-100 text-amber-800 border-amber-200' : 'bg-blue-100 text-blue-800 border-blue-200'}">
										{sale.payment_method}
									</span>
								</td>
								<td class="p-4 text-slate-500">
									{sale.items?.length || 0} ítems
								</td>
								<td class="p-4 font-black text-slate-900 font-mono text-sm">
									S/ {sale.total.toFixed(2)}
								</td>
								<td class="p-4 text-right">
									<button
										onclick={() => viewSaleDetails(sale)}
										class="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition border border-slate-200"
									>
										Ver Boleta 👁️
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>

<!-- Modal Detalle de Boleta -->
{#if showDetailModal && selectedSale}
	<div class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
		<div class="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 border border-slate-200 shadow-2xl animate-fade-in">
			<div class="flex items-center justify-between border-b border-slate-200 pb-3">
				<div>
					<h3 class="text-base font-black text-slate-900 flex items-center gap-2">
						<span>🧾</span> Boleta {selectedSale.receipt_series}-{String(selectedSale.receipt_number).padStart(6, '0')}
					</h3>
					<p class="text-[11px] text-slate-500">
						{new Date(selectedSale.created_at).toLocaleString('es-PE')}
					</p>
				</div>
				<button onclick={() => (showDetailModal = false)} class="text-slate-400 hover:text-slate-700">✕</button>
			</div>

			<div class="space-y-3 text-xs">
				<div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
					<p class="text-slate-500">Cliente: <strong class="text-slate-900">{selectedSale.customer_name}</strong></p>
					<p class="text-slate-500">Forma de Pago: <strong class="text-emerald-700 uppercase font-black">{selectedSale.payment_method}</strong></p>
					{#if selectedSale.cash_received}
						<p class="text-slate-500">Pagó con: <span class="font-bold text-slate-800">S/ {selectedSale.cash_received.toFixed(2)}</span></p>
					{/if}
					{#if selectedSale.cash_change > 0}
						<p class="text-amber-800 font-bold">Vuelto entregado: <span class="font-black">S/ {selectedSale.cash_change.toFixed(2)}</span></p>
					{/if}
				</div>

				<h4 class="font-black text-slate-800 pt-1">Productos Vendidos:</h4>
				<div class="max-h-48 overflow-y-auto space-y-1.5 divide-y divide-slate-100">
					{#each selectedSale.items || [] as item}
						<div class="pt-1.5 first:pt-0 flex items-center justify-between text-xs">
							<div>
								<p class="font-bold text-slate-900">{item.product_name}</p>
								<p class="text-[11px] text-slate-500 font-medium">
									{item.quantity} x S/ {item.unit_price.toFixed(2)}
								</p>
							</div>
							<span class="font-black text-slate-900 font-mono">
								S/ {item.subtotal.toFixed(2)}
							</span>
						</div>
					{/each}
				</div>

				<div class="pt-3 border-t border-slate-200 space-y-1 text-xs">
					<div class="flex justify-between text-slate-500">
						<span>Subtotal</span>
						<span>S/ {selectedSale.subtotal.toFixed(2)}</span>
					</div>
					<div class="flex justify-between text-slate-500">
						<span>IGV (18% incluido)</span>
						<span>S/ {selectedSale.tax.toFixed(2)}</span>
					</div>
					<div class="flex justify-between font-black text-base text-slate-900 pt-1">
						<span>TOTAL:</span>
						<span class="text-emerald-700">S/ {selectedSale.total.toFixed(2)}</span>
					</div>
				</div>
			</div>

			<div class="pt-2 flex gap-2">
				<button
					onclick={() => window.print()}
					class="flex-1 py-2.5 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300"
				>
					🖨️ Imprimir Ticket
				</button>
				<button
					onclick={() => (showDetailModal = false)}
					class="flex-1 py-2.5 rounded-xl text-xs font-black bg-slate-900 hover:bg-slate-800 text-white"
				>
					Cerrar
				</button>
			</div>
		</div>
	</div>
{/if}
