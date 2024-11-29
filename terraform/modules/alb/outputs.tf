output "alb_sg_id" {
  value = aws_security_group.alb_sg.id
}

output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "flask_target_group_arn" {
  value = aws_lb_target_group.flask_target.arn
}
