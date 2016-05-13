resource "aws_instance" "test" {
  count="1"
  ami = "<test-ami>"
  instance_type = "t2.micro"
  tags {
    Name = "test-vm"
  }
}
