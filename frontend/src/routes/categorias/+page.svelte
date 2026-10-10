<script>
	import { onMount } from 'svelte';
	import { categoriesApi, productsApi } from '$lib/api/client.js';
	import { showToast } from '$lib/toast.js';

	let categories = $state([]);
	let products = $state([]);
	let loading = $state(true);

	// Modal Crear Categoría
	let showModal = $state(false);
	let isSubmitting = $state(false);

	let form = $state({
		name: '',
		code: '',
		icon: '📦',
		color: 'emerald',
		description: ''
	});

	onMount(async () => {
		await loadData();
	});

	async function loadData() {
		loading = true;
		try {
			const [cats, prods] = await Promise.all([
				categoriesApi.list(),
				productsApi.list()
			]);
			categories = cats || [];
			products = prods || [];
		} catch (err) {
			showToast('Error cargando categorías: ' + err.message, 'error');
		} finally {
			loading = false;
		}
	}

	function getProductCount(catId) {
		return products.filter((p) => p.category_id === catId).length;
	}

	function openCreateModal() {
		form = {
			name: '',
			code: '',
			icon: '🏷️',
			color: 'emerald',
			description: ''
		};
		showModal = true;
	}

	async function handleSubmit(e) {
		e.preventDefault();
		if (!form.name.trim() || !form.code.trim()) {
			showToast('Nombre y código de categoría son obligatorios', 'error');
			return;
		}

		isSubmitting = true;
		try {
			await categoriesApi.create({
				name: form.name.trim(),
				code: form.code.trim().toUpperCase(),
				icon: form.icon,
				color: form.color,
				description: form.description.trim()
			});
			showToast(`Categoría '${form.name}' creada.`, 'success');
			showModal = false;
			await loadData();
		} catch (err) {
			showToast(err.message, 'error');
		} finally {
			isSubmitting = false;
		}
	}

	async function handleDelete(cat) {
		if (getProductCount(cat.id) > 0) {
			showToast(`No puedes eliminar '${cat.name}' porque contiene productos registrados.`, 'error');
			return;
		}
		if (!confirm(`¿Eliminar la categoría '${cat.name}'?`)) return;

		try {
			await categoriesApi.delete(cat.id);
			showToast(`Categoría eliminada.`, 'success');
			await loadData();
		} catch (err) {
			showToast('Error: ' + err.message, 'error');
		}
	}
</script>

<div class="space-y-5">
	<!-- Encabezado -->
	<div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
		<div class="flex items-center gap-3">
			<span class="w-12 h-12 rounded-2xl bg-rose-100 text-rose-800 flex items-center justify-center text-2xl font-bold">
				🏷️
			</span>
			<div>
				<h1 class="text-xl font-black text-slate-900">Categorías de la Tienda de Abarrotes</h1>
				<p class="text-xs text-slate-500">Agrupación de artículos para una rápida búsqueda y cobro en la caja POS</p>
			</div>
		</div>

		<button
			onclick={openCreateModal}
			class="px-5 py-2.5 rounded-xl text-xs font-black bg-rose-600 hover:bg-rose-700 text-white transition flex items-center gap-1.5 shadow-sm active:scale-95 cursor-pointer"
		>
			<span>+</span> Nueva Categoría
		</button>
	</div>

	<!-- Grid de Categorías -->
	{#if loading}
		<div class="p-12 text-center text-slate-400 text-sm font-medium">Cargando categorías...</div>
	{:else}
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
			{#each categories as cat}
				{@const count = getProductCount(cat.id)}
				<div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs hover:border-emerald-500 hover:shadow-md transition flex flex-col justify-between gap-3">
					<div class="space-y-2">
						<div class="flex items-center justify-between">
							<span class="text-3xl p-2.5 rounded-2xl bg-slate-50 border border-slate-200">{cat.icon || '📦'}</span>
							<span class="text-[10px] font-bold font-mono px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
								{cat.code}
							</span>
						</div>
						<div>
							<h3 class="text-base font-black text-slate-900">{cat.name}</h3>
							<p class="text-xs text-slate-500 line-clamp-2 leading-relaxed pt-1">
								{cat.description || 'Artículos esenciales de la bodega'}
							</p>
						</div>
					</div>

					<div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
						<span class="font-bold text-slate-700">
							{count} {count === 1 ? 'producto' : 'productos'}
						</span>
						<div class="flex items-center gap-2">
							<a
								href="/productos"
								class="text-xs text-emerald-700 hover:underline font-bold"
							>
								Ver en catálogo →
							</a>
							{#if count === 0}
								<button
									onclick={() => handleDelete(cat)}
									class="text-slate-400 hover:text-rose-600 text-sm p-1"
									title="Eliminar"
								>
									🗑️
								</button>
							{/if}
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Modal Crear Categoría -->
{#if showModal}
	<div class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
		<div class="bg-white rounded-3xl max-w-sm w-full p-6 space-y-4 border border-slate-200 shadow-2xl animate-fade-in">
			<div class="flex items-center justify-between border-b border-slate-200 pb-3">
				<h3 class="text-base font-black text-slate-900 flex items-center gap-2">
					<span>🏷️</span> Nueva Categoría de Abarrotes
				</h3>
				<button onclick={() => (showModal = false)} class="text-slate-400 hover:text-slate-700">✕</button>
			</div>

			<form onsubmit={handleSubmit} class="space-y-3 text-xs">
				<div class="space-y-1">
					<label for="c-name" class="font-bold text-slate-800">Nombre de la Categoría *</label>
					<input
						id="c-name"
						type="text"
						required
						bind:value={form.name}
						placeholder="Ej: Lácteos, Granos, Bebidas, Aseo..."
						class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 font-semibold focus:outline-none"
					/>
				</div>

				<div class="grid grid-cols-2 gap-2">
					<div class="space-y-1">
						<label for="c-code" class="font-bold text-slate-800">Código Corto *</label>
						<input
							id="c-code"
							type="text"
							required
							bind:value={form.code}
							placeholder="Ej: LAC, ABA, BEB"
							class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 font-mono text-slate-900 uppercase font-bold focus:outline-none"
						/>
					</div>

					<div class="space-y-1">
						<label for="c-icon" class="font-bold text-slate-800">Emoji / Icono</label>
						<input
							id="c-icon"
							type="text"
							bind:value={form.icon}
							placeholder="🥛, 🌾, 🥤, 🧼..."
							class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-center text-lg focus:outline-none"
						/>
					</div>
				</div>

				<div class="space-y-1">
					<label for="c-desc" class="font-bold text-slate-800">Descripción</label>
					<textarea
						id="c-desc"
						rows="2"
						bind:value={form.description}
						placeholder="Descripción de los productos que van en esta sección..."
						class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none"
					></textarea>
				</div>

				<div class="flex gap-2 pt-2 border-t border-slate-200">
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
						class="flex-1 py-2.5 rounded-xl font-black bg-rose-600 hover:bg-rose-700 text-white disabled:opacity-50"
					>
						{isSubmitting ? 'Guardando...' : 'Crear Categoría'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
