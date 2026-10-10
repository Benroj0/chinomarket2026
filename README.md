# 🏪 Chino Market 2026 — Sistema de Gestión Comercial y Punto de Venta (POS)

Chinomarket remaster remake 2.0 shippuden next generation DLC la venganza. Sistema completo e independiente para la administración de tiendas de abarrotes, bodegas y minimarkets.

## 🚀 Stack Tecnológico
* **Backend:** FastAPI (Python 3.12), SQLModel, SQLAlchemy Async, Alembic, PostgreSQL 16 (asyncpg).
* **Frontend:** SvelteKit 2 + Svelte 5 (Runes), Tailwind CSS v4, Vanilla CSS Design System.
* **Infraestructura:** Docker & Docker Compose con puertos dedicados independientes.

## 🗄️ Mapeo del Modelo de Dominio
| Sistema de Torneos | Chino Market (Abarrotes) | Propósito |
| :--- | :--- | :--- |
| **Torneos** | **Categorías & Tienda** | Agrupación de productos (Lácteos, Abarrotes, Limpieza, etc.) |
| **Equipos** | **Productos & Proveedores** | Catálogo con SKU, código de barras, unidades (kg, lt, und) y costos |
| **Partidos / Fixture** | **Ventas & Boletas (POS)** | Registro de compras con comprobantes y líneas de venta |
| **Arbitraje & Marcador** | **Punto de Venta (POS)** | Cobro en tiempo real (Efectivo, Yape/Plin, Tarjeta, Fiado) |
| **Tabla de Posiciones** | **Kárdex & Control Stock** | Movimientos de inventario (Entradas, Salidas, Mermas, Ajustes) |
| **Delegados / Jugadores** | **Clientes & Deudores** | Libro de fiados, límites de crédito y clientes mayoristas |

## 📦 Puesta en Marcha Rápida con Docker Compose

```bash
docker compose up --build
```

* **Frontend:** http://localhost:5174
* **Backend API:** http://localhost:8002
* **Documentación OpenAPI (Swagger):** http://localhost:8002/docs
* **Base de Datos PostgreSQL:** Puerto 5434 (base de datos `chinomarket_db`)
