# 🗑️ Azure Infrastructure Cleanup Guide

This guide provides multiple options to destroy the Azure infrastructure created by the CI/CD pipeline for the FastAPI TDD Docker project.

## ⚠️ **Important Notes**

- **This is irreversible** - once deleted, all data and configurations are lost
- **Backup any important data** before proceeding
- **Verify you're targeting the correct resources** to avoid accidental deletion

## 🎯 **Method 1: Direct Resource Group Deletion (Recommended)**

**Fastest and most reliable method**

### Prerequisites

- Azure CLI installed and authenticated
- Know your resource group name (likely `rg-production` or similar)

### Steps

```bash
# 1. Login to Azure (if not already logged in)
az login

# 2. List all resource groups to find the one created by azd
az group list --output table

# 3. Look for resource groups with names like:
#    - rg-fastapi-tdd-docker-production
#    - rg-fastapi-tdd-docker-*
#    - Any group created around your deployment time

# 4. Delete the resource group (replace with actual name)
az group delete --name "rg-fastapi-tdd-docker-production" --yes --no-wait

# 5. Verify deletion (optional)
az group list --output table
```

### What This Deletes

- Container Apps Environment
- Container Registry
- Application Insights
- Log Analytics Workspace
- All associated networking and security resources

---

## 🚀 **Method 2: GitHub Actions Destroy Workflow**

**Automated destruction through CI/CD**

### Create Destroy Workflow File

Create `.github/workflows/destroy-infrastructure.yml`:

```yaml
name: 🗑️ Destroy Azure Infrastructure

on:
  workflow_dispatch: # Manual trigger only - prevents accidental destruction
    inputs:
      confirmation:
        description: 'Type "DESTROY" to confirm infrastructure deletion'
        required: true
        type: string

env:
  AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
  AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
  AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

jobs:
  destroy:
    name: "🔥 Destroy Azure Resources"
    runs-on: ubuntu-latest
    if: github.event.inputs.confirmation == 'DESTROY'
    environment: production
    permissions:
      contents: read
      id-token: write

    steps:
      - name: ⚠️ Destruction Confirmation
        run: |
          echo "🚨 DESTRUCTIVE ACTION CONFIRMED"
          echo "This will permanently delete all Azure resources"
          echo "Environment: production"

      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install Azure Developer CLI (azd)
        run: |
          curl -fsSL https://aka.ms/install-azd.sh | bash
          echo "$HOME/.azd/bin" >> $GITHUB_PATH

      - name: Log in to Azure
        uses: azure/login@v2
        with:
          creds: '{"clientId":"${{ secrets.AZURE_CLIENT_ID }}","clientSecret":"${{ secrets.AZURE_CLIENT_SECRET }}","subscriptionId":"${{ secrets.AZURE_SUBSCRIPTION_ID }}","tenantId":"${{ secrets.AZURE_TENANT_ID }}"}'

      - name: Destroy Infrastructure with azd
        run: |
          # Authenticate azd with service principal
          azd auth login --client-id "$AZURE_CLIENT_ID" --client-secret "$AZURE_CLIENT_SECRET" --tenant-id "$AZURE_TENANT_ID"

          # Try to select production environment
          azd env select production || azd env new production

          # Set environment location
          azd env set AZURE_LOCATION australiaeast

          # Destroy all resources
          azd down --force --purge
        env:
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
          AZURE_ENV_NAME: production

      - name: ✅ Destruction Complete
        run: |
          echo "🎉 Infrastructure successfully destroyed!"
          echo "All Azure resources have been removed."
          echo "💰 No more charges will be incurred."
```

### How to Use

1. Commit and push the workflow file
2. Go to GitHub Actions tab in your repository
3. Select "🗑️ Destroy Azure Infrastructure" workflow
4. Click "Run workflow"
5. Type "DESTROY" in the confirmation field
6. Click "Run workflow" button

---

## 🌐 **Method 3: Azure Portal (GUI Method)**

**Visual approach using web interface**

### Steps

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Sign in with your Azure account
3. In the left sidebar, click **Resource groups**
4. Find the resource group created by azd (usually `rg-fastapi-tdd-docker-production` or similar)
5. Click on the resource group name
6. Review the resources inside (Container Apps, Registry, etc.)
7. Click **Delete resource group** at the top
8. Type the resource group name to confirm
9. Check "Apply force delete" if prompted
10. Click **Delete**

