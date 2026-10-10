<script>
	import { onMount } from 'svelte';
	import { productsApi, categoriesApi, customersApi, salesApi } from '$lib/api/client.js';
	import { showToast } from '$lib/toast.js';

	// Datos
	let products = $state([]);
	let categories = $state([]);
	let customers = $state([]);
	let loading = $state(true);

	// Filtros
	let searchQuery = $state('');
	let selectedCategory = $state(null);

	// Carrito de mostrador
	let cart = $state([]);
	let selectedCustomerId = $state(null);
	let paymentMethod = $state('efectivo');
	let cashReceived = $state('');
	let isProcessingSale = $state(false);

	// Modal Comprobante
	let lastSaleResult = $state(null);
	let showSuccessModal = $state(false);

	onMount(async () => {
		await loadData();
	});

	async function loadData() {
		loading = true;
		try {
			const [prods, cats, custs] = await Promise.all([
				productsApi.list(),
				categoriesApi.list(),
				customersApi.list()
			]);
			products = prods || [];
			categories = cats || [];
			customers = custs || [];
		} catch (err) {
			showToast('Error cargando catálogo: ' + err.message, 'error');
		} finally {
			loading = false;
		}
	}

	function getProductIcon(prod) {
		const n = (prod.name || '').toLowerCase();
		if (n.includes('leche')) return '🥛';
		if (n.includes('huevo')) return '🥚';
		if (n.includes('mantequilla')) return '🧈';
		if (n.includes('arroz')) return '🌾';
		if (n.includes('aceite')) return '🍾';
		if (n.includes('azúcar') || n.includes('azucar')) return '🍚';
		if (n.includes('fideo')) return '🍝';
		if (n.includes('inca') || n.includes('coca') || n.includes('gaseosa')) return '🥤';
		if (n.includes('agua')) return '💧';
		if (n.includes('detergente') || n.includes('jabón') || n.includes('jabon')) return '🧼';
		if (n.includes('papel')) return '🧻';
		if (n.includes('galleta')) return '🍪';
		if (n.includes('atún') || n.includes('atun')) return '🐟';
		if (n.includes('pan')) return '🥖';
		return '📦';
	}

	// Filtro en tiempo real
	const filteredProducts = $derived(
		products.filter((p) => {
			const matchesCat = !selectedCategory || p.category_id === selectedCategory;
			const query = searchQuery.trim().toLowerCase();
			if (!query) return matchesCat;
			const matchesSearch =
				p.name.toLowerCase().includes(query) ||
				p.sku.toLowerCase().includes(query) ||
				(p.barcode && p.barcode.toLowerCase().includes(query));
			return matchesCat && matchesSearch;
		})
	);

	// Cálculos
	const total = $derived(
		cart.reduce((sum, item) => sum + item.quantity * item.sale_price, 0)
	);
	const igv = $derived((total * 0.18) / 1.18);
	const cashChange = $derived(
		paymentMethod === 'efectivo' && Number(cashReceived) > total
			? Number(cashReceived) - total
			: 0
	);

	function addToCart(product) {
		if (product.current_stock <= 0) {
			showToast(`'${product.name}' está agotado`, 'error');
			return;
		}
		const existing = cart.find((item) => item.id === product.id);
		if (existing) {
			if (existing.quantity + 1 > product.current_stock) {
				showToast(`Solo quedan ${product.current_stock} ${product.unit} en bodega`, 'error');
				return;
			}
			existing.quantity += 1;
		} else {
			cart.push({ ...product, quantity: 1 });
		}
	}

	function updateQuantity(item, delta) {
		const newQty = item.quantity + delta;
		if (newQty <= 0) {
			removeFromCart(item.id);
		} else if (newQty > item.current_stock) {
			showToast(`Stock disponible: ${item.current_stock}`, 'error');
		} else {
			item.quantity = newQty;
		}
	}

	function removeFromCart(id) {
		cart = cart.filter((item) => item.id !== id);
	}

	function clearCart() {
		cart = [];
		cashReceived = '';
	}

	function setQuickCash(amount) {
		cashReceived = amount.toString();
	}

	async function processSale() {
		if (cart.length === 0) {
			showToast('Toca los productos para agregarlos al ticket antes de cobrar', 'error');
			return;
		}

		if (paymentMethod === 'efectivo' && cashReceived && Number(cashReceived) < total) {
			showToast('El dinero recibido es menor al total de la cuenta', 'error');
			return;
		}

		if (paymentMethod === 'credito' && !selectedCustomerId) {
			showToast('Selecciona a qué vecino se le anota el fiado', 'error');
			return;
		}

		isProcessingSale = true;
		try {
			const payload = {
				customer_id: selectedCustomerId ? Number(selectedCustomerId) : null,
				payment_method: paymentMethod,
				discount: 0,
				cash_received: paymentMethod === 'efectivo' && cashReceived ? Number(cashReceived) : null,
				items: cart.map((i) => ({
					product_id: i.id,
					quantity: i.quantity,
					unit_price: i.sale_price
				}))
			};

			const result = await salesApi.create(payload);
			const custObj = customers.find((c) => c.id === Number(selectedCustomerId));

			lastSaleResult = {
				...result,
				items: [...cart],
				total: total,
				cashReceived: cashReceived ? Number(cashReceived) : total,
				change: cashChange,
				customerName: custObj ? custObj.name : 'Público General (Mostrador)',
				date: new Date().toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
			};
			showSuccessModal = true;
			showToast(`¡Venta cobrada! Boleta ${result.receipt}`, 'success');
			clearCart();
			loadData();
		} catch (err) {
			showToast(err.message, 'error');
		} finally {
			isProcessingSale = false;
		}
	}
