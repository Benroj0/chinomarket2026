/**
 * lib/api/client.js — Cliente HTTP para Chino Market API
 */

const BASE_URL =
	(typeof import.meta !== 'undefined' &&
		(import.meta.env?.PUBLIC_API_BASE_URL || import.meta.env?.VITE_API_BASE_URL)) ||
	'/api/v1';

async function request(path, options = {}) {
	const url = `${BASE_URL}${path}`;
	const response = await fetch(url, {
		headers: {
			'Content-Type': 'application/json',
			...options.headers
		},
		...options
	});

	if (!response.ok) {
		let message = `HTTP ${response.status}`;
		try {
			const errData = await response.json();
			message = errData.detail || errData.message || message;
		} catch (_) {}
		throw new Error(message);
	}

	if (response.status === 204) return null;
	return response.json();
}

export const api = {
	get: (path) => request(path, { method: 'GET' }),
	post: (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) }),
	put: (path, body) => request(path, { method: 'PUT', body: JSON.stringify(body) }),
	patch: (path, body) => request(path, { method: 'PATCH', body: JSON.stringify(body) }),
	delete: (path) => request(path, { method: 'DELETE' })
};

export const dashboardApi = {
	getStats: () => api.get('/dashboard/stats')
};

export const categoriesApi = {
	list: () => api.get('/categories'),
	get: (id) => api.get(`/categories/${id}`),
	create: (data) => api.post('/categories', data),
	delete: (id) => api.delete(`/categories/${id}`)
};

export const productsApi = {
	list: (params) => {
		const qs = params ? '?' + new URLSearchParams(params).toString() : '';
		return api.get(`/products${qs}`);
	},
	get: (id) => api.get(`/products/${id}`),
	create: (data) => api.post('/products', data),
	update: (id, data) => api.put(`/products/${id}`, data),
	delete: (id) => api.delete(`/products/${id}`),
	updateStock: (id, qty) => api.patch(`/products/${id}/stock`, { quantity: qty })
};

export const inventoryApi = {
	listMovements: (limit = 50) => api.get(`/inventory/movements?limit=${limit}`),
	registerMovement: (data) => api.post('/inventory/movements', data),
	getAlerts: () => api.get('/inventory/alerts')
};

export const salesApi = {
	list: () => api.get('/sales'),
	create: (data) => api.post('/sales', data),
	get: (id) => api.get(`/sales/${id}`)
};

export const customersApi = {
	list: () => api.get('/customers'),
	create: (data) => api.post('/customers', data),
	payDebt: (id, data) => api.post(`/customers/${id}/pay-debt`, data)
};
