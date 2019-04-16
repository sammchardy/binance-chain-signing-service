# Set up cloudwatch group and log stream and retain logs for 30 days
resource "aws_cloudwatch_log_group" "cw_log_group" {
  name              = "/ecs/${var.app_name}-app"
  retention_in_days = 30

  tags {
    Name = "${var.app_name}-log-group"
  }
}

resource "aws_cloudwatch_log_stream" "cw_log_stream" {
  name           = "${var.app_name}-log-stream"
  log_group_name = "${aws_cloudwatch_log_group.cw_log_group.name}"
}
