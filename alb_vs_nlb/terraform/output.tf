output "alb_dns" {
  value       = aws_lb.alb.dns_name
  description = "ALB DNS name"
}

output "nlb_dns" {
  value       = aws_lb.nlb.dns_name
  description = "NLB DNS name"
}

output "nlb_static_ip_1" {
  value       = aws_eip.nlb_1.public_ip
  description = "NLB Static IP (AZ1)"
}

output "nlb_static_ip_2" {
  value       = aws_eip.nlb_2.public_ip
  description = "NLB Static IP (AZ2)"
}

output "cluster_name" {
  value       = aws_ecs_cluster.alb_nlb.name
  description = "ECS Cluster name"
}

output "vpc_id" {
  value       = aws_vpc.alb_nlb.id
  description = "VPC ID"
}
