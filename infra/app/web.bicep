param name string
param location string = resourceGroup().location
param tags object = {}

param identityName string
param containerAppsEnvironmentName string
param containerRegistryName string
param databaseServiceName string
param exists bool

@description('Port used by the web service')
param port int = 8000

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
    exists: exists
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
        value: 'postgresql://postgres:postgres@${databaseServiceName}:5432/web_production'
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
    ], env)
    targetPort: exists ? port : 80  // Use port 80 for placeholder, 8000 for your app
  }
}

output defaultDomain string = app.outputs.defaultDomain
output identityPrincipalId string = webIdentity.properties.principalId
output name string = app.outputs.name
output uri string = app.outputs.uri
