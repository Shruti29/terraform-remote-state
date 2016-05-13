# This make file
ENV = $(shell echo `grep "^environment" terraform.tfvars | cut -d '=' -f2 | tr -d ' ' |tr -d '"'`)
REGION = $(shell echo `grep "^region" terraform.tfvars | cut -d '=' -f2 | tr -d ' ' | tr -d '"'`)

# Set the following environment variables before running the plan
ACCESS_KEY_ID = $(AWS_ACCESS_KEY_ID)
SECRET_ACCESS_KEY = $(AWS_SECRET_ACCESS_KEY)
AWS_REGION = $(strip $(AWS_DEFAULT_REGION))
TFSTATE_BUCKET=$(S3_BUCKET_NAME)-$(AWS_REGION)
TFSTATE_FILE=terraform.tfstate #This can be a variable as well.


.PHONY: plan
.PHONY: check-prereq config plan deploy

#
# Do the following steps prior to running the environment setup
#   - Install tools in PATH: terraform

check-prereq:
	@echo "check pre-requisites ..."
	command -v terraform >/dev/null 2>&1 || { echo "terraform is not in PATH.  Aborting." >&2; exit 1; }

#
# Set the following environment variable prior to config, plan and apply
#  AWS_DEFAULT_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
#
config:
	@echo "Terraform remote S3 backend config for terraform state ..."
	terraform remote config -backend=s3 \
	  -backend-config="bucket=$(TFSTATE_BUCKET)" \
	  -backend-config="key=$(TFSTATE_FILE)"

plan: config
	@echo "Terraform get, plan ..."
	terraform get
	terraform plan

apply: config
	terraform apply
	rm -f .terraform/terraform.tfstate*


output: config
	terraform show
	rm -f .terraform/terraform.tfstate*

destroy: plan
	terraform destroy
	rm -rf .terraform
