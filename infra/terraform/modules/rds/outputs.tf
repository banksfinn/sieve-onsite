output "rds_endpoint" {
  description = "The url of the database"
  value       = aws_db_instance.findfi_rds.endpoint
}

output "rds_database_name" {
  description = "The name of the database"
  value       = aws_db_instance.findfi_rds.db_name
}

output "rds_username" {
  description = "The username of the database"
  value       = aws_db_instance.findfi_rds.username
}

output "rds_password" {
  description = "The password of the database"
  value       = aws_db_instance.findfi_rds.password
}
