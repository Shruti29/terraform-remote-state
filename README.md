# terraform-remote-state
This repository enables locking and unlocking of terraform remote state file for AWS.

Pre Requisites:
Before running the 'terraform.py' ensure the following resources on your system.
1. Latest terraform build
2. AWS credentials are sources as environment variables:
      export AWS_DEFAULT_REGION=<Region name>
      export AWS_ACCESS_KEY_ID=<Your access key id>
      export AWS_SECRET_ACCESS_KEY=<Your secret key id>
      export S3_BUCKET_NAME=pubc-tfstate
      export DB_DOMAIN_NAME=tfstate
3. Run 'pip install -r requirements.txt' (To install dependencies)
4. The Terraform template file is in the same directory as the resository.

To run terraform.py:
python terraform.py <cmd>

For terraform plan : python terraform.py plan
For terraform apply : python terraform.py deploy
For terraform destroy: python terraform.py destroy.

To use this file as a library:
import terraform

To call terraform run:
terraform.run_command('plan/apply/destroy')
