# terraform-remote-state
This repository enables locking and unlocking of terraform remote state file for AWS. <br /><br />

Pre Requisites:<br />
Before running the 'terraform.py' ensure the following resources on your system.<br />
1. Latest terraform build<br />
2. AWS credentials are sources as environment variables:<br />
      export AWS_DEFAULT_REGION=<Region name><br />
      export AWS_ACCESS_KEY_ID=<Your access key id><br />
      export AWS_SECRET_ACCESS_KEY=<Your secret key id><br />
      export S3_BUCKET_NAME=pubc-tfstate<br />
      export DB_DOMAIN_NAME=tfstate<br />
3. Run 'pip install -r requirements.txt' (To install dependencies)<br />
4. The Terraform template file is in the same directory as the resository.<br /><br />

To run terraform.py:<br />
python terraform.py <cmd><br /><br />

For terraform plan : python terraform.py plan<br />
For terraform apply : python terraform.py deploy<br />
For terraform destroy: python terraform.py destroy.<br /><br />

To use this file as a library:<br />
import terraform<br /><br />

To call terraform run:<br />
terraform.run_command('plan/apply/destroy')<br />
