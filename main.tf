terraform {
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = ">= 2.49"
        }
    }

    backend "azurerm" {
        resource_group_name  = "Capita1_LouisEgbufor_ProjectExercise"
        storage_account_name = "tfstate5353"
        container_name       = "tfstate"
        key                  = "terraform.tfstate"
    }
}


provider "azurerm" {
    features {}
}


data "azurerm_resource_group" "main" {
    name = var.resource_group       
}

resource "azurerm_app_service_plan" "main" {
    name = "${var.prefix}-terraformed-asp"
    location = var.location
    resource_group_name = data.azurerm_resource_group.main.name
    kind = "Linux"
    per_site_scaling = false    
    reserved = true
    sku {
        tier = "Basic"
        size = "B1"
    }
}
resource "azurerm_app_service" "main" {
    name = var.webapp
    location = data.azurerm_resource_group.main.location
    resource_group_name = data.azurerm_resource_group.main.name
    app_service_plan_id = azurerm_app_service_plan.main.id
    site_config {
        app_command_line = ""
        linux_fx_version = "DOCKER|${var.docker_image}"
    }
    app_settings = {
        "DOCKER_REGISTRY_SERVER_URL" = "https://index.docker.io"
        "MONGO_USERNAME" = azurerm_cosmosdb_account.main.name
        "MONGO_PASSWORD" = azurerm_cosmosdb_account.main.primary_key
        "MONGO_DB" = azurerm_cosmosdb_mongo_database.main.name
        "MONGO_URL" = "${var.cosmosdb_account}.mongo.cosmos.azure.com:10255"
        "MONGO_OPTIONS" = "ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000"
        "GITHUB_CLIENT_ID" = var.GITHUB_CLIENT_ID
        "GITHUB_CLIENT_SECRET" = var.GITHUB_CLIENT_SECRET
        "ROLEWRITER_USER" = var.ROLEWRITER_USER
        "GITHUB_REDIRECT_URI" = var.GITHUB_REDIRECT_URI
        "OAUTHLIB_INSECURE_TRANSPORT" = var.OAUTHLIB_INSECURE_TRANSPORT
        "SECRET_KEY"                  = var.SECRET_KEY
    }
    
}

resource "azurerm_cosmosdb_account" "main" {
  name                = var.cosmosdb_account
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "MongoDB"

  capabilities        {
    name = "EnableServerless"
  }

  capabilities { 
      name ="EnableMongo" 
      }

   geo_location {
    location          = var.geo_location
    failover_priority = 0
  }

  consistency_policy {
            consistency_level = "Session"            
        }
}

resource "azurerm_cosmosdb_mongo_database" "main" {
  name                = var.cosmosdb
  resource_group_name = data.azurerm_resource_group.main.name
  account_name        = var.cosmosdb_account
  lifecycle { prevent_destroy = true }
}