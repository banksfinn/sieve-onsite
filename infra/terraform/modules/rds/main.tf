resource "aws_db_subnet_group" "findfi_rds_subnet_group" {
  name       = "findfi-rds-subnet-group"
  subnet_ids = var.private_subnet_ids

}

# Create an RDS Instance
resource "aws_db_instance" "findfi_rds" {
  allocated_storage    = 20
  engine               = "postgres"
  instance_class       = "db.t4g.micro"
  username             = "findfi"
  password             = var.password
  parameter_group_name = "default.postgres16"
  db_name              = var.database_name

  vpc_security_group_ids = [var.rds_security_group_id]
  db_subnet_group_name = aws_db_subnet_group.findfi_rds_subnet_group.name
  skip_final_snapshot  = true
}
