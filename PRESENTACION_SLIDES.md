# 📊 Guía Completa de Presentación — Grupo 1: Tienda Virtual Chino Market

Esta guía contiene el contenido exacto y desarrollado para cada una de las diapositivas requeridas por el docente.

---

## 🏷️ Slide 1 — La Empresa y su Problema

### 1. ¿Qué aplicación tienen?
* **Nombre:** Chino Market — Tienda Virtual de Abarrotes y Ventas en Línea.
* **Descripción de la Plataforma:** Es un sistema de comercio electrónico completo compuesto por:
  * **Frontend (SvelteKit):** Catálogo de productos interactivo, carrito de compras, cálculo de montos con IGV, checkout y panel de administración de productos y stock.
  * **Backend (FastAPI):** API REST asíncrona de alto rendimiento que procesa ventas, transacciones de pago, gestión de inventario y autenticación administrativa.
  * **Base de Datos (PostgreSQL en Amazon RDS):** Almacenamiento relacional de productos, clientes, pedidos y comprobantes.

### 2. ¿Qué información manejan?
* **Datos de Clientes:** Nombres, apellidos, número de documento (DNI / RUC), dirección de entrega, número de teléfono y correo electrónico.
* **Datos Transaccionales y de Pagos:** Métodos de pago (Yape, Plin, Transferencia, Tarjeta), montos cobrados, comprobantes de pago (Boletas y Facturas electrónicas) e historial de compras.
* **Datos del Negocio:** Inventario de abarrotes, precios unitarios, tasas de impuestos (IGV 18%) y márgenes de ganancia.

### 3. ¿Qué necesitan proteger?
* **Confidencialidad de Datos Personales:** Cumplimiento con la Ley de Protección de Datos Personales (LPDP). Ningún tercero debe poder acceder a los datos de los clientes.
* **Integridad Financiera:** Evitar manipulación de precios o montos de pago durante el proceso de compra.
* **Disponibilidad del Servicio:** La tienda debe estar operativa 24/7 para no perder ventas ni generar desconfianza en los usuarios.
* **Aislamiento de la Base de Datos:** Prevenir ataques de inyección SQL, accesos no autorizados o filtración masiva de la base de datos de clientes.

---

## ☁️ Slide 2 — Arquitectura Cloud en AWS (Diagrama y Justificación)

### 1. Diagrama de Arquitectura (Para dibujar a mano o en pizarra)

