# CI/CD Pipeline Setup Summary

## 🚀 What We've Built

A comprehensive GitHub Actions CI/CD pipeline for your FastAPI TDD Docker project that automatically:

### ✅ **Testing & Quality Assurance**

- **Unit Tests**: Runs pytest with PostgreSQL test database
- **Coverage**: Enforces 80% minimum coverage, generates HTML reports
- **Code Quality**: Linting and formatting with Ruff (20+ rule sets)
- **Security**: Security scanning with Ruff security rules
- **Build Validation**: Tests Docker image builds

### 🔄 **Automated Workflows**

#### 1. **Main CI/CD Pipeline** (`.github/workflows/ci-cd.yml`)

- **Triggers**: Push to `master` branch
- **Jobs**: Test → Code Quality → Security → Build → Deploy to Azure
- **Features**:
  - PostgreSQL service container for integration tests
  - Coverage reports uploaded to Codecov
  - Docker layer caching for faster builds
  - Azure deployment with health checks
  - Deployment summary with links

#### 2. **Pull Request Validation** (`.github/workflows/pr-validation.yml`)

- **Triggers**: Pull requests to `master`
- **Jobs**: Same as main pipeline except no deployment
- **Features**:
  - Automatic PR comments on failures
  - Status checks for merge protection
  - Build validation without deployment

## 📋 **Setup Requirements**

### **Required GitHub Secrets**

These secrets must be added to your GitHub repository for Azure deployment:

| Secret Name             | Description                     | How to Get                              |
| ----------------------- | ------------------------------- | --------------------------------------- |
| `AZURE_CLIENT_ID`       | Service Principal Client ID     | Run `./scripts/setup-github-actions.sh` |
| `AZURE_CLIENT_SECRET`   | Service Principal Client Secret | From setup script output                |
| `AZURE_TENANT_ID`       | Azure Tenant ID                 | From setup script output                |
| `AZURE_SUBSCRIPTION_ID` | Azure Subscription ID           | From setup script output                |

### **Optional Secrets**

