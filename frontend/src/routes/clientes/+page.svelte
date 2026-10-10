<script>
	import { onMount } from 'svelte';
	import { customersApi } from '$lib/api/client.js';
	import { showToast } from '$lib/toast.js';

	let customers = $state([]);
	let loading = $state(true);

	// Modal Cobrar Abono
	let showPayModal = $state(false);
	let selectedCustomer = $state(null);
	let paymentAmount = $state('');
	let isSubmittingPay = $state(false);

	// Modal Nuevo Cliente
	let showCreateModal = $state(false);
	let isSubmittingCustomer = $state(false);
	let customerForm = $state({
		name: '',
		document_number: '',
		phone: '',
		credit_limit: 150.0,
		customer_type: 'regular'
	});

	onMount(async () => {
		await loadCustomers();
	});

	async function loadCustomers() {
		loading = true;
		try {
			const data = await customersApi.list();
			customers = data || [];
		} catch (err) {
			showToast('Error cargando clientes: ' + err.message, 'error');
		} finally {
			loading = false;
		}
	}

	function openPayModal(cust) {
		selectedCustomer = cust;
		paymentAmount = cust.current_debt.toString();
		showPayModal = true;
	}

	async function handlePaySubmit(e) {
		e.preventDefault();
		const amount = Number(paymentAmount);
		if (!amount || amount <= 0) {
			showToast('Ingresa un monto válido a pagar', 'error');
			return;
		}

		isSubmittingPay = true;
		try {
			await customersApi.payDebt(selectedCustomer.id, {
				amount: amount,
				notes: 'Abono en efectivo en mostrador'
			});
			showToast(`Abono de S/ ${amount.toFixed(2)} registrado para ${selectedCustomer.name}.`, 'success');
			showPayModal = false;
			await loadCustomers();
		} catch (err) {
			showToast(err.message, 'error');
		} finally {
			isSubmittingPay = false;
		}
	}

	function openCreateModal() {
		customerForm = {
			name: '',
			document_number: '',
			phone: '',
			credit_limit: 150.0,
			customer_type: 'regular'
		};
		showCreateModal = true;
	}

	async function handleCreateSubmit(e) {
		e.preventDefault();
		if (!customerForm.name.trim()) {
			showToast('El nombre del vecino es obligatorio', 'error');
			return;
		}

		isSubmittingCustomer = true;
		try {
			await customersApi.create({
				name: customerForm.name.trim(),
				document_type: 'DNI',
				document_number: customerForm.document_number?.trim() || null,
				phone: customerForm.phone?.trim() || null,
				credit_limit: Number(customerForm.credit_limit) || 100.0,
				customer_type: customerForm.customer_type
			});
			showToast(`Cliente '${customerForm.name}' agregado al libro de fiados.`, 'success');
			showCreateModal = false;
			await loadCustomers();
		} catch (err) {
			showToast(err.message, 'error');
		} finally {
			isSubmittingCustomer = false;
		}
	}

	const totalDebt = $derived(customers.reduce((acc, c) => acc + c.current_debt, 0));
	const debtorCount = $derived(customers.filter((c) => c.current_debt > 0).length);
</script>

