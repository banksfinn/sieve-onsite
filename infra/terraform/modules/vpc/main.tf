# Create a VPC
resource "aws_vpc" "findfi_vpc" {
  cidr_block           = var.cidr_block
}

# Create Public Subnets
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.findfi_vpc.id
  for_each      = var.public_subnets
  cidr_block    = each.value.cidr
  availability_zone = each.value.az
}

# Create Private Subnets
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.findfi_vpc.id
  for_each      = var.private_subnets
  cidr_block    = each.value.cidr
  availability_zone = each.value.az
}

# Create an Internet Gateway
resource "aws_internet_gateway" "findfi_igw" {
  vpc_id = aws_vpc.findfi_vpc.id
}

resource "aws_eip" "nat_eip" {
  lifecycle {
    create_before_destroy = true 
  }
}

resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = tolist(values(aws_subnet.public))[0].id
  depends_on    = [aws_internet_gateway.findfi_igw]
}

# Create a Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.findfi_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.findfi_igw.id
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.findfi_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gw.id
  }
}

# Associate Public Route Table with Public Subnets
resource "aws_route_table_association" "public" {
  for_each      = aws_subnet.public
  subnet_id     = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  for_each      = aws_subnet.private
  subnet_id     = each.value.id
  route_table_id = aws_route_table.private.id
}