| Secret Name     | Description              | How to Get                                  |
| --------------- | ------------------------ | ------------------------------------------- |
| `CODECOV_TOKEN` | Coverage reporting token | Sign up at [codecov.io](https://codecov.io) |

## 🛠️ **Setup Steps**

### 1. **Create Azure Service Principal**

```bash
# Run the helper script (recommended) - includes all required permissions
./scripts/setup-github-actions.sh

# Or manually:
az login

# Create service principal with Contributor role
az ad sp create-for-rbac \
  --name "github-actions-fastapi-tdd" \
  --role contributor \
  --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID> \
  --output json

# IMPORTANT: Also add User Access Administrator role for azd deployments
az role assignment create \
  --assignee <CLIENT_ID_FROM_ABOVE> \
  --role "User Access Administrator" \
  --scope /subscriptions/<YOUR_SUBSCRIPTION_ID>
```

#### **🔐 Required Azure Permissions**

The service principal needs **both** roles for successful azd deployment:

| Role                          | Purpose                           | Required For                                  |
| ----------------------------- | --------------------------------- | --------------------------------------------- |
| **Contributor**               | Create and manage Azure resources | Resource provisioning, Container Apps, etc.   |
| **User Access Administrator** | Create role assignments           | Container Registry access, managed identities |

> **💡 Note**: User Access Administrator is needed because azd creates role assignments between services (e.g., Container Apps accessing Container Registry). This is a standard requirement for automated Azure deployments.

### 2. **Add GitHub Secrets**

1. Go to GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add each secret from the table above

### 3. **Test the Pipeline**

```bash
# Make a small change and push to master
git add .
git commit -m "feat: test CI/CD pipeline"
git push origin master

# Watch the pipeline run in GitHub Actions tab
```

## 🎯 **Pipeline Features**

### **Performance Optimizations**

- ⚡ **UV Package Manager**: 10-100x faster than pip
- 🗄️ **Docker Caching**: GitHub Actions cache for faster builds
- 🔄 **Parallel Jobs**: Tests and quality checks run simultaneously
- 📦 **Smart Dependencies**: Only installs needed extras per job

### **Quality Gates**

- 🧪 **Test Coverage**: Minimum 80% coverage required
- 🔍 **Code Quality**: Ruff linting with 20+ rule sets
- 🛡️ **Security**: Automated security vulnerability scanning
- 🐳 **Build Validation**: Docker images must build successfully
- ✅ **Health Checks**: Post-deployment endpoint validation

### **Developer Experience**

- 💬 **PR Comments**: Automatic feedback on code quality issues
- 📊 **Rich Reports**: Coverage reports, deployment summaries
- 🏷️ **Smart Labels**: Auto-categorized dependency updates
- 🔗 **Quick Links**: Direct links to deployed app and docs

## 🚦 **Workflow Triggers**

| Event            | Workflow       | Actions                                        |
| ---------------- | -------------- | ---------------------------------------------- |
| Push to `master` | Main CI/CD     | Test → Quality → Security → Build → **Deploy** |
| Pull Request     | PR Validation  | Test → Quality → Security → Build (no deploy)  |
| Manual Trigger   | Both workflows | Can be triggered manually from Actions tab     |

## 📈 **Monitoring & Reporting**

### **GitHub Actions Dashboard**

- **Actions Tab**: View all workflow runs and logs
- **Deployments**: Environment-specific deployment history
- **Security Tab**: Dependency vulnerability alerts

### **Coverage Reporting**

- **Codecov Integration**: Detailed coverage analysis and trends
- **HTML Reports**: Downloadable artifacts for line-by-line coverage
- **PR Comments**: Coverage change summaries on pull requests

### **Azure Monitoring**

- **Container Apps**: Application performance and logs
- **Application Insights**: Detailed telemetry and monitoring
- **Health Endpoints**: Automated health checks post-deployment

## 🔧 **Customization Options**

### **Adjust Coverage Threshold**

```yaml
# In ci-cd.yml, change --cov-fail-under value
uv run python -m pytest --cov=app --cov-fail-under=85 # Change from 80 to 85
```

### **Add More Linting Rules**

```toml
# In project/pyproject.toml, add rule sets
[tool.ruff.lint]
select = [
    "E", "W", "F", "UP", "B", "SIM", "I", "N", "C4",
    "DJ",  # Add Django rules
    "PD",  # Add pandas rules
]
```

### **Change Deployment Environment**

```yaml
# In ci-cd.yml, update environment
if: github.ref == 'refs/heads/master' # Change to 'main' if needed
environment: production # Change to 'staging' for staging deployments
```

### **Add Integration Tests**

```yaml
# Add after deployment step
- name: Run integration tests
  run: |
    curl -f "${{ steps.get-url.outputs.deployment-url }}/summaries/" 
    # Add more endpoint tests
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Azure Authentication Failures**

   - Verify service principal has Contributor role
   - Check secret values are correct (no extra spaces)
   - Ensure subscription ID matches your target subscription

2. **Test Database Issues**

   - PostgreSQL service takes time to start (health checks handle this)
   - Migration failures usually mean database connection issues

3. **Coverage Failures**

   - Run locally: `./scripts/lint.sh all && docker-compose exec web uv run python -m pytest --cov=app --cov-report=html`
   - Check `htmlcov/index.html` for uncovered lines

4. **Code Quality Failures**

   - Run locally: `./scripts/lint.sh all`
   - Commit the fixes and push again

5. **Docker Build Failures**
   - Usually lockfile issues: run `cd project && uv lock`
   - Check Dockerfile changes haven't broken the build

### **Getting Help**

- **GitHub Issues**: Report problems with detailed error logs
- **Actions Logs**: Click on failed jobs for detailed error messages
- **Azure Portal**: Check Container Apps logs for deployment issues

## 🎉 **Next Steps**

1. **Set up GitHub Secrets** using the helper script
2. **Push code to master** to test the full pipeline
3. **Monitor the deployment** in GitHub Actions
4. **Check your deployed app** in Azure Container Apps
5. **Create a PR** to test the validation workflow

Your FastAPI application now has enterprise-grade CI/CD! 🚀
