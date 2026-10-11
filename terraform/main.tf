# ─────────────────────────────────────────────────────────────────────────────
# 1. Red y VPC (2 Capas: Pública y Privada)
# ─────────────────────────────────────────────────────────────────────────────

# VPC Principal
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name    = "${var.project_name}-vpc"
    Project = var.project_name
  }
}

# Internet Gateway para acceso público
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Subred Pública (Capa Web / Aplicación)
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-subnet"
    Tier = "Public"
  }
}

# Subred Privada 1 (Capa Base de Datos - AZ A)
resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_1_cidr
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "${var.project_name}-private-subnet-1"
    Tier = "Private"
  }
}

# Subred Privada 2 (Capa Base de Datos - AZ B, requerida por RDS)
resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_2_cidr
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "${var.project_name}-private-subnet-2"
    Tier = "Private"
  }
}

# Tabla de Enrutamiento Pública (Salida a Internet por IGW)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Tabla de Enrutamiento Privada (Sin salida a Internet - Aislamiento Total)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-private-rt"
  }
}

resource "aws_route_table_association" "private_1" {
  subnet_id      = aws_subnet.private_1.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_2" {
  subnet_id      = aws_subnet.private_2.id
  route_table_id = aws_route_table.private.id
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. Seguridad (Security Groups)
# ─────────────────────────────────────────────────────────────────────────────

# Security Group para Capa Pública (Web / EC2)
resource "aws_security_group" "web_sg" {
  name        = "${var.project_name}-web-sg"
  description = "Reglas de firewall para servidores web publicos"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP Web"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS Web"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SvelteKit Frontend Directo"
    from_port   = 5174
    to_port     = 5174
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "FastAPI Backend Directo"
    from_port   = 8002
    to_port     = 8002
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Permitir todo el trafico de salida"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-web-sg"
  }
}

# Security Group para Capa Privada (Base de Datos RDS)
resource "aws_security_group" "db_sg" {
  name        = "${var.project_name}-db-sg"
  description = "Permite acceso a PostgreSQL solo desde el SG de la capa Web"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL exclusivo desde Web SG"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web_sg.id]
  }

  egress {
    description = "Trafico de salida"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-db-sg"
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. Base de Datos en Capa Privada (Amazon RDS PostgreSQL)
# ─────────────────────────────────────────────────────────────────────────────

resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier             = "${var.project_name}-db"
  allocated_storage      = 20
  max_allocated_storage  = 20
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "15.13"
  instance_class         = "db.t3.micro"
  db_name                = "chinomarket_db"
  username               = "postgres"
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  publicly_accessible    = false
  skip_final_snapshot    = true
  deletion_protection    = false

  tags = {
    Name = "${var.project_name}-rds-postgres"
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. Par de Llaves SSH para Acceso a EC2
# ─────────────────────────────────────────────────────────────────────────────

resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated_key" {
  key_name   = "${var.project_name}-key"
  public_key = tls_private_key.ssh_key.public_key_openssh
}

resource "local_file" "ssh_private_key_file" {
  content         = tls_private_key.ssh_key.private_key_pem
  filename        = "${path.module}/chinomarket-key.pem"
  file_permission = "0600"
}

# ─────────────────────────────────────────────────────────────────────────────
# 5. Instancia EC2 en Capa Pública (Frontend + Backend)
# ─────────────────────────────────────────────────────────────────────────────

# AMI Oficial Ubuntu 24.04 LTS
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

resource "aws_instance" "web_server" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t3.small"
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web_sg.id]
  key_name                    = aws_key_pair.generated_key.key_name
  associate_public_ip_address = true

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  user_data = <<-EOF
              #!/bin/bash
              set -ex

              # 1. Actualizar sistema e instalar dependencias basicas
              apt-get update -y
              apt-get install -y ca-certificates curl gnupg git netcat-openbsd

              # 2. Configurar repositorio e instalar Docker oficial
              install -m 0755 -d /etc/apt/keyrings
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
              chmod a+r /etc/apt/keyrings/docker.asc

              echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
                $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
                tee /etc/apt/sources.list.d/docker.list > /dev/null

              apt-get update -y
              apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

              systemctl enable docker
              systemctl start docker
              usermod -aG docker ubuntu

              # 3. Clonar repositorio
              mkdir -p /opt/app
              git clone https://github.com/Benroj0/chinomarket2026.git /opt/app
              cd /opt/app
              chown -R ubuntu:ubuntu /opt/app

              # 4. Crear archivo .env para backend conectando a RDS en Subred Privada
              RDS_HOST="${aws_db_instance.postgres.address}"
              cat <<EOT > /opt/app/backend/.env
              APP_NAME="Chino Market API"
              APP_VERSION="0.1.0"
              DEBUG=false
              DATABASE_URL=postgresql+asyncpg://postgres:${var.db_password}@$${RDS_HOST}:5432/chinomarket_db
              SECRET_KEY=super-secret-key-chinomarket-2026
              ADMIN_PIN=1234
              CORS_ORIGINS=*
              EOT

              # 5. Crear archivo docker-compose.prod.yml sin contenedor local de BD
              cat <<EOT > /opt/app/docker-compose.prod.yml
              services:
                backend:
                  build:
                    context: ./backend
                  container_name: chinomarket_backend
                  restart: unless-stopped
                  env_file:
                    - ./backend/.env
                  ports:
                    - "8002:8000"
                  command: >
                    sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8000"

                frontend:
                  image: node:20-alpine
                  container_name: chinomarket_frontend
                  working_dir: /app
                  restart: unless-stopped
                  environment:
                    PUBLIC_API_BASE_URL: /api/v1
                    BACKEND_URL: http://backend:8000
                  ports:
                    - "5174:5173"
                    - "80:5173"
                  volumes:
                    - ./frontend:/app
                    - /app/node_modules
                  command: >
                    sh -c "npm install && npm run dev -- --host 0.0.0.0 --port 5173"
                  depends_on:
                    - backend
              EOT

              # 6. Levantar servicios con Docker Compose
              docker compose -f /opt/app/docker-compose.prod.yml up -d --build
              EOF

  tags = {
    Name = "${var.project_name}-web-server"
    Tier = "Public"
  }

  depends_on = [aws_db_instance.postgres]
}
