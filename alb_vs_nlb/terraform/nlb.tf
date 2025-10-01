resource "aws_ecs_service" "nlb_app" {
  name            = "nlb-app"
  cluster         = aws_ecs_cluster.alb_nlb.id
  task_definition = aws_ecs_task_definition.nlb_app.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups  = [aws_security_group.nlb_ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.nlb_tcp.arn
    container_name   = "nlb-app"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.nlb_tcp]
}

resource "aws_ecs_task_definition" "nlb_app" {
  family                   = "nlb-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "nlb-app"
      image = "hashicorp/http-echo:latest"

      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        }
      ]

      command = [
        "-text=NLB-APP-SERVICE: Successful response from NLB",
        "-listen=:8080"
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = local.aws_region
          "awslogs-stream-prefix" = "nlb-app"
        }
      }
    }
  ])
}


resource "aws_lb" "nlb" {
  name               = "nlb"
  internal           = false
  load_balancer_type = "network"
  security_groups    = [aws_security_group.nlb.id]

  subnet_mapping {
    subnet_id     = aws_subnet.public_1.id
    allocation_id = aws_eip.nlb_1.id
  }

  subnet_mapping {
    subnet_id     = aws_subnet.public_2.id
    allocation_id = aws_eip.nlb_2.id
  }

  enable_deletion_protection       = false
  enable_cross_zone_load_balancing = false
}

resource "aws_lb_target_group" "nlb_tcp" {
  name        = "nlb-tcp-tg"
  port        = 8080
  protocol    = "TCP"
  vpc_id      = aws_vpc.alb_nlb.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    protocol            = "TCP"
  }

  preserve_client_ip = true
}

resource "aws_lb_listener" "nlb_tcp" {
  load_balancer_arn = aws_lb.nlb.arn
  port              = "80"
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.nlb_tcp.arn
  }
}