### Verification

- The resource group will show "Deleting..." status
- Refresh after a few minutes to confirm it's gone
- Check your Azure billing to ensure charges have stopped

---

## 🛠️ **Method 4: Local azd Command**

**Using azd locally with remote environment sync**

### Prerequisites

- Azure Developer CLI (azd) installed locally
- Access to the same service principal used in CI/CD

### Steps

```bash
# 1. Navigate to project directory
cd /home/pedro/code/fastapi-tdd-docker

# 2. Create/select production environment
azd env new production
# OR
azd env select production

# 3. Set environment variables to match CI/CD
azd env set AZURE_LOCATION australiaeast

# 4. Authenticate with service principal (use your actual values)
azd auth login --client-id "$AZURE_CLIENT_ID" \
               --client-secret "$AZURE_CLIENT_SECRET" \
               --tenant-id "$AZURE_TENANT_ID"

# 5. Destroy infrastructure
azd down --force --purge

# 6. Verify destruction
azd show
```

---

## 🔑 **Method 5: Service Principal Direct Commands**

**Using the same credentials as CI/CD**

### Get Your Service Principal Details

From your `github-secrets-*.txt` file or GitHub secrets:

- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

### Commands

```bash
# 1. Login with service principal
az login --service-principal \
  --username "YOUR_AZURE_CLIENT_ID" \
  --password "YOUR_AZURE_CLIENT_SECRET" \
  --tenant "YOUR_AZURE_TENANT_ID"

# 2. Set subscription context
az account set --subscription "YOUR_AZURE_SUBSCRIPTION_ID"

# 3. List resource groups to identify target
az group list --output table

# Delete the azd-created resource group
az group delete --name "rg-fastapi-tdd-docker-production" --yes --no-wait

# 5. Logout (security best practice)
az logout
```

---

## 🧹 **Complete Cleanup Checklist**

After destroying Azure infrastructure, consider cleaning up:

### GitHub Repository

- [ ] Remove GitHub secrets (if not needed for other projects):
  - `AZURE_CLIENT_ID`
  - `AZURE_CLIENT_SECRET`
  - `AZURE_TENANT_ID`
  - `AZURE_SUBSCRIPTION_ID`

### Azure Service Principal

```bash
# List service principals to find yours
az ad sp list --display-name "github-actions-fastapi-tdd" --output table

# Delete service principal (optional)
az ad sp delete --id "YOUR_SERVICE_PRINCIPAL_OBJECT_ID"
```

### Local Files

- [ ] Delete `github-secrets-*.txt` files
- [ ] Clear local azd environments: `azd env list` and `azd env delete <name>`

---

## 💰 **Cost Verification**

After destruction, verify no charges are occurring:

1. **Azure Cost Management**: Check [Azure Cost Management](https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Menu/~/overview)
2. **Billing Alerts**: Set up alerts for unexpected charges
3. **Resource Verification**: Ensure no orphaned resources remain

---

## 🆘 **Troubleshooting**

### "Resource Group Not Found"

- Check if it was already deleted
- Verify you're in the correct subscription: `az account show`

### "Permission Denied"

- Ensure your service principal has `Contributor` + `User Access Administrator` roles
- Verify you're authenticated: `az account show`

### "Resources Still Exist After Deletion"

- Some resources may take time to fully delete
- Check for dependencies that might prevent deletion
- Use `--force` flags where available

### "azd Command Not Found"

```bash
# Install azd
curl -fsSL https://aka.ms/install-azd.sh | bash
source ~/.bashrc
```

---

## 🎉 **Success Indicators**

You'll know the destruction was successful when:

- ✅ Resource group no longer appears in `az group list`
- ✅ Azure portal shows no resources for the project
- ✅ Azure billing shows $0.00 for related services
- ✅ `azd show` returns "no environment found" or similar

---

## 📞 **Need Help?**

If you encounter issues:

1. Check the Azure Activity Log in the portal
2. Review error messages carefully
3. Try the Portal method as a fallback
4. Remember: deleting the resource group is the nuclear option that always works

**Happy cleanup!** 🧹✨
