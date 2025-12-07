param name string
param location string = resourceGroup().location
param tags object = {}

param identityName string
param containerAppsEnvironmentName string
param containerRegistryName string
param databaseServiceName string

@secure()
@description('PostgreSQL password')
param postgresPassword string

@description('Port used by the web service')
param port int = 8000

@description('CORS origins for the web service')
param corsOrigins string = ''

@description('Azure AD Tenant ID')
param tenantId string = ''

@description('Azure AD App Client ID')
param appClientId string = ''

@description('Azure AD Frontend Client ID (for OpenAPI/Swagger)')
param openApiClientId string = ''

@description('Environment variables for the web service')
param env array = []

resource webIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

module app '../core/host/container-app.bicep' = {
  name: '${name}-container-app'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': 'web' })
    identityName: webIdentity.name
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    containerCpuCoreCount: '1.0'
    containerMemory: '2Gi'
    containerName: 'web'
    containerMinReplicas: 1
    containerMaxReplicas: 10
    secrets: []
    env: union([
      {
        name: 'DATABASE_URL'
        value: 'postgres://postgres:${postgresPassword}@${databaseServiceName}:5432/web_production'
      }
      {
        name: 'ENVIRONMENT'
        value: 'production'
      }
      {
        name: 'TESTING'
        value: '0'
      }
      {
        name: 'PORT'
        value: string(port)
      }
      {
        name: 'BACKEND_CORS_ORIGINS'
        value: corsOrigins
      }
      {
        name: 'TENANT_ID'
        value: tenantId
      }
      {
        name: 'APP_CLIENT_ID'
        value: appClientId
      }
      {
        name: 'OPENAPI_CLIENT_ID'
        value: openApiClientId
      }
    ], env)
    targetPort: port  // Use the configured port (8000) for FastAPI
  }
}

output defaultDomain string = app.outputs.defaultDomain
output identityPrincipalId string = webIdentity.properties.principalId
output name string = app.outputs.name
output uri string = app.outputs.uri
