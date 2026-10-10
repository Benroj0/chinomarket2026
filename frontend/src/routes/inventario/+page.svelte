<script>
	import { onMount } from 'svelte';
	import { inventoryApi, productsApi } from '$lib/api/client.js';
	import { showToast } from '$lib/toast.js';

	let movements = $state([]);
	let alerts = $state([]);
	let products = $state([]);
	let loading = $state(true);

	// Modales
	let showModal = $state(false);
	let movementType = $state('entrada');
	let isSubmitting = $state(false);

	let form = $state({
		product_id: null,
		quantity: 12,
		reference_document: '',
		reason: ''
	});

	onMount(async () => {
		await loadData();
	});

	async function loadData() {
		loading = true;
		try {
			const [movs, altList, prods] = await Promise.all([
				inventoryApi.listMovements(100),
				inventoryApi.getAlerts(),
				productsApi.list()
			]);
			movements = movs || [];
			alerts = altList || [];
			products = prods || [];
			if (products.length > 0 && !form.product_id) {
				form.product_id = products[0].id;
			}
		} catch (err) {
			showToast('Error cargando kárdex: ' + err.message, 'error');
		} finally {
			loading = false;
		}
	}

	function openMovementModal(type) {
		movementType = type;
		form = {
			product_id: products.length > 0 ? products[0].id : null,
			quantity: 12,
			reference_document: type === 'entrada' ? 'FAC-PROVEEDOR-' + Math.floor(1000 + Math.random() * 9000) : 'MERMA-' + Math.floor(100 + Math.random() * 900),
			reason: type === 'entrada' ? 'Reabastecimiento semanal de abarrotes' : 'Producto vencido o empaque roto'
		};
		showModal = true;
	}

	async function handleMovementSubmit(e) {
		e.preventDefault();
		if (!form.product_id) {
			showToast('Selecciona un producto', 'error');
			return;
		}
		if (Number(form.quantity) <= 0) {
			showToast('Ingresa una cantidad válida mayor a 0', 'error');
			return;
		}

		isSubmitting = true;
		try {
			await inventoryApi.registerMovement({
				product_id: Number(form.product_id),
				movement_type: movementType,
				quantity: Number(form.quantity),
				reference_document: form.reference_document,
				reason: form.reason
			});
			showToast(`Movimiento registrado en Kárdex.`, 'success');
			showModal = false;
			await loadData();
		} catch (err) {
			showToast(err.message, 'error');
		} finally {
			isSubmitting = false;
		}
	}

	const totalInventoryValue = $derived(
		products.reduce((acc, p) => acc + (p.current_stock * p.sale_price), 0)
	);
</script>

