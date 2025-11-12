#!/bin/bash

# GitHub Actions Azure Setup Helper Script
# This script helps you create the Azure Service Principal and provides the values needed for GitHub secrets

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Azure CLI is installed
check_azure_cli() {
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed. Please install it first:"
        echo "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    print_success "Azure CLI is installed"
}

# Check if user is logged in to Azure
check_azure_login() {
    if ! az account show &> /dev/null; then
        print_warning "You are not logged in to Azure. Please run 'az login' first."
        echo "Would you like to log in now? (y/n)"
        read -r response
        if [[ $response =~ ^[Yy]$ ]]; then
            az login
        else
            exit 1
        fi
    fi
    print_success "Logged in to Azure"
}

# Show current subscription
show_subscription() {
    print_header "Current Azure Subscription"
    SUBSCRIPTION_INFO=$(az account show)
    SUBSCRIPTION_ID=$(echo "$SUBSCRIPTION_INFO" | jq -r '.id')
    SUBSCRIPTION_NAME=$(echo "$SUBSCRIPTION_INFO" | jq -r '.name')
    TENANT_ID=$(echo "$SUBSCRIPTION_INFO" | jq -r '.tenantId')
    
    echo "Subscription ID: $SUBSCRIPTION_ID"
    echo "Subscription Name: $SUBSCRIPTION_NAME"
    echo "Tenant ID: $TENANT_ID"
    echo
    
    echo "Is this the correct subscription? (y/n)"
    read -r response
    if [[ ! $response =~ ^[Yy]$ ]]; then
        print_info "List available subscriptions:"
        az account list --output table
        echo
        echo "Enter the subscription ID you want to use:"
        read -r NEW_SUBSCRIPTION_ID
        az account set --subscription "$NEW_SUBSCRIPTION_ID"
        print_success "Subscription changed"
        
        # Get updated info
        SUBSCRIPTION_INFO=$(az account show)
        SUBSCRIPTION_ID=$(echo "$SUBSCRIPTION_INFO" | jq -r '.id')
        TENANT_ID=$(echo "$SUBSCRIPTION_INFO" | jq -r '.tenantId')
    fi
}

# Create service principal
create_service_principal() {
    print_header "Creating Azure Service Principal"
    
    SP_NAME="github-actions-fastapi-tdd-$(date +%s)"
    
    print_info "Creating service principal: $SP_NAME"
    print_info "This may take a moment..."
    
    SP_OUTPUT=$(az ad sp create-for-rbac \
        --name "$SP_NAME" \
        --role contributor \
        --scopes "/subscriptions/$SUBSCRIPTION_ID" \
        --output json)
    
    CLIENT_ID=$(echo "$SP_OUTPUT" | jq -r '.appId')
    CLIENT_SECRET=$(echo "$SP_OUTPUT" | jq -r '.password')
    
    print_success "Service principal created successfully!"
    
    print_info "Adding User Access Administrator role for Azure deployment permissions..."
    az role assignment create \
        --assignee "$CLIENT_ID" \
        --role "User Access Administrator" \
        --scope "/subscriptions/$SUBSCRIPTION_ID" \
        --output none
    
    print_success "Additional permissions configured successfully!"
}

# Display GitHub secrets
display_secrets() {
    print_header "GitHub Repository Secrets"
    print_info "Add these secrets to your GitHub repository:"
    print_info "Repository → Settings → Secrets and variables → Actions → New repository secret"
    echo
    
    echo "╔══════════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                                  GITHUB SECRETS                                      ║"
    echo "╠══════════════════════════════════════════════════════════════════════════════════════╣"
    echo "║                                                                                      ║"
    printf "║ %-25s │ %-50s ║\n" "Secret Name" "Secret Value"
    echo "║                                                                                      ║"
    echo "╠══════════════════════════════════════════════════════════════════════════════════════╣"
    printf "║ %-25s │ %-50s ║\n" "AZURE_CLIENT_ID" "$CLIENT_ID"
    printf "║ %-25s │ %-50s ║\n" "AZURE_CLIENT_SECRET" "$CLIENT_SECRET"
    printf "║ %-25s │ %-50s ║\n" "AZURE_TENANT_ID" "$TENANT_ID"
    printf "║ %-25s │ %-50s ║\n" "AZURE_SUBSCRIPTION_ID" "$SUBSCRIPTION_ID"
    echo "║                                                                                      ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════════════╝"
    echo
    
    print_warning "IMPORTANT: Save these values securely! The client secret cannot be retrieved again."
    print_info "Optional: Add CODECOV_TOKEN secret for coverage reporting (get from codecov.io)"
}

# Save to file option
save_to_file() {
    echo
    echo "Would you like to save these values to a secure file? (y/n)"
    read -r response
    if [[ $response =~ ^[Yy]$ ]]; then
        SECRETS_FILE="github-secrets-$(date +%Y%m%d-%H%M%S).txt"
        cat > "$SECRETS_FILE" << EOF
# GitHub Actions Secrets for FastAPI TDD Docker Project
# Created: $(date)
# Service Principal: $SP_NAME

AZURE_CLIENT_ID=$CLIENT_ID
AZURE_CLIENT_SECRET=$CLIENT_SECRET
AZURE_TENANT_ID=$TENANT_ID
AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID

# Instructions:
# 1. Go to GitHub repository → Settings → Secrets and variables → Actions
# 2. Click "New repository secret" for each secret above
# 3. Delete this file after adding secrets to GitHub

# Optional secrets:
# CODECOV_TOKEN=<get from codecov.io for coverage reporting>
EOF
        chmod 600 "$SECRETS_FILE"
        print_success "Secrets saved to: $SECRETS_FILE"
        print_warning "Remember to delete this file after adding secrets to GitHub!"
    fi
}

# Test Azure deployment (optional)
test_deployment() {
    echo
    echo "Would you like to test Azure deployment locally first? (y/n)"
    read -r response
    if [[ $response =~ ^[Yy]$ ]]; then
        print_info "Testing local Azure deployment..."
        print_info "This will run 'azd up' to verify everything works"
        
        export AZURE_CLIENT_ID="$CLIENT_ID"
        export AZURE_CLIENT_SECRET="$CLIENT_SECRET"
        export AZURE_TENANT_ID="$TENANT_ID"
        export AZURE_SUBSCRIPTION_ID="$SUBSCRIPTION_ID"
        
        echo "Proceeding with azd up..."
        if azd up --no-prompt; then
            print_success "Local deployment test successful!"
            print_info "Your CI/CD pipeline should work correctly"
        else
            print_warning "Local deployment had issues. Please check the configuration."
        fi
    fi
}

# Main function
main() {
    print_header "FastAPI TDD Docker - GitHub Actions Azure Setup"
    print_info "This script will help you set up Azure authentication for GitHub Actions"
    echo
    
    # Checks
    check_azure_cli
    check_azure_login
    
    # Setup
    show_subscription
    create_service_principal
    
    # Display results
    display_secrets
    save_to_file
    test_deployment
    
    print_header "Setup Complete!"
    print_success "Your GitHub Actions CI/CD pipeline is ready to use!"
    print_info "Next steps:"
    echo "1. Add the secrets to your GitHub repository"
    echo "2. Push code to master branch to trigger the pipeline"
    echo "3. Monitor the deployment in GitHub Actions tab"
    echo "4. Check your deployed application in Azure Container Apps"
    echo
    print_info "Need help? Check the README.md CI/CD section for troubleshooting."
}

# Run main function
main "$@"