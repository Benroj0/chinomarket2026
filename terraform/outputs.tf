output "vpc_id" {
  description = "ID de la VPC creada"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "ID de la subred pública"
  value       = aws_subnet.public.id
}

output "private_subnets" {
  description = "IDs de las subredes privadas"
  value       = [aws_subnet.private_1.id, aws_subnet.private_2.id]
}

output "rds_endpoint" {
  description = "Endpoint privado de PostgreSQL RDS"
  value       = aws_db_instance.postgres.address
}

output "ec2_public_ip" {
  description = "Dirección IP pública de la instancia EC2"
  value       = aws_instance.web_server.public_ip
}

output "app_url" {
  description = "URL para acceder a la tienda en línea"
  value       = "http://${aws_instance.web_server.public_ip}"
}

output "app_direct_vite_url" {
  description = "URL directa en puerto 5174"
  value       = "http://${aws_instance.web_server.public_ip}:5174"
}

output "api_docs_url" {
  description = "URL de la documentación interactiva Swagger"
  value       = "http://${aws_instance.web_server.public_ip}:8002/docs"
}

output "ssh_command" {
  description = "Comando para conectarse por SSH al servidor"
  value       = "ssh -i chinomarket-key.pem ubuntu@${aws_instance.web_server.public_ip}"
}
