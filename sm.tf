resource "aws_secretsmanager_secret" "master" {
  name_prefix = "${var.project}-${local.environment}-${var.name}-postgresql-master"
  tags = merge(var.tags, {
    Name        = "${var.project}-${local.environment}-${var.name}-sms-postgresql-master"
    Environment = "${var.project}-${local.environment}"
  })
}

resource "aws_secretsmanager_secret_version" "rds_admin" {
  secret_id = aws_secretsmanager_secret.master.id
  secret_string = jsonencode({
    username = var.db_master_username
    password = var.db_master_password
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

resource "aws_secretsmanager_secret" "user" {
  name_prefix = "${var.project}-${local.environment}-${var.name}-postgresql-user"
  tags = merge(var.tags, {
    Name        = "${var.project}-${local.environment}-${var.name}-sms-postgresql-user"
    Environment = "${var.project}-${local.environment}"
  })
}

resource "aws_secretsmanager_secret_version" "rds_user" {
  secret_id = aws_secretsmanager_secret.user.id
  secret_string = jsonencode({
    username = var.db_new_user_name
    password = uuid()
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

