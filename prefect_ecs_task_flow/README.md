# How to Run Prefect Flow as ECS Task
## 1. BuiltIn Container + Storage
Use the Prefect official Docker image, download the files required for running the Flow.

## 2. Custom Container
Use a self-made image that includes dependencies and the Flow code.

# SetUp
## Hosting Agent by ECS Service
1. Change variable values in infra/secret.tfvars
```terraform
access_key      = "*****" # AWS Access Key
secret_key      = "*****" # AWS Secret Key
region          = "*****" # AWS Region
prefect_api_key = "*****" # Prefect Cloud API Key
```

2. Run terraform
```bash
cd infra 
```

```bash
terraform init
```

```bash
terraform apply -var-file=secret.tfvars
```
