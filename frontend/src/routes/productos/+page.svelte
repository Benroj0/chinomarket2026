<script>
	import { onMount } from 'svelte';
	import { productsApi, categoriesApi } from '$lib/api/client.js';
	import { showToast } from '$lib/toast.js';

	let products = $state([]);
	let categories = $state([]);
	let loading = $state(true);

	// Filtros
	let searchQuery = $state('');
	let selectedCategory = $state(null);
	let onlyLowStock = $state(false);

	// Modal Crear / Editar
	let showModal = $state(false);
	let isEditing = $state(false);
	let editingId = $state(null);
	let isSubmitting = $state(false);

	let form = $state({
		category_id: null,
		name: '',
		sku: '',
		barcode: '',
		unit: 'und',
		cost_price: 0.0,
		sale_price: 0.0,
		current_stock: 12.0,
		min_stock: 5.0,
		expiration_date: ''
	});

	// Modal Reabastecer Rápido
	let showRestockModal = $state(false);
	let restockProduct = $state(null);
	let restockQuantity = $state(12);

	onMount(async () => {
		await loadData();
	});

	async function loadData() {
		loading = true;
		try {
			const [prods, cats] = await Promise.all([
				productsApi.list(),
				categoriesApi.list()
			]);
			products = prods || [];
			categories = cats || [];
			if (categories.length > 0 && !form.category_id) {
				form.category_id = categories[0].id;
			}
		} catch (e) {
			showToast('Error cargando inventario: ' + e.message, 'error');
		} finally {
			loading = false;
		}
	}

	const filteredProducts = $derived(
		products.filter((p) => {
			const matchesCat = !selectedCategory || p.category_id === selectedCategory;
			const matchesLow = !onlyLowStock || p.current_stock <= p.min_stock;
			const query = searchQuery.trim().toLowerCase();
			const matchesSearch =
				!query ||
				p.name.toLowerCase().includes(query) ||
				p.sku.toLowerCase().includes(query) ||
				(p.barcode && p.barcode.toLowerCase().includes(query));
			return matchesCat && matchesLow && matchesSearch;
		})
	);

	function openCreateModal() {
		isEditing = false;
		editingId = null;
		form = {
			category_id: categories.length > 0 ? categories[0].id : null,
			name: '',
			sku: 'PROD-' + Math.floor(100 + Math.random() * 900),
			barcode: '',
			unit: 'und',
			cost_price: 0.0,
			sale_price: 0.0,
			current_stock: 12.0,
			min_stock: 5.0,
			expiration_date: ''
		};
		showModal = true;
	}

	function openEditModal(prod) {
		isEditing = true;
		editingId = prod.id;
		form = {
			category_id: prod.category_id,
			name: prod.name,
			sku: prod.sku,
			barcode: prod.barcode || '',
			unit: prod.unit,
			cost_price: prod.cost_price,
			sale_price: prod.sale_price,
			current_stock: prod.current_stock,
			min_stock: prod.min_stock,
			expiration_date: prod.expiration_date || ''
		};
		showModal = true;
	}

	function openRestockModal(prod) {
		restockProduct = prod;
		restockQuantity = 12;
		showRestockModal = true;
	}

	async function handleSubmit(e) {
		e.preventDefault();
		if (!form.name.trim()) {
			showToast('Ingresa el nombre del producto', 'error');
			return;
		}
		if (!form.sale_price || Number(form.sale_price) <= 0) {
			showToast('El precio de venta debe ser mayor a 0', 'error');
			return;
		}

		isSubmitting = true;
		try {
			const payload = {
				category_id: Number(form.category_id),
				name: form.name.trim(),
				sku: form.sku.trim().toUpperCase(),
				barcode: form.barcode?.trim() || null,
				unit: form.unit,
				cost_price: Number(form.cost_price) || 0.0,
				sale_price: Number(form.sale_price),
				current_stock: Number(form.current_stock) || 0.0,
				min_stock: Number(form.min_stock) || 0.0,
				expiration_date: form.expiration_date || null
			};

			if (isEditing) {
				await productsApi.update(editingId, payload);
				showToast(`Producto '${form.name}' actualizado.`, 'success');
			} else {
				await productsApi.create(payload);
				showToast(`Producto '${form.name}' registrado en la tienda.`, 'success');
			}

			showModal = false;
			await loadData();
		} catch (err) {
			showToast(err.message, 'error');
		} finally {
			isSubmitting = false;
		}
	}

	async function submitRestock() {
		if (!restockProduct || Number(restockQuantity) <= 0) return;
		try {
			await productsApi.updateStock(restockProduct.id, Number(restockQuantity));
			showToast(`Se agregaron +${restockQuantity} unidades a '${restockProduct.name}'.`, 'success');
			showRestockModal = false;
			await loadData();
		} catch (err) {
			showToast('Error: ' + err.message, 'error');
		}
	}

	async function handleDelete(prod) {
		if (!confirm(`¿Deseas retirar el producto '${prod.name}' del catálogo activo?`)) return;
		try {
			await productsApi.delete(prod.id);
			showToast(`Producto retirado del catálogo.`, 'success');
			await loadData();
		} catch (err) {
			showToast('Error: ' + err.message, 'error');
		}
	}

	const profitMargin = $derived(
		form.sale_price > 0 && form.cost_price > 0
			? (((form.sale_price - form.cost_price) / form.sale_price) * 100).toFixed(1)
			: 0
	);
