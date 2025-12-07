targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@minLength(1)
@description('Name of the application')
param appName string = 'fastapi-tdd-docker'

@description('Name of the resource group. Leave empty to let azd generate one.')
param resourceGroupName string = ''

// Azure AD Configuration
@description('Azure AD Tenant ID')
param azureTenantId string = ''

@description('Azure AD API Client ID (backend)')
param apiClientId string = ''

@description('Azure AD Frontend Client ID (for OpenAPI/Swagger)')
param openApiClientId string = ''

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Generate secure passwords
var postgresPassword = uniqueString(subscription().id, environmentName, 'postgres-v1')

// Pre-compute URLs for cross-referencing
var webAppName = '${abbrs.appContainerApps}web-${resourceToken}'
var frontendAppName = '${abbrs.appContainerApps}frontend-${resourceToken}'

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${appName}-${environmentName}'
  location: location
  tags: tags
}

// The backend API
module web './app/web.bicep' = {
  name: 'web'
  scope: rg
  params: {
    name: webAppName
    location: location
    tags: tags
    identityName: '${abbrs.managedIdentityUserAssignedIdentities}web-${resourceToken}'
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    containerRegistryName: containerApps.outputs.registryName
    databaseServiceName: database.outputs.serviceName
    postgresPassword: postgresPassword
    corsOrigins: '["https://${frontendAppName}.${containerApps.outputs.defaultDomain}"]'
    tenantId: azureTenantId
    appClientId: apiClientId
    openApiClientId: openApiClientId
  }
}

// The React frontend application
module frontend './app/frontend.bicep' = {
  name: 'frontend'
  scope: rg
  params: {
    name: frontendAppName
    location: location
    tags: tags
    identityName: '${abbrs.managedIdentityUserAssignedIdentities}frontend-${resourceToken}'
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    containerRegistryName: containerApps.outputs.registryName
  }
}

// The application database (containerized PostgreSQL)
module database './app/database-container.bicep' = {
  name: 'database'
  scope: rg
  params: {
    name: '${abbrs.appContainerApps}db-${resourceToken}'
    location: location
    tags: tags
    identityName: '${abbrs.managedIdentityUserAssignedIdentities}db-${resourceToken}'
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    containerRegistryName: containerApps.outputs.registryName
    databaseName: 'web_production'
    postgresPassword: postgresPassword
  }
}

// Container apps host (including container registry)
module containerApps './core/host/container-apps.bicep' = {
  name: 'container-apps'
  scope: rg
  params: {
    name: 'app'
    location: location
    tags: tags
    containerAppsEnvironmentName: '${abbrs.appManagedEnvironments}${resourceToken}'
    containerRegistryName: '${abbrs.containerRegistryRegistries}${resourceToken}'
    logAnalyticsWorkspaceName: monitoring.outputs.logAnalyticsWorkspaceName
  }
}



// Monitor application with Azure Monitor
module monitoring './core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  scope: rg
  params: {
    location: location
    tags: tags
    logAnalyticsName: '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: '${abbrs.insightsComponents}${resourceToken}'
  }
}

// App outputs
output APPLICATIONINSIGHTS_CONNECTION_STRING string = monitoring.outputs.applicationInsightsConnectionString
output AZURE_CONTAINER_ENVIRONMENT_NAME string = containerApps.outputs.environmentName
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerApps.outputs.registryLoginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerApps.outputs.registryName

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output DATABASE_SERVICE_NAME string = database.outputs.serviceName
output WEB_URI string = web.outputs.uri
output FRONTEND_URI string = frontend.outputs.uri
