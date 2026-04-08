# Providers
provider "aws" {
  region = var.aws_region
  profile = var.aws_profile
}

terraform {
  backend "s3" {
    key    = "staging/vpc.tfstate"
    bucket = "findfi-terraform-config"
    region =  "us-west-2"
    profile = "findfi"
  }
}

# Include the ALB module
module "alb" {
  source             = "../../modules/alb"
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids       = values(module.vpc.public_subnets)
  alb_security_group_id = module.security_group.alb_security_group_id
  certificate_arn = "arn:aws:acm:us-west-2:229581800822:certificate/22fa2ddd-5c6c-4b64-913c-cbba1fa2a587"
}

module "ecr" {
  source      = "../../modules/ecr"
}

module "ecs" {
  source      = "../../modules/ecs"
  environment = var.environment
  ecs_security_group_id = module.security_group.ecs_security_group_id
  vpc_id = module.vpc.vpc_id
  findfi_version = var.findfi_version
  private_subnet_ids = values(module.vpc.private_subnets)
  ecr_repository_url = module.ecr.ecr_repository_url
  alb_target_group_arn = module.alb.alb_target_group_arn
  # Scaling option
  gateway_desired_count = 1

  rds_connection_string = "postgresql://${module.rds.rds_username}:${module.rds.rds_password}@${module.rds.rds_endpoint}/${module.rds.rds_database_name}"
}

module "rds" {
  source      = "../../modules/rds"
  environment = var.environment
  rds_security_group_id = module.security_group.rds_security_group_id
  password = "1234562252"
  vpc_id = module.vpc.vpc_id
  private_subnet_ids = values(module.vpc.private_subnets)
  database_name = "findfi"
}

module "vpc" {
  source      = "../../modules/vpc"
  environment = var.environment
  cidr_block = var.vpc_cidr_block
  public_subnets = var.public_subnets
  private_subnets = var.private_subnets
}


module "security_group" {
  source      = "../../modules/sg"
  vpc_id      = module.vpc.vpc_id
  environment        = var.environment
}
