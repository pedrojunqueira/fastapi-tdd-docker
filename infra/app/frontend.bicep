param name string
param location string = resourceGroup().location
param tags object = {}

param identityName string
param containerAppsEnvironmentName string
param containerRegistryName string

@description('Port used by the frontend service')
param port int = 80

resource frontendIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

module app '../core/host/container-app.bicep' = {
  name: '${name}-container-app'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': 'frontend' })
    identityName: frontendIdentity.name
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    containerCpuCoreCount: '0.5'
    containerMemory: '1Gi'
    containerName: 'frontend'
    containerMinReplicas: 1
    containerMaxReplicas: 5
    secrets: []
    env: []
    targetPort: port
  }
}

output defaultDomain string = app.outputs.defaultDomain
output identityPrincipalId string = frontendIdentity.properties.principalId
output name string = app.outputs.name
output uri string = app.outputs.uri
