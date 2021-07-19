variable "prefix" {
    description = "The prefix used for all resources in this environment"
}
variable "location" {
    description = "The Azure location where all resources in this deployment should be created"
    default = "uksouth"
}

variable "resource_group" {
    default = "Capita1_LouisEgbufor_ProjectExercise"
}

variable "GITHUB_CLIENT_ID" { 
}

variable "GITHUB_CLIENT_SECRET" { 
}

variable "webapp" {     
}


variable "GITHUB_REDIRECT_URI" { 
}

variable "SECRET_KEY" {    
}

variable "OAUTHLIB_INSECURE_TRANSPORT" { 
    default = "1"
}

variable "ROLEWRITER_USER" {    
}

variable "docker_image" {
    default = "louiseg/todo-app:latest"
}
variable "cosmosdb_account" {}
variable "cosmosdb" {}
variable "geo_location" {
    default = "UK South"   
}
variable "ARM_ACCESS_KEY" {}
   

