param name string
param location string = resourceGroup().location
param tags object = {}

param identityName string
param containerAppsEnvironmentName string
param containerRegistryName string

@description('PostgreSQL database name')
param databaseName string = 'web_production'



resource dbIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

module containerApp '../core/host/container-app.bicep' = {
  name: '${name}-container-app'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': 'database' })
    identityName: dbIdentity.name
    exists: true  // Use existing PostgreSQL image, not custom build
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    containerCpuCoreCount: '0.5'
    containerMemory: '1Gi'
    containerName: 'postgres'
    containerMinReplicas: 1
    containerMaxReplicas: 1
    secrets: []
    env: [
      {
        name: 'POSTGRES_USER'
        value: 'postgres'
      }
      {
        name: 'POSTGRES_PASSWORD'
        value: 'postgres'
      }
      {
        name: 'POSTGRES_DB'
        value: databaseName
      }
    ]
    targetPort: 5432
    isInternalOnly: true  // Database should not be externally accessible
  }
}

// Connection string will be constructed by the web app using service name
output identityPrincipalId string = dbIdentity.properties.principalId
output name string = containerApp.outputs.name
output serviceName string = name
