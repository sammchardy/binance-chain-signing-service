variable "aws_region" {
  description = "The AWS region to create things in."
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "The AWS profile to authenticate with."
  default     = "default"
}

variable "ecs_task_execution_role" {
  description = "Role arn for the ecsTaskExecutionRole"
}

variable "app_image" {
  description = "Docker image to run in the ECS cluster"
}

variable "app_name" {
  description = "Short name of the app"
  default     = "bdex-sign"
}

variable "az_count" {
  description = "Number of AZs to cover in a given AWS region"
  default     = "2"
}


variable "app_port" {
  description = "Port exposed by the docker image to redirect traffic to"
  default = 80
}

variable "app_count" {
  description = "Number of docker containers to run"
  default     = 1
}


variable "health_check_path" {
  default = "/"
}

variable "fargate_cpu" {
  description = "Fargate instance CPU units to provision (1 vCPU = 1024 CPU units)"
  default     = "256"
}

variable "fargate_memory" {
  description = "Fargate instance memory to provision (in MiB)"
  default     = "512"
}
