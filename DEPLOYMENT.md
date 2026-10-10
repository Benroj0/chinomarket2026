# 🚀 Guía de Despliegue en AWS — Chino Market

Esta guía explica paso a paso cómo ejecutar el sistema en local y cómo llevarlo a producción en **Amazon Web Services (AWS)**, siguiendo una arquitectura idéntica a proyectos cloud basados en contenedores (FastAPI + SvelteKit + PostgreSQL).

---

## 💻 1. Ejecución Local (Entorno de Desarrollo)

Dado que tienes **Docker** y **Docker Compose** instalados, la forma más rápida de correr todo el sistema (Base de Datos + API + Web) es:

```bash
# 1. Ubícate en la raíz del proyecto
cd chinomarket

# 2. Levantar los 3 contenedores
docker compose up --build
```

*(Para correrlo en segundo plano, añade la bandera `-d`: `docker compose up -d --build`)*

### 🌐 Accesos Locales:
* **Frontend Web (SvelteKit):** [http://localhost:5174](http://localhost:5174)
* **Backend API (FastAPI):** [http://localhost:8002](http://localhost:8002)
* **Documentación Swagger:** [http://localhost:8002/docs](http://localhost:8002/docs)
* **Health Check:** [http://localhost:8002/health](http://localhost:8002/health)
* **PostgreSQL:** `localhost:5434` (Usuario: `postgres`, Contraseña: `postgres`, BD: `chinomarket_db`)

---

## ☁️ 2. Estrategia de Despliegue en AWS

Tienes dos opciones principales según los requisitos de tu curso/proyecto:

### Opción A: AWS EC2 con Docker Compose (Recomendada y más directa)
Esta es la opción estándar y rápida, ideal para proyectos académicos y demostraciones completas.

#### Paso 1: Lanzar una Instancia EC2
1. Ir a la consola de AWS -> **EC2** -> **Launch Instance**.
2. **Nombre:** `chinomarket-server`
3. **AMI:** Ubuntu 24.04 LTS o Amazon Linux 2023.
4. **Tipo de Instancia:** `t3.small` (recomendado) o `t3.micro` (capa gratuita, requiere configurar 1-2 GB de swap si compila Vite).
5. **Key Pair:** Crea o selecciona tu par de llaves `.pem` para SSH.
6. **Security Group (Reglas de Entrada / Inbound Rules):**
   * **SSH (22):** Tu IP o Anywhere (0.0.0.0/0).
   * **HTTP (80):** Anywhere (0.0.0.0/0).
   * **HTTPS (443):** Anywhere (0.0.0.0/0).
   * **Custom TCP (5174):** Anywhere (para frontend directo, o redirigir mediante Nginx al puerto 80).
   * **Custom TCP (8002):** Anywhere (para backend API directo).

#### Paso 2: Conectarse y Configurar el Servidor
```bash
ssh -i "tu-llave.pem" ubuntu@<IP-PUBLICA-EC2>

# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker y Git
sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker ubuntu
newgrp docker
```

#### Paso 3: Clonar el Repositorio y Configurar Variables
```bash
git clone <URL_DE_TU_REPOSITORIO_CHINOMARKET>
cd chinomarket

# Revisar variables en backend/.env
# En producción cambia SECRET_KEY y añade la IP/Dominio a CORS_ORIGINS:
nano backend/.env
```

#### Paso 4: Levantar el Proyecto con Docker Compose
```bash
docker compose up -d --build
```

---

### Opción B: Arquitectura Desacoplada (AWS ECS / RDS / S3)
Si tu curso requiere servicios gestionados:
1. **Base de Datos:** AWS RDS PostgreSQL (Single-AZ `db.t3.micro` / `db.t4g.micro`).
2. **Contenedores:** AWS ECR (repositorio de imágenes de Backend) y AWS ECS Fargate o AWS App Runner.
3. **Frontend:** Servido en un contenedor SvelteKit o compilado como SPA/estático en AWS S3 + CloudFront.

---

## 🛡️ 3. Consideraciones de Seguridad para Producción
1. **Cambiar Contraseñas:** No usar `postgres`/`postgres` en producción.
2. **CORS:** En `backend/.env`, actualiza `CORS_ORIGINS` con la IP pública o dominio de tu instancia EC2.
3. **Proxy Inverso:** Puedes colocar un contenedor Nginx o Caddy en el puerto 80/443 para gestionar certificados SSL automáticos con Let's Encrypt.