```
                       ┌────────────────────────────────────────────────────────┐
                       │                     INTERNET                           │
                       └──────────────────────────┬─────────────────────────────┘
                                                  │
                                                  ▼
                                       [ Internet Gateway (IGW) ]
                                                  │
┌─────────────────────────────────────────────────┼─────────────────────────────────────────────┐
│  VPC: 10.0.0.0/16                               │                                             │
│                                                 ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ SUBRED PÚBLICA (10.0.1.0/24) - Zona us-east-1a                                          │  │
│  │ Tabla de Enrutamiento: 0.0.0.0/0 ──► Internet Gateway (IGW)                             │  │
│  │                                                                                         │  │
│  │   ┌──────────────────────────────────────────────────────────────────┐                  │  │
│  │   │ Instancia EC2: chinomarket-web-server (Ubuntu 24.04)             │                  │  │
│  │   │ IP Pública Asociada                                              │                  │  │
│  │   │ Security Group Web (Inbound: 80 HTTP, 443 HTTPS, 22 SSH)         │                  │  │
│  │   │   • Frontend Web (SvelteKit)  ── Puerto 80 / 5174                │                  │  │
│  │   │   • Backend API (FastAPI)     ── Puerto 8002                     │                  │  │
│  │   └────────────────────────────────┬─────────────────────────────────┘                  │  │
│  └────────────────────────────────────┼────────────────────────────────────────────────────┘  │
│                                       │ Conexión interna (Puerto 5432)                        │
│                                       ▼                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ SUBRED PRIVADA (10.0.2.0/24 y 10.0.3.0/24) - Zonas us-east-1a y us-east-1b              │  │
│  │ Tabla de Enrutamiento: Solo Tráfico Local (10.0.0.0/16) - SIN ACCESO A INTERNET         │  │
│  │                                                                                         │  │
│  │   ┌──────────────────────────────────────────────────────────────────┐                  │  │
│  │   │ Base de Datos: Amazon RDS PostgreSQL (chinomarket-db)            │                  │  │
│  │   │ IP Privada únicamente (Sin IP Pública)                           │                  │  │
│  │   │ Security Group DB: Solo permite TCP 5432 proveniente del Web SG  │                  │  │
│  │   └──────────────────────────────────────────────────────────────────┘                  │  │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2. Justificación de los Elementos Arquitectónicos:
* **VPC (Virtual Private Cloud):** Proporciona una red virtual aislada y privada en la nube de AWS para tener control absoluto del direccionamiento IP y la topología de red.
* **Internet Gateway (IGW):** Permite que los clientes desde cualquier navegador en Internet puedan conectarse a la tienda web.
* **Subred Pública:** Aloja el servidor EC2 de la aplicación porque los clientes necesitan acceder al catálogo y realizar compras desde la web pública.
* **¿Por qué agregar una Subred Privada? (Justificación Clave):**
  * La base de datos contiene los **datos personales y registros de pago de los clientes**.
  * Si la base de datos estuviera en una subred pública, estaría expuesta a escaneos de puertos, ataques de fuerza bruta e intentos de intrusión directa desde Internet.
  * Al ubicarla en la **Subred Privada**, la base de datos carece de IP pública y de ruta hacia Internet. Solo la instancia EC2 autorizada en la subred pública puede consultarla internamente.

---

## 🔒 Slide 3 — Seguridad (4 Medidas Implementadas)

1. **Separación de Red en Capas (Pública / Privada):**
   * División estricta de subredes dentro de la VPC. La capa de presentación y API es pública, mientras que la capa de persistencia (PostgreSQL) está completamente aislada en la subred privada sin acceso a Internet.

2. **Security Groups como Firewalls Stateful en Cadena:**
   * **Web Security Group:** Permite tráfico web entrante en los puertos 80, 443, 5174 y 8002 desde Internet, y restringe la administración.
   * **Database Security Group:** No permite conexiones por CIDR abierto; utiliza una regla basada en origen referencial (`source: sg-web`) en el puerto `5432`. Solo los paquetes provenientes de la EC2 autorizada pueden tocar la base de datos.

3. **Control de Acceso Administrativo Seguro por Llaves Criptográficas (SSH):**
   * Deshabilitación de autenticación por contraseñas en el servidor Linux.
   * Uso exclusivo de llaves asimétricas RSA de 4096 bits (`chinomarket-key.pem`) para cualquier labor de administración o mantenimiento.

4. **Gestión de Identidades y Menor Privilegio con AWS IAM:**
   * No se almacenan credenciales maestras de AWS dentro de los contenedores ni en el código fuente.
   * Se asignan roles de servicio (`LabRole`) con políticas de privilegios mínimos para que los recursos interactúen de forma segura.

---

## 📐 Slide 5 — Las 6 Dimensiones de AWS Well-Architected Framework

### 1. Excelencia Operativa (Operational Excellence)
* **Infraestructura como Código (IaC):** Toda la arquitectura está definida en Terraform, lo que permite crear, reproducir y versionar el entorno en minutos sin errores manuales.
* **Monitoreo y Salud:** Implementación de endpoints de salud (`/health`) en FastAPI y healthchecks automáticos en Docker para verificar el estado de la aplicación.

### 2. Seguridad (Security)
* **Defensa en Profundidad:** Aislamiento en 2 capas de red (VPC pública/privada), firewalls virtuales (Security Groups), variables de entorno protegidas (`.env`) y cifrado de contraseñas con hashing.

### 3. Confiabilidad (Reliability)
* **Servicio Gestionado con RDS:** Amazon RDS se encarga del aprovisionamiento, respaldos automatizados y recuperación ante fallos de la base de datos.
* **Resiliencia de Contenedores:** Políticas de reinicio automático (`restart: unless-stopped`) en los servicios de Docker ante posibles caídas.

### 4. Eficiencia del Rendimiento (Performance Efficiency)
* **Stack Tecnológico Asíncrono:** Backend con FastAPI y Asyncpg (I/O asíncrono no bloqueante) junto con Frontend reactivo en SvelteKit para tiempos de respuesta ultra rápidos.
* **Almacenamiento de Alto Rendimiento:** Uso de volúmenes SSD de última generación (General Purpose SSD gp3/gp2) tanto en EC2 como en RDS.

### 5. Optimización de Costos (Cost Optimization)
* **Dimensionamiento Adecuado (Right-Sizing):** Uso de instancias `t3.small` y `db.t3.micro` que aprovechan los créditos de AWS Academy / Capa Gratuita sin sobrecostos.
* **Consolidación en Contenedores:** Frontend y Backend comparten la misma instancia de cómputo en la capa web mediante Docker, reduciendo el gasto a un solo servidor EC2.

### 6. Sostenibilidad (Sustainability)
* **Aprovechamiento Eficiente de Recursos:** Al utilizar contenedores Docker livianos (Alpine Linux), se minimiza el uso de CPU y memoria, reduciendo la huella de carbono digital de la infraestructura en los centros de datos de AWS.