<div class="space-y-5">
	<!-- Encabezado -->
	<div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
		<div class="flex items-center gap-3">
			<span class="w-12 h-12 rounded-2xl bg-cyan-100 text-cyan-800 flex items-center justify-center text-2xl font-bold">
				👥
			</span>
			<div>
				<h1 class="text-xl font-black text-slate-900">Libro de Fiados & Clientes de la Bodega</h1>
				<p class="text-xs text-slate-500">Registro de deudas de vecinos de confianza, límites de crédito y cobro de abonos</p>
			</div>
		</div>

		<button
			onclick={openCreateModal}
			class="px-5 py-2.5 rounded-xl text-xs font-black bg-cyan-600 hover:bg-cyan-700 text-white transition flex items-center gap-1.5 shadow-sm active:scale-95 cursor-pointer"
		>
			<span>+</span> Registrar Nuevo Vecino
		</button>
	</div>

	<!-- Indicadores de Fiados -->
	<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
		<div class="bg-white rounded-2xl p-5 border border-rose-200 shadow-xs space-y-1 bg-rose-50/40">
			<span class="text-xs font-bold text-rose-800 uppercase">Total Pendiente por Cobrar</span>
			<p class="text-2xl sm:text-3xl font-black text-rose-700 font-mono">S/ {totalDebt.toFixed(2)}</p>
			<span class="text-[11px] text-rose-600 font-medium">{debtorCount} vecinos con saldo pendiente</span>
		</div>

		<div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-1">
			<span class="text-xs font-bold text-slate-500 uppercase">Clientes Registrados</span>
			<p class="text-2xl sm:text-3xl font-black text-slate-900 font-mono">{customers.length}</p>
			<span class="text-[11px] text-slate-500">Cuentas con opción de crédito</span>
		</div>

		<div class="bg-white rounded-2xl p-5 border border-emerald-200 shadow-xs space-y-1 bg-emerald-50/40">
			<span class="text-xs font-bold text-emerald-800 uppercase">Vecinos al Día</span>
			<p class="text-2xl sm:text-3xl font-black text-emerald-700 font-mono">{customers.length - debtorCount}</p>
			<span class="text-[11px] text-emerald-600 font-medium">Sin deudas acumuladas</span>
		</div>
	</div>

	<!-- Tabla de Clientes del Cuaderno de Fiados -->
	<div class="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
		<div class="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
			<h2 class="text-xs font-black uppercase text-slate-700 flex items-center gap-2">
				<span>📖</span> Cuentas Corrientes de Vecinos
			</h2>
			<span class="text-xs text-slate-500 font-medium">{customers.length} cuentas en libreta</span>
		</div>

		{#if loading}
			<div class="p-12 text-center text-slate-400 text-sm font-medium">Cargando cuentas...</div>
		{:else if customers.length === 0}
			<div class="p-12 text-center text-slate-500 text-sm space-y-3 font-medium">
				<p>Aún no hay clientes anotados en la libreta de fiados.</p>
				<button onclick={openCreateModal} class="text-xs font-bold text-cyan-700 underline">
					+ Registrar el primer cliente ahora
				</button>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full text-left text-xs">
					<thead class="bg-white text-slate-600 uppercase tracking-wider text-[11px] font-bold border-b border-slate-200">
						<tr>
							<th class="p-4">Nombre del Vecino</th>
							<th class="p-4">DNI / Celular</th>
							<th class="p-4">Límite de Fiado</th>
							<th class="p-4">Deuda Actual</th>
							<th class="p-4">Estado</th>
							<th class="p-4 text-right">Opciones</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-100 font-medium">
						{#each customers as cust}
							<tr class="hover:bg-slate-50/80 transition">
								<td class="p-4">
									<p class="font-bold text-slate-900 text-sm">{cust.name}</p>
									<span class="text-[10px] uppercase font-bold text-slate-400">Tipo: {cust.customer_type}</span>
								</td>
								<td class="p-4 text-slate-600 font-mono text-[11px]">
									{cust.document_number || 'Sin DNI'} {cust.phone ? `• ${cust.phone}` : ''}
								</td>
								<td class="p-4 text-slate-600 font-mono">
									S/ {cust.credit_limit.toFixed(2)}
								</td>
								<td class="p-4">
									<span class="font-black font-mono text-sm {cust.current_debt > 0 ? 'text-rose-600' : 'text-slate-400'}">
										S/ {cust.current_debt.toFixed(2)}
									</span>
								</td>
								<td class="p-4">
									{#if cust.current_debt > 0}
										<span class="px-2.5 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-200 text-[10px] font-black uppercase">
											Debe S/ {cust.current_debt.toFixed(2)}
										</span>
									{:else}
										<span class="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 text-[10px] font-black uppercase">
											✓ Al Día
										</span>
									{/if}
								</td>
								<td class="p-4 text-right">
									{#if cust.current_debt > 0}
										<button
											onclick={() => openPayModal(cust)}
											class="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-black text-xs transition shadow-xs active:scale-95 cursor-pointer"
										>
											💵 Cobrar Abono
										</button>
									{:else}
										<span class="text-slate-400 text-[11px] font-medium">Sin saldo</span>
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>

<!-- Modal Registrar Abono -->
{#if showPayModal && selectedCustomer}
	<div class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
		<div class="bg-white rounded-3xl max-w-sm w-full p-6 space-y-4 border border-slate-200 shadow-2xl animate-fade-in">
			<div class="flex items-center justify-between border-b border-slate-200 pb-3">
				<h3 class="text-base font-black text-slate-900 flex items-center gap-2">
					<span>💵</span> Registrar Pago de Fiado
				</h3>
				<button onclick={() => (showPayModal = false)} class="text-slate-400 hover:text-slate-700">✕</button>
			</div>

			<form onsubmit={handlePaySubmit} class="space-y-3.5 text-xs">
				<div class="p-3.5 rounded-2xl bg-rose-50/70 border border-rose-200 space-y-1">
					<p class="text-slate-600">Vecino: <strong class="text-slate-900">{selectedCustomer.name}</strong></p>
					<p class="text-slate-600">Deuda actual: <strong class="text-rose-700 text-base font-mono">S/ {selectedCustomer.current_debt.toFixed(2)}</strong></p>
				</div>

				<div class="space-y-1">
					<label for="c-pay" class="font-bold text-slate-800">Monto recibido en efectivo (S/) *</label>
					<input
						id="c-pay"
						type="number"
						step="0.5"
						min="0.5"
						max={selectedCustomer.current_debt}
						required
						bind:value={paymentAmount}
						class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-300 text-emerald-800 text-xl font-black font-mono focus:outline-none"
					/>
				</div>

				<div class="flex gap-1.5 pt-1">
					<button
						type="button"
						onclick={() => (paymentAmount = (selectedCustomer.current_debt / 2).toFixed(2))}
						class="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs"
					>
						Pagar la mitad (50%)
					</button>
					<button
						type="button"
						onclick={() => (paymentAmount = selectedCustomer.current_debt.toFixed(2))}
						class="px-2.5 py-1.5 rounded-lg bg-emerald-100 hover:bg-emerald-200 text-emerald-800 font-black text-xs"
					>
						Cancelar Todo (100%)
					</button>
				</div>

				<div class="flex gap-2 pt-3 border-t border-slate-200">
					<button
						type="button"
						onclick={() => (showPayModal = false)}
						class="flex-1 py-2.5 rounded-xl font-bold bg-slate-100 hover:bg-slate-200 text-slate-700"
					>
						Cancelar
					</button>
					<button
						type="submit"
						disabled={isSubmittingPay}
						class="flex-1 py-2.5 rounded-xl font-black bg-emerald-600 hover:bg-emerald-700 text-white disabled:opacity-50"
					>
						{isSubmittingPay ? 'Guardando...' : 'Confirmar Abono'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- Modal Registrar Nuevo Vecino -->
{#if showCreateModal}
	<div class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
		<div class="bg-white rounded-3xl max-w-sm w-full p-6 space-y-4 border border-slate-200 shadow-2xl animate-fade-in">
			<div class="flex items-center justify-between border-b border-slate-200 pb-3">
				<h3 class="text-base font-black text-slate-900 flex items-center gap-2">
					<span>👤</span> Anotar Nuevo Vecino
				</h3>
				<button onclick={() => (showCreateModal = false)} class="text-slate-400 hover:text-slate-700">✕</button>
			</div>

			<form onsubmit={handleCreateSubmit} class="space-y-3 text-xs">
				<div class="space-y-1">
					<label for="cn-name" class="font-bold text-slate-800">Nombre del Vecino *</label>
					<input
						id="cn-name"
						type="text"
						required
						bind:value={customerForm.name}
						placeholder="Ej: Doña Rosa (Frente a la tienda)..."
						class="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 font-semibold focus:outline-none"
					/>
				</div>

				<div class="grid grid-cols-2 gap-2">
					<div class="space-y-1">
						<label for="cn-dni" class="font-bold text-slate-800">DNI</label>
						<input
							id="cn-dni"
							type="text"
							bind:value={customerForm.document_number}
							placeholder="8 dígitos"
							class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 font-mono text-slate-900 focus:outline-none"
						/>
					</div>

					<div class="space-y-1">
						<label for="cn-phone" class="font-bold text-slate-800">Teléfono / WhatsApp</label>
						<input
							id="cn-phone"
							type="text"
							bind:value={customerForm.phone}
							placeholder="987 654 321"
							class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 font-mono text-slate-900 focus:outline-none"
						/>
					</div>
				</div>

				<div class="space-y-1">
					<label for="cn-limit" class="font-bold text-slate-800">Límite Máximo de Fiado (S/)</label>
					<input
						id="cn-limit"
						type="number"
						step="10"
						bind:value={customerForm.credit_limit}
						class="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 font-bold text-slate-900 focus:outline-none"
					/>
				</div>

				<div class="flex gap-2 pt-2 border-t border-slate-200">
					<button
						type="button"
						onclick={() => (showCreateModal = false)}
						class="flex-1 py-2.5 rounded-xl font-bold bg-slate-100 hover:bg-slate-200 text-slate-700"
					>
						Cancelar
					</button>
					<button
						type="submit"
						disabled={isSubmittingCustomer}
						class="flex-1 py-2.5 rounded-xl font-black bg-cyan-600 hover:bg-cyan-700 text-white disabled:opacity-50"
					>
						{isSubmittingCustomer ? 'Guardando...' : 'Anotar en Libreta'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
