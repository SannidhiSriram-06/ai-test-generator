terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

resource "aws_ecr_repository" "ai_test_generator" {
  name                 = "ai-test-generator"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "ai_test_generator" {
  repository = aws_ecr_repository.ai_test_generator.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 10 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
      action = {
        type = "expire"
      }
    }]
  })
}

output "repository_url" {
  value       = aws_ecr_repository.ai_test_generator.repository_url
  description = "ECR repository URL for tagging and pushing images"
}