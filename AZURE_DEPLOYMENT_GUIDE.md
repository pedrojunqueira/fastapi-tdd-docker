# Azure Deployment Guide

## What Has Been Created

This FastAPI project now includes a complete Azure infrastructure setup using Azure Developer CLI (azd). Here's what we've built:

## 1. Project Configuration Files

### `azure.yaml`

- Main azd configuration file
- Defines your application service and deployment hooks
- Points to the `./project` directory containing your FastAPI app

### `infra/` Directory

Complete Azure infrastructure defined as code using Bicep templates:

**Main Infrastructure:**

- `main.bicep`: Orchestrates all Azure resources
- `main.parameters.json`: Environment-specific parameters

**Application Layer:**

- `app/web.bicep`: Azure Container Apps configuration for your FastAPI app
- `database-container.bicep`: Azure PostgreSQL Server setup in container

**Core Infrastructure:**

- `core/host/container-apps.bicep`: Container Apps Environment & Registry
- `core/host/container-app.bicep`: Individual container app configuration
- `core/security/keyvault.bicep`: Key Vault for secrets management
- `core/monitor/monitoring.bicep`: Log Analytics & Application Insights

## 2. Azure Resources That Will Be Created

When you run `azd up`, these Azure resources will be provisioned:

1. **Resource Group**: Container for all resources
2. **Azure Container Registry**: Stores your Docker images
3. **Azure Container Apps Environment**: Managed Kubernetes environment
4. **Azure Container Apps (Web)**: Runs your FastAPI application
5. **Azure Container Apps (Database)**: Runs PostgreSQL database container
6. **Azure Key Vault**: Stores secrets and configuration
7. **Log Analytics Workspace**: Centralized logging
8. **Application Insights**: Application monitoring and diagnostics

### Database Architecture: Containerized PostgreSQL

**Key Change**: We're using a **containerized PostgreSQL database** instead of Azure Database for PostgreSQL managed service.

#### Benefits:

- **💰 Cost Savings**: ~70% cheaper than managed PostgreSQL
- **🔄 Consistency**: Same database setup as local development
- **⚡ Simplicity**: No complex networking or firewall rules
- **🎛️ Control**: Full control over PostgreSQL configuration

#### Architecture:

```
┌─────────────────────────────────────────┐
│        Container Apps Environment        │
│  ┌─────────────┐    ┌─────────────────┐ │
│  │    Web      │───▶│    Database     │ │
│  │  (FastAPI)  │    │  (PostgreSQL)   │ │
│  └─────────────┘    └─────────────────┘ │
└─────────────────────────────────────────┘
```

## 3. How the Deployment Works

### Build Process:

1. azd builds your Docker image from `./project/Dockerfile.prod`
2. Pushes the image to Azure Container Registry
3. Deploys the image to Azure Container Apps

### Infrastructure Process:

1. Provisions all Azure resources using Bicep templates
2. Configures networking, security, and monitoring
3. Sets up database with proper firewall rules
4. Stores connection strings in Key Vault

### Environment Variables:

- `DATABASE_URL`: Automatically configured from PostgreSQL
- `ENVIRONMENT`: Set to "production"
- `TESTING`: Set to "0"

## 4. Next Steps to Deploy

### Prerequisites Check:

```bash
# Check if Azure CLI is installed
az --version

# Check if azd is installed
azd version

# Login to Azure
azd auth login
```

### Deploy to Australia East:

```bash
# Navigate to your project directory
cd /home/pedro/code/fastapi-tdd-docker

# Set the location to Australia East
azd env set AZURE_LOCATION australiaeast

# Get List of evironement variables
azd env get-values

# Deploy everything (first time)
azd up
```

### What azd up will do:

1. Prompt you to select an Azure subscription
2. Create a new environment name (or use existing)
3. Provision all Azure resources in Australia East
4. Build and deploy your FastAPI application
5. Run database migrations
6. Provide you with the application URL

### After Deployment:

```bash
# View your deployed application URL
azd show

# Check application logs
azd logs

# Monitor in Azure portal
azd dashboard
```

## 5. Understanding the Cost

The resources created will incur costs (Australia East pricing):

- **Container Apps (Web + DB)**: Pay per usage (~$10-25/month for light usage)
- **Container Registry**: Basic tier (~$6 AUD/month)
- **Log Analytics & Monitoring**: Based on data ingestion (~$5 AUD/month)
- **Key Vault**: Operations-based (~$2 AUD/month)

**Total Estimated Cost**: ~$23-38 AUD/month

### Cost Comparison:

- **Containerized PostgreSQL**: ~$25-35 AUD/month total
- **Managed Azure PostgreSQL**: ~$60-80 AUD/month total
- **💰 Savings**: ~40-60% cost reduction with containerized approach

## 6. Managing Environments

You can create multiple environments (dev, staging, prod):

```bash
# Create staging environment
azd env new staging

# Switch environments
azd env select production
azd env select staging

# Each environment is completely isolated
```

## 7. Updating Your Application

For code changes:

```bash
# Deploy only application changes (faster)
azd deploy
```

For infrastructure changes:

```bash
# Update infrastructure only
azd provision

# Or do both
azd up
```

## 8. Cleanup

When you're done testing:

```bash
# Remove all Azure resources (saves money)
azd down
```

This will delete everything except the Container Registry images (which have minimal cost).

---

**Ready to deploy?** Run `azd up` from your project directory and azd will guide you through the process!
