resource "aws_ecs_task_definition" "alb_app" {
  family                   = "alb-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "app"
      image = "hashicorp/http-echo:latest"

      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        }
      ]

      command = [
        "-text=ALB-APP-SERVICE: Successful response from ALB",
        "-listen=:8080"
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = local.aws_region
          "awslogs-stream-prefix" = "alb-app"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "alb_api" {
  family                   = "alb-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "api"
      image = "hashicorp/http-echo:latest"

      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        }
      ]

      command = [
        "-text=ALB-API-SERVICE: Successful response from ALB",
        "-listen=:8080"
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = local.aws_region
          "awslogs-stream-prefix" = "alb-api"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "alb_app" {
  name            = "alb-app"
  cluster         = aws_ecs_cluster.alb_nlb.id
  task_definition = aws_ecs_task_definition.alb_app.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups  = [aws_security_group.alb_ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.alb_app.arn
    container_name   = "app"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.alb_http]
}

resource "aws_ecs_service" "alb_api" {
  name            = "alb-api"
  cluster         = aws_ecs_cluster.alb_nlb.id
  task_definition = aws_ecs_task_definition.alb_api.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups  = [aws_security_group.alb_ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.alb_api.arn
    container_name   = "api"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.alb_http]
}

resource "aws_lb" "alb" {
  name               = "alb-app"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]

  enable_deletion_protection = false
  enable_http2               = true

}

resource "aws_lb_target_group" "alb_app" {
  name        = "alb-app-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = aws_vpc.alb_nlb.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
  }
}

resource "aws_lb_target_group" "alb_api" {
  name        = "alb-api-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = aws_vpc.alb_nlb.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
  }
}

resource "aws_lb_listener" "alb_http" {
  load_balancer_arn = aws_lb.alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.alb_app.arn
  }
}

resource "aws_lb_listener_rule" "alb_api_path" {
  listener_arn = aws_lb_listener.alb_http.arn
  priority     = 50

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.alb_api.arn
  }

  condition {
    path_pattern {
      values = ["/api/*", "/api"]
    }
  }
}

resource "aws_lb_listener_rule" "redirect_api" {
  listener_arn = aws_lb_listener.alb_http.arn
  priority     = 90

  action {
    type = "redirect"
    redirect {
      path        = "/api"
      status_code = "HTTP_301"
    }
  }

  condition {
    path_pattern {
      values = ["/redirect/*", "/redirect"]
    }
  }
}

resource "aws_lb_listener_rule" "forbidden" {
  listener_arn = aws_lb_listener.alb_http.arn
  priority     = 10

  action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "Access Denied: This resource is restricted"
      status_code  = "403"
    }
  }

  condition {
    path_pattern {
      values = ["/admin", "/admin/*"]
    }
  }
}