</script>

<div class="space-y-4">
	<!-- Franja de Ayuda Rápida para el Vendedor -->
	<div class="bg-emerald-600 text-white rounded-2xl p-4 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
		<div class="flex items-center gap-3">
			<span class="text-3xl p-1 bg-white/20 rounded-xl">🏪</span>
			<div>
				<h1 class="text-base sm:text-lg font-black tracking-tight">Caja Registradora — Mostrador de Bodega</h1>
				<p class="text-xs text-emerald-100 font-medium">Toca o haz clic en cualquier producto para agregarlo a la boleta y presiona COBRAR.</p>
			</div>
		</div>

		<div class="flex items-center gap-2">
			<a
				href="/productos"
				class="px-3.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition border border-white/20"
			>
				+ Agregar Producto
			</a>
			{#if cart.length > 0}
				<button
					onclick={clearCart}
					class="px-3.5 py-1.5 rounded-xl bg-rose-500 hover:bg-rose-600 text-white text-xs font-bold transition shadow-xs"
				>
					Borrar Ticket
				</button>
			{/if}
		</div>
	</div>

	<!-- Layout: Catálogo Visual de Abarrotes (Izquierda) + Boleta de Cobro (Derecha) -->
	<div class="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
		<!-- Catálogo con Botones Grandes e Iconos Claros -->
		<div class="lg:col-span-7 xl:col-span-8 space-y-4">
			<!-- Buscador Simple -->
			<div class="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs space-y-3">
				<div class="relative">
					<span class="absolute left-4 top-3.5 text-slate-400 text-lg">🔍</span>
					<input
						type="text"
						bind:value={searchQuery}
						placeholder="Buscar por nombre (leche, arroz, aceite, gaseosa...) o escanear código..."
						class="w-full pl-12 pr-4 py-3.5 rounded-xl bg-slate-50 border-2 border-slate-200 text-base font-bold text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-emerald-600 focus:bg-white transition"
					/>
				</div>

				<!-- Categorías de Bodega en Botones Grandes -->
				<div class="flex items-center gap-2 overflow-x-auto pb-1 text-xs no-scrollbar">
					<button
						onclick={() => (selectedCategory = null)}
						class="px-4 py-2.5 rounded-xl font-black whitespace-nowrap transition border-2 {selectedCategory === null ? 'bg-slate-900 text-white border-slate-900 shadow-xs' : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'}"
					>
						Todos los Productos ({products.length})
					</button>
					{#each categories as cat}
						<button
							onclick={() => (selectedCategory = cat.id)}
							class="px-4 py-2.5 rounded-xl font-bold whitespace-nowrap transition border-2 flex items-center gap-1.5 {selectedCategory === cat.id ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs font-black' : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'}"
						>
							<span class="text-base">{cat.icon || '🏷️'}</span>
							<span>{cat.name}</span>
						</button>
					{/each}
				</div>
			</div>

			<!-- Cuadrícula de Productos Estilo Bodega -->
			{#if loading}
				<div class="bg-white rounded-2xl p-12 text-center text-slate-400 font-bold border border-slate-200">
					Cargando productos de la tienda...
				</div>
			{:else if filteredProducts.length === 0}
				<div class="bg-white rounded-2xl p-12 text-center text-slate-500 font-medium border border-slate-200 space-y-2">
					<span class="text-4xl block">🔍</span>
					<p class="font-bold text-slate-800">No encontramos ningún producto con ese nombre.</p>
					<button onclick={() => (searchQuery = '')} class="text-xs font-bold text-emerald-700 underline">
						Mostrar todos los productos
					</button>
				</div>
			{:else}
				<div class="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-3.5">
					{#each filteredProducts as prod}
						{@const icon = getProductIcon(prod)}
						<button
							onclick={() => addToCart(prod)}
							disabled={prod.current_stock <= 0}
							class="bg-white rounded-2xl p-4 text-left border-2 border-slate-200 shadow-xs hover:border-emerald-600 hover:shadow-md active:scale-95 transition-all flex flex-col justify-between gap-3 group relative cursor-pointer {prod.current_stock <= 0 ? 'opacity-40 grayscale pointer-events-none' : ''}"
						>
							<div class="space-y-2">
								<div class="flex items-center justify-between">
									<span class="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-2xl group-hover:scale-110 transition">
										{icon}
									</span>
									<span class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-bold text-[10px]">
										{prod.unit}
									</span>
								</div>

								<h3 class="text-xs sm:text-sm font-black text-slate-900 group-hover:text-emerald-700 transition line-clamp-2 leading-tight">
									{prod.name}
								</h3>
							</div>

							<!-- Precio Grande y Stock -->
							<div class="pt-2 border-t border-slate-100 flex items-baseline justify-between">
								<div>
									<span class="text-xs text-slate-500 font-bold">S/</span>
									<span class="text-xl sm:text-2xl font-black text-emerald-600 tracking-tight font-mono">
										{prod.sale_price.toFixed(2)}
									</span>
								</div>
								<span class="text-[11px] font-bold {prod.current_stock <= prod.min_stock ? 'text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded font-black' : 'text-slate-400'}">
									Quedan: {prod.current_stock}
								</span>
							</div>
						</button>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Panel Derecho: La Boleta de Cobro / Carrito -->
		<div class="lg:col-span-5 xl:col-span-4 space-y-4 sticky top-20">
			<div class="bg-white rounded-2xl border-2 border-slate-300 shadow-md p-5 space-y-4">
				<!-- Título de la Boleta -->
				<div class="flex items-center justify-between border-b-2 border-slate-100 pb-3">
					<div class="flex items-center gap-2">
						<span class="text-2xl">🧾</span>
						<h2 class="text-base font-black text-slate-900">Boleta de Venta</h2>
					</div>
					<span class="text-xs font-black px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800">
						{cart.length} {cart.length === 1 ? 'producto' : 'productos'}
					</span>
				</div>

				<!-- Lista de Artículos Añadidos -->
				{#if cart.length === 0}
					<div class="py-12 text-center text-slate-400 space-y-2">
						<span class="text-5xl block">🛒</span>
						<p class="text-xs font-bold text-slate-600">No hay productos en la cuenta.</p>
						<p class="text-[11px] text-slate-400">Toca cualquier producto de la izquierda para agregarlo.</p>
					</div>
				{:else}
					<div class="max-h-60 overflow-y-auto space-y-2 pr-1 divide-y divide-slate-100">
						{#each cart as item}
							<div class="pt-2.5 first:pt-0 flex items-center justify-between gap-2">
								<div class="flex-1 min-w-0">
									<p class="font-black text-slate-900 text-xs truncate">{item.name}</p>
									<p class="text-[11px] text-slate-500 font-bold">
										S/ {item.sale_price.toFixed(2)} c/u
									</p>
								</div>

								<!-- Botones de Cantidad (+ / -) Grandes -->
								<div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-300">
									<button
										onclick={() => updateQuantity(item, -1)}
										class="w-7 h-7 flex items-center justify-center font-black text-slate-800 hover:bg-white rounded-lg transition text-sm cursor-pointer"
										aria-label="Restar"
									>
										-
									</button>
									<span class="w-6 text-center text-xs font-black text-slate-900">{item.quantity}</span>
									<button
										onclick={() => updateQuantity(item, 1)}
										class="w-7 h-7 flex items-center justify-center font-black text-slate-800 hover:bg-white rounded-lg transition text-sm cursor-pointer"
										aria-label="Sumar"
									>
										+
									</button>
								</div>

								<!-- Total Ítem -->
								<div class="text-right min-w-[65px]">
									<span class="text-xs font-black text-slate-900 font-mono">
										S/ {(item.quantity * item.sale_price).toFixed(2)}
									</span>
								</div>

								<button
									onclick={() => removeFromCart(item.id)}
									class="text-slate-400 hover:text-rose-600 p-1 text-sm transition cursor-pointer"
									title="Eliminar de la boleta"
								>
									🗑️
								</button>
							</div>
						{/each}
					</div>
				{/if}

				<!-- Selección de Cliente / Vecino para Fiado -->
				<div class="pt-3 border-t-2 border-slate-100 space-y-1">
					<label for="pos-cust" class="text-xs font-black text-slate-700 block">Cliente / Vecino:</label>
					<select
						id="pos-cust"
						bind:value={selectedCustomerId}
						class="w-full px-3 py-2.5 rounded-xl bg-slate-50 border-2 border-slate-200 text-xs font-bold text-slate-800 focus:outline-none focus:border-emerald-600"
					>
						<option value={null}>Público Mostrador (Venta Regular)</option>
						{#each customers as cust}
							<option value={cust.id}>
								{cust.name} {cust.current_debt > 0 ? `(Debe: S/ ${cust.current_debt.toFixed(2)})` : '• Al día'}
							</option>
						{/each}
					</select>
				</div>

				<!-- Forma de Cobro con Botones de Colores Vivos -->
				<div class="space-y-1.5">
					<span class="text-xs font-black text-slate-700 block">¿Cómo te van a pagar?:</span>
					<div class="grid grid-cols-4 gap-1.5 text-xs font-black">
						<button
							onclick={() => (paymentMethod = 'efectivo')}
							class="py-3 rounded-xl border-2 transition flex flex-col items-center gap-1 cursor-pointer {paymentMethod === 'efectivo' ? 'bg-emerald-600 border-emerald-600 text-white shadow-sm' : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'}"
						>
							<span class="text-base">💵</span>
							<span>Efectivo</span>
						</button>
						<button
							onclick={() => (paymentMethod = 'yape')}
							class="py-3 rounded-xl border-2 transition flex flex-col items-center gap-1 cursor-pointer {paymentMethod === 'yape' ? 'bg-purple-600 border-purple-600 text-white shadow-sm' : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'}"
						>
							<span class="text-base">🟣</span>
							<span>Yape/Plin</span>
						</button>
						<button
							onclick={() => (paymentMethod = 'tarjeta')}
							class="py-3 rounded-xl border-2 transition flex flex-col items-center gap-1 cursor-pointer {paymentMethod === 'tarjeta' ? 'bg-blue-600 border-blue-600 text-white shadow-sm' : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'}"
						>
							<span class="text-base">💳</span>
							<span>Tarjeta</span>
						</button>
						<button
							onclick={() => (paymentMethod = 'credito')}
							class="py-3 rounded-xl border-2 transition flex flex-col items-center gap-1 cursor-pointer {paymentMethod === 'credito' ? 'bg-amber-500 border-amber-500 text-white shadow-sm' : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'}"
						>
							<span class="text-base">📝</span>
							<span>Fiado</span>
						</button>
					</div>
				</div>

				<!-- Calculador de Vuelto para Efectivo -->
				{#if paymentMethod === 'efectivo'}
					<div class="bg-emerald-50 border-2 border-emerald-300 rounded-2xl p-3.5 space-y-2">
						<div class="flex items-center justify-between text-xs font-black text-emerald-900">
							<span>Paga con billete de:</span>
							<input
								type="number"
								step="1"
								bind:value={cashReceived}
								placeholder={`S/ ${total.toFixed(2)}`}
								class="w-28 text-right px-2.5 py-1.5 rounded-xl bg-white border-2 border-emerald-400 text-sm font-black text-emerald-900 focus:outline-none font-mono"
							/>
						</div>

						<!-- Billetes Rápidos -->
						<div class="flex items-center gap-1.5 text-xs font-bold pt-1">
							<span class="text-[10px] text-emerald-800 font-extrabold">Rápido:</span>
							<button onclick={() => setQuickCash(total)} class="px-2 py-1 rounded-lg bg-white border border-emerald-300 text-emerald-900 hover:bg-emerald-100 text-[11px] font-black">Exacto</button>
							<button onclick={() => setQuickCash(10)} class="px-2 py-1 rounded-lg bg-white border border-emerald-300 text-emerald-900 hover:bg-emerald-100 text-[11px] font-black">S/ 10</button>
							<button onclick={() => setQuickCash(20)} class="px-2 py-1 rounded-lg bg-white border border-emerald-300 text-emerald-900 hover:bg-emerald-100 text-[11px] font-black">S/ 20</button>
							<button onclick={() => setQuickCash(50)} class="px-2 py-1 rounded-lg bg-white border border-emerald-300 text-emerald-900 hover:bg-emerald-100 text-[11px] font-black">S/ 50</button>
							<button onclick={() => setQuickCash(100)} class="px-2 py-1 rounded-lg bg-white border border-emerald-300 text-emerald-900 hover:bg-emerald-100 text-[11px] font-black">S/ 100</button>
						</div>

						{#if cashChange > 0}
							<div class="flex items-center justify-between pt-2 border-t-2 border-emerald-200">
								<span class="text-xs font-black text-amber-900 uppercase">Vuelto a entregar:</span>
								<span class="text-xl font-black text-amber-800 font-mono">S/ {cashChange.toFixed(2)}</span>
							</div>
						{/if}
					</div>
				{/if}

				<!-- Total Grande y Destacado -->
				<div class="bg-slate-900 rounded-2xl p-4 text-white flex items-center justify-between shadow-xs">
					<div>
						<span class="text-[11px] uppercase tracking-wider text-slate-300 font-black block">TOTAL A COBRAR</span>
						<span class="text-[10px] text-slate-400">IGV 18% incluido: S/ {igv.toFixed(2)}</span>
					</div>
					<div class="text-right">
						<span class="text-3xl font-black text-emerald-400 font-mono tracking-tight">
							S/ {total.toFixed(2)}
						</span>
					</div>
				</div>

				<!-- Botón Principal Gigante de Cobro -->
				<button
					onclick={processSale}
					disabled={cart.length === 0 || isProcessingSale}
					class="w-full py-4 rounded-2xl text-lg font-black bg-emerald-600 hover:bg-emerald-700 disabled:opacity-30 text-white transition shadow-lg shadow-emerald-700/20 active:scale-98 flex items-center justify-center gap-2 cursor-pointer"
				>
					{#if isProcessingSale}
						<span>⏳ Guardando boleta...</span>
					{:else}
						<span>🟢 COBRAR (S/ {total.toFixed(2)})</span>
					{/if}
				</button>
			</div>
		</div>
	</div>
</div>

<!-- Modal Comprobante Emitido -->
{#if showSuccessModal && lastSaleResult}
	<div class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
		<div class="bg-white rounded-3xl max-w-sm w-full p-6 space-y-4 border border-slate-200 shadow-2xl text-center animate-fade-in">
			<div class="w-16 h-16 rounded-full bg-emerald-100 text-emerald-700 mx-auto flex items-center justify-center text-3xl font-black">
				✓
			</div>
			<div>
				<h3 class="text-xl font-black text-slate-900">¡Venta Exitosa!</h3>
				<p class="text-xs font-black text-emerald-700 font-mono">Boleta: {lastSaleResult.receipt}</p>
				<p class="text-[11px] text-slate-500 font-semibold">{lastSaleResult.customerName} • {lastSaleResult.date}</p>
			</div>

			<!-- Ticket Estilo Térmico -->
			<div class="bg-slate-50 p-4 rounded-2xl border border-slate-200 text-left text-xs space-y-2 font-mono">
				<div class="text-center pb-2 border-b border-dashed border-slate-300">
					<p class="font-black text-slate-900 text-sm">🏪 CHINO MARKET</p>
					<p class="text-[10px] text-slate-500">Bodega & Minimarket</p>
					<p class="text-[10px] text-slate-500">RUC: 20601234567 • Morales, San Martín</p>
				</div>
				<div class="space-y-1 py-1">
					{#each lastSaleResult.items as item}
						<div class="flex justify-between text-[11px] text-slate-800">
							<span class="truncate max-w-[160px]">{item.name} (x{item.quantity})</span>
							<span class="font-bold">S/ {(item.quantity * item.sale_price).toFixed(2)}</span>
						</div>
					{/each}
				</div>
				<div class="border-t border-dashed border-slate-300 pt-2 space-y-1 text-xs">
					<div class="flex justify-between font-black text-slate-900 text-sm">
						<span>TOTAL PAGADO:</span>
						<span class="text-emerald-700">S/ {lastSaleResult.total.toFixed(2)}</span>
					</div>
					{#if lastSaleResult.change > 0}
						<div class="flex justify-between text-amber-800 font-bold">
							<span>VUELTO:</span>
							<span>S/ {lastSaleResult.change.toFixed(2)}</span>
						</div>
					{/if}
				</div>
			</div>

			<div class="flex gap-2 pt-1">
				<button
					onclick={() => window.print()}
					class="flex-1 py-3 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 transition border border-slate-300"
				>
					🖨️ Imprimir
				</button>
				<button
					onclick={() => (showSuccessModal = false)}
					class="flex-1 py-3 rounded-xl text-xs font-black bg-emerald-600 hover:bg-emerald-700 text-white transition shadow-sm"
				>
					Siguiente Venta →
				</button>
			</div>
		</div>
	</div>
{/if}