<div class="space-y-5">
	<!-- Encabezado -->
	<div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
		<div class="flex items-center gap-3">
			<span class="w-12 h-12 rounded-2xl bg-amber-100 text-amber-800 flex items-center justify-center text-2xl font-bold">
				📋
			</span>
			<div>
				<h1 class="text-xl font-black text-slate-900">Kárdex & Movimientos de Stock</h1>
				<p class="text-xs text-slate-500">Control de entradas de proveedores, salidas por ventas en mostrador y mermas</p>
			</div>
		</div>

		<div class="flex items-center gap-2 flex-wrap">
			<button
				onclick={() => openMovementModal('entrada')}
				class="px-4 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white transition flex items-center gap-1.5 shadow-sm active:scale-95 cursor-pointer"
			>
				<span>📥</span> Registrar Compra / Ingreso
			</button>
			<button
				onclick={() => openMovementModal('merma')}
				class="px-4 py-2.5 rounded-xl text-xs font-bold bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-300 transition flex items-center gap-1.5 active:scale-95 cursor-pointer"
			>
				<span>⚠️</span> Registrar Merma / Baja
			</button>
		</div>
	</div>

	<!-- Indicadores de Stock -->
	<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
		<div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-1">
			<span class="text-xs font-bold text-slate-500 uppercase">Valor en Mercadería</span>
			<p class="text-2xl font-black text-slate-900 font-mono">S/ {totalInventoryValue.toFixed(2)}</p>
			<span class="text-[11px] text-slate-500">Calculado a precio de venta</span>
		</div>

		<div class="bg-white rounded-2xl p-5 border border-amber-200 shadow-xs space-y-1 bg-amber-50/40">
			<span class="text-xs font-bold text-amber-800 uppercase">Por Reabastecer</span>
			<p class="text-2xl font-black text-amber-700 font-mono">{alerts.length} artículos</p>
			<span class="text-[11px] text-amber-700">Stock igual o menor al mínimo</span>
		</div>

		<div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-1">
			<span class="text-xs font-bold text-slate-500 uppercase">Historial de Kárdex</span>
			<p class="text-2xl font-black text-slate-900 font-mono">{movements.length} movimientos</p>
			<span class="text-[11px] text-slate-500">Trazabilidad de cada producto</span>
		</div>
	</div>

	<!-- Tabla del Kárdex -->
	<div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
		<div class="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
			<h2 class="text-xs font-black uppercase text-slate-700 flex items-center gap-2">
				<span>📑</span> Movimientos Registrados en Tienda
			</h2>
			<span class="text-xs text-slate-500 font-medium">Últimos {movements.length} registros</span>
		</div>

		{#if loading}
			<div class="p-12 text-center text-slate-400 text-sm font-medium">Cargando kárdex...</div>
		{:else if movements.length === 0}
			<div class="p-12 text-center text-slate-500 text-sm font-medium">
				Aún no hay movimientos registrados.
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full text-left text-xs">
					<thead class="bg-white text-slate-600 uppercase tracking-wider text-[11px] font-bold border-b border-slate-200">
						<tr>
							<th class="p-3.5">Fecha y Hora</th>
							<th class="p-3.5">Producto</th>
							<th class="p-3.5">Tipo de Movimiento</th>
							<th class="p-3.5">Cantidad</th>
							<th class="p-3.5">Stock Anterior</th>
							<th class="p-3.5">Stock Final</th>
							<th class="p-3.5">Referencia / Motivo</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-100 font-medium">
						{#each movements as mov}
							<tr class="hover:bg-slate-50/80 transition">
								<td class="p-3.5 text-slate-500 font-mono text-[11px]">
									{new Date(mov.created_at).toLocaleString('es-PE', { dateStyle: 'short', timeStyle: 'short' })}
								</td>
								<td class="p-3.5">
									<p class="font-bold text-slate-900 text-xs">{mov.product_name}</p>
									<span class="text-[10px] text-slate-400 font-mono">SKU: {mov.product_sku}</span>
								</td>
								<td class="p-3.5">
									{#if mov.movement_type === 'entrada'}
										<span class="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 text-[10px] font-black uppercase">
											📥 Entrada (Compra)
										</span>
									{:else if mov.movement_type === 'salida'}
										<span class="px-2.5 py-1 rounded-full bg-blue-100 text-blue-800 border border-blue-200 text-[10px] font-black uppercase">
											📤 Salida (Venta POS)
										</span>
									{:else if mov.movement_type === 'merma'}
										<span class="px-2.5 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-200 text-[10px] font-black uppercase">
											⚠️ Merma / Baja
										</span>
									{:else}
										<span class="px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 border border-amber-200 text-[10px] font-black uppercase">
											⚙️ Ajuste
										</span>
									{/if}
								</td>
								<td class="p-3.5 font-black font-mono text-sm {mov.movement_type === 'entrada' ? 'text-emerald-700' : 'text-slate-800'}">
									{mov.movement_type === 'entrada' ? '+' : '-'}{mov.quantity}
								</td>
								<td class="p-3.5 text-slate-500 font-mono">
									{mov.previous_stock}
								</td>
								<td class="p-3.5 font-black text-slate-900 font-mono">
									{mov.new_stock}
								</td>
								<td class="p-3.5">
									<p class="text-slate-800 font-mono text-[11px] font-semibold">{mov.reference_document || '-'}</p>
									<p class="text-[10px] text-slate-500 truncate max-w-xs">{mov.reason || 'Sin motivo'}</p>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>

<!-- Modal Entrada o Merma -->
{#if showModal}
	<div class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
		<div class="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 border border-slate-200 shadow-2xl animate-fade-in">
			<div class="flex items-center justify-between border-b border-slate-200 pb-3">
				<h3 class="text-base font-black text-slate-900 flex items-center gap-2">
					<span>{movementType === 'entrada' ? '📥' : '⚠️'}</span>
					{movementType === 'entrada' ? 'Registrar Compra de Mercadería' : 'Registrar Merma / Vencimiento'}
				</h3>
				<button onclick={() => (showModal = false)} class="text-slate-400 hover:text-slate-700">✕</button>
			</div>

			<form onsubmit={handleMovementSubmit} class="space-y-3.5 text-xs">
				<div class="space-y-1">
					<label for="inv-prod" class="font-bold text-slate-800">Producto *</label>
					<select
						id="inv-prod"
						required
						bind:value={form.product_id}
						class="w-full px-3 py-2.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-800 font-semibold focus:outline-none"
					>
						{#each products as p}
							<option value={p.id}>
								{p.name} (Stock: {p.current_stock} {p.unit})
							</option>
						{/each}
					</select>
				</div>

				<div class="space-y-1">
					<label for="inv-qty" class="font-bold text-slate-800">Cantidad ({movementType === 'entrada' ? '+' : '-'}) *</label>
					<input
						id="inv-qty"
						type="number"
						step="0.5"
						min="0.5"
						required
						bind:value={form.quantity}
						class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 text-lg font-black focus:outline-none"
					/>
				</div>

				<div class="space-y-1">
					<label for="inv-doc" class="font-bold text-slate-800">Guía / Factura de Proveedor</label>
					<input
						id="inv-doc"
						type="text"
						bind:value={form.reference_document}
						placeholder="Ej: FACT-ALICORP-1048, GUIA-984..."
						class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-800 font-mono focus:outline-none"
					/>
				</div>

				<div class="space-y-1">
					<label for="inv-reason" class="font-bold text-slate-800">Motivo / Proveedor</label>
					<input
						id="inv-reason"
						type="text"
						bind:value={form.reason}
						placeholder="Ej: Compra directa a distribuidora, rotura de empaque..."
						class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-800 focus:outline-none"
					/>
				</div>

				<div class="flex gap-2 pt-3 border-t border-slate-200">
					<button
						type="button"
						onclick={() => (showModal = false)}
						class="flex-1 py-2.5 rounded-xl font-bold bg-slate-100 hover:bg-slate-200 text-slate-700"
					>
						Cancelar
					</button>
					<button
						type="submit"
						disabled={isSubmitting}
						class="flex-1 py-2.5 rounded-xl font-black text-white transition disabled:opacity-50 {movementType === 'entrada' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-rose-600 hover:bg-rose-700'}"
					>
						{isSubmitting ? 'Registrando...' : 'Confirmar en Kárdex'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
