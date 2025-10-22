param name string
param location string = resourceGroup().location
param tags object = {}

param identityName string
param containerAppsEnvironmentName string
param containerRegistryName string
param containerCpuCoreCount string = '0.5'
param containerMemory string = '1Gi'
param containerName string
param containerMinReplicas int = 1
param containerMaxReplicas int = 3
param secrets array = []
param env array = []
param targetPort int = 8000
param isInternalOnly bool = false
param volumes array = []
param transport string = 'http'
param containerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

resource userIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: identityName
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' existing = {
  name: containerAppsEnvironmentName
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' existing = {
  name: containerRegistryName
}

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${userIdentity.id}': {} }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: targetPort > 0 ? {
        external: !isInternalOnly
        targetPort: targetPort
        transport: transport
        allowInsecure: false
      } : null
      registries: [
        {
          server: containerRegistry.properties.loginServer
          identity: userIdentity.id
        }
      ]
      secrets: secrets
    }
    template: {
      containers: [
        {
          image: containerImage
          name: containerName
          env: env
          resources: {
            cpu: json(containerCpuCoreCount)
            memory: containerMemory
          }
        }
      ]
      scale: {
        minReplicas: containerMinReplicas
        maxReplicas: containerMaxReplicas
      }
      volumes: volumes
    }
  }
}

// Grant the container app's identity with access to the container registry
resource containerRegistryRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: containerRegistry
  name: guid(subscription().id, resourceGroup().id, userIdentity.id, 'acrpull')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalType: 'ServicePrincipal'
    principalId: userIdentity.properties.principalId
  }
}

output defaultDomain string = containerApp.properties.configuration.ingress.fqdn
output name string = containerApp.name
output uri string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