</script>

<div class="space-y-5">
	<!-- Encabezado -->
	<div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
		<div class="flex items-center gap-3">
			<span class="w-12 h-12 rounded-2xl bg-blue-100 text-blue-700 flex items-center justify-center text-2xl font-bold">
				📦
			</span>
			<div>
				<h1 class="text-xl font-black text-slate-900">Catálogo de Productos & Precios</h1>
				<p class="text-xs text-slate-500">Agrega mercadería, modifica precios de venta y controla el stock</p>
			</div>
		</div>

		<button
			onclick={openCreateModal}
			class="px-5 py-3 rounded-xl text-xs sm:text-sm font-black bg-emerald-600 hover:bg-emerald-700 text-white transition flex items-center gap-2 shadow-sm active:scale-95 cursor-pointer"
		>
			<span class="text-base font-bold">+</span> Registrar Nuevo Producto
		</button>
	</div>

	<!-- Filtros y Búsqueda -->
	<div class="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 text-xs">
		<div class="relative flex-1">
			<span class="absolute left-3.5 top-3 text-slate-400">🔍</span>
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Buscar por nombre, código de barras o SKU..."
				class="w-full pl-9 pr-3 py-2.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white"
			/>
		</div>

		<div class="flex items-center gap-2 flex-wrap">
			<select
				bind:value={selectedCategory}
				class="px-3 py-2.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-700 font-bold focus:outline-none"
			>
				<option value={null}>Todas las Categorías</option>
				{#each categories as cat}
					<option value={cat.id}>{cat.icon || '🏷️'} {cat.name}</option>
				{/each}
			</select>

			<button
				onclick={() => (onlyLowStock = !onlyLowStock)}
				class="px-3.5 py-2.5 rounded-xl font-bold transition flex items-center gap-1.5 border {onlyLowStock ? 'bg-amber-100 border-amber-300 text-amber-800' : 'bg-slate-50 border-slate-300 text-slate-600 hover:bg-slate-100'}"
			>
				<span>⚠️</span> Stock Bajo ({products.filter((p) => p.current_stock <= p.min_stock).length})
			</button>
		</div>
	</div>

	<!-- Tabla de Productos Limpia -->
	<div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
		{#if loading}
			<div class="p-12 text-center text-slate-400 text-sm font-medium">Cargando inventario...</div>
		{:else if filteredProducts.length === 0}
			<div class="p-12 text-center text-slate-500 text-sm space-y-3 font-medium">
				<p>No hay productos con los filtros seleccionados.</p>
				<button onclick={openCreateModal} class="text-xs font-bold text-emerald-700 underline">
					+ Registrar un nuevo producto ahora
				</button>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full text-left text-xs">
					<thead class="bg-slate-50 text-slate-600 uppercase tracking-wider text-[11px] font-bold border-b border-slate-200">
						<tr>
							<th class="p-4">Producto & Código</th>
							<th class="p-4">Categoría</th>
							<th class="p-4">Costo Compra</th>
							<th class="p-4">Precio Venta (Público)</th>
							<th class="p-4">Stock en Tienda</th>
							<th class="p-4 text-right">Opciones</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-100 font-medium">
						{#each filteredProducts as prod}
							<tr class="hover:bg-slate-50/80 transition">
								<td class="p-4">
									<p class="font-bold text-slate-900 text-sm">{prod.name}</p>
									<p class="text-[11px] text-slate-400 font-mono">
										SKU: {prod.sku} {prod.barcode ? `• Código: ${prod.barcode}` : ''}
									</p>
								</td>
								<td class="p-4">
									<span class="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-[11px] font-bold border border-slate-200">
										{prod.category_name || 'General'}
									</span>
								</td>
								<td class="p-4 text-slate-500 font-mono text-xs">
									S/ {prod.cost_price.toFixed(2)}
								</td>
								<td class="p-4 font-black text-emerald-700 font-mono text-sm">
									S/ {prod.sale_price.toFixed(2)}
								</td>
								<td class="p-4">
									<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl font-bold text-xs {prod.current_stock <= prod.min_stock ? 'bg-amber-100 text-amber-800 border border-amber-300' : 'bg-slate-100 text-slate-800'}">
										{#if prod.current_stock <= prod.min_stock}
											<span>⚠️</span>
										{/if}
										{prod.current_stock} {prod.unit}
									</span>
								</td>
								<td class="p-4 text-right">
									<div class="inline-flex items-center gap-1.5">
										<button
											onclick={() => openRestockModal(prod)}
											class="px-2.5 py-1.5 rounded-lg bg-emerald-50 text-emerald-800 hover:bg-emerald-100 border border-emerald-300 transition font-bold text-xs"
											title="Reabastecer stock rápido"
										>
											+ Stock
										</button>
										<button
											onclick={() => openEditModal(prod)}
											class="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
											title="Editar precio o datos"
										>
											✏️
										</button>
										<button
											onclick={() => handleDelete(prod)}
											class="p-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-600 transition"
											title="Desactivar producto"
										>
											🗑️
										</button>
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>

<!-- Modal Crear / Editar Producto -->
{#if showModal}
	<div class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
		<div class="bg-white rounded-3xl max-w-lg w-full p-6 space-y-4 border border-slate-200 shadow-2xl animate-fade-in">
			<div class="flex items-center justify-between border-b border-slate-200 pb-3">
				<h3 class="text-base font-black text-slate-900 flex items-center gap-2">
					<span>{isEditing ? '✏️' : '📦'}</span>
					{isEditing ? 'Editar Producto' : 'Registrar Nuevo Producto en Tienda'}
				</h3>
				<button onclick={() => (showModal = false)} class="text-slate-400 hover:text-slate-700 text-sm font-bold">✕</button>
			</div>

			<form onsubmit={handleSubmit} class="space-y-3.5 text-xs">
				<!-- Nombre -->
				<div class="space-y-1">
					<label for="p-name" class="font-bold text-slate-800">Nombre del Producto *</label>
					<input
						id="p-name"
						type="text"
						required
						bind:value={form.name}
						placeholder="Ej: Leche Gloria Azul 400g, Arroz Costeño 1kg, Coca Cola 1.5L..."
						class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white"
					/>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<div class="space-y-1">
						<label for="p-cat" class="font-bold text-slate-800">Categoría *</label>
						<select
							id="p-cat"
							required
							bind:value={form.category_id}
							class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-800 font-semibold focus:outline-none"
						>
							{#each categories as cat}
								<option value={cat.id}>{cat.icon || '🏷️'} {cat.name}</option>
							{/each}
						</select>
					</div>

					<div class="space-y-1">
						<label for="p-unit" class="font-bold text-slate-800">Unidad de Venta *</label>
						<select
							id="p-unit"
							bind:value={form.unit}
							class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-800 font-semibold focus:outline-none"
						>
							<option value="und">Unidad (und)</option>
							<option value="kg">Kilogramo (kg)</option>
							<option value="lt">Litro (lt)</option>
							<option value="paq">Paquete (paq)</option>
							<option value="lata">Lata (lata)</option>
							<option value="bol">Bolsa (bol)</option>
						</select>
					</div>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<div class="space-y-1">
						<label for="p-sku" class="font-bold text-slate-800">Código SKU *</label>
						<input
							id="p-sku"
							type="text"
							required
							bind:value={form.sku}
							placeholder="Ej: GLOR-001"
							class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-800 uppercase font-mono font-bold focus:outline-none"
						/>
					</div>

					<div class="space-y-1">
						<label for="p-barcode" class="font-bold text-slate-800">Código de Barras</label>
						<input
							id="p-barcode"
							type="text"
							bind:value={form.barcode}
							placeholder="Ej: 7750151000101"
							class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-800 font-mono focus:outline-none"
						/>
					</div>
				</div>

				<!-- Precios y Ganancia -->
				<div class="p-3.5 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-2">
					<div class="grid grid-cols-2 gap-3">
						<div class="space-y-1">
							<label for="p-cost" class="font-bold text-slate-700">Costo de Compra (S/)</label>
							<input
								id="p-cost"
								type="number"
								step="0.1"
								bind:value={form.cost_price}
								class="w-full px-3 py-1.5 rounded-lg bg-white border border-slate-300 font-bold font-mono text-slate-900 focus:outline-none"
							/>
						</div>
						<div class="space-y-1">
							<label for="p-sale" class="font-black text-emerald-900">Precio Venta Público (S/) *</label>
							<input
								id="p-sale"
								type="number"
								step="0.1"
								required
								bind:value={form.sale_price}
								class="w-full px-3 py-1.5 rounded-lg bg-white border border-emerald-300 font-black font-mono text-emerald-800 text-sm focus:outline-none"
							/>
						</div>
					</div>
					{#if profitMargin > 0}
						<p class="text-[11px] text-emerald-800 font-medium">
							Margen de ganancia: <strong class="font-black">{profitMargin}%</strong> (Ganas S/ {(form.sale_price - form.cost_price).toFixed(2)} por cada {form.unit})
						</p>
					{/if}
				</div>

				<!-- Stock -->
				<div class="grid grid-cols-2 gap-3">
					<div class="space-y-1">
						<label for="p-stock" class="font-bold text-slate-800">Stock Inicial</label>
						<input
							id="p-stock"
							type="number"
							step="0.5"
							bind:value={form.current_stock}
							class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-800 font-bold focus:outline-none"
						/>
					</div>
					<div class="space-y-1">
						<label for="p-min" class="font-bold text-amber-800">Alerta de Stock Mínimo</label>
						<input
							id="p-min"
							type="number"
							step="1"
							bind:value={form.min_stock}
							class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-800 font-bold focus:outline-none"
						/>
					</div>
				</div>

				<div class="flex gap-2 pt-3 border-t border-slate-200">
					<button
						type="button"
						onclick={() => (showModal = false)}
						class="flex-1 py-2.5 rounded-xl font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
					>
						Cancelar
					</button>
					<button
						type="submit"
						disabled={isSubmitting}
						class="flex-1 py-2.5 rounded-xl font-black bg-emerald-600 hover:bg-emerald-700 text-white transition disabled:opacity-50"
					>
						{isSubmitting ? 'Guardando...' : isEditing ? 'Guardar Cambios' : 'Registrar Producto'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- Modal Reabastecer Rápido -->
{#if showRestockModal && restockProduct}
	<div class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
		<div class="bg-white rounded-3xl max-w-sm w-full p-5 space-y-4 border border-slate-200 shadow-2xl animate-fade-in">
			<div class="space-y-1">
				<h3 class="text-sm font-black text-slate-900">📥 Agregar Stock</h3>
				<p class="text-xs font-bold text-emerald-700">{restockProduct.name}</p>
				<p class="text-[11px] text-slate-500">Stock actual en tienda: {restockProduct.current_stock} {restockProduct.unit}</p>
			</div>

			<div class="space-y-2 text-xs">
				<label for="r-qty" class="block font-bold text-slate-700">Cantidad recibida (+):</label>
				<input
					id="r-qty"
					type="number"
					step="1"
					min="1"
					bind:value={restockQuantity}
					class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 text-lg font-black focus:outline-none"
				/>
				<div class="flex gap-1.5 pt-1">
					<button onclick={() => (restockQuantity = 6)} class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold">+6</button>
					<button onclick={() => (restockQuantity = 12)} class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold">+12 (Docena)</button>
					<button onclick={() => (restockQuantity = 24)} class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold">+24 (Caja)</button>
				</div>
			</div>

			<div class="flex gap-2 pt-2 border-t border-slate-200">
				<button
					type="button"
					onclick={() => (showRestockModal = false)}
					class="flex-1 py-2 rounded-xl text-xs font-bold bg-slate-100 text-slate-700 hover:bg-slate-200"
				>
					Cancelar
				</button>
				<button
					type="button"
					onclick={submitRestock}
					class="flex-1 py-2 rounded-xl text-xs font-black bg-emerald-600 hover:bg-emerald-700 text-white"
				>
					Confirmar Ingreso
				</button>
			</div>
		</div>
	</div>
{/if}
