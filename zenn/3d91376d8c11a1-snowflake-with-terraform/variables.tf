variable "organization_name" {
  description = "Snowflake organization name"
  type        = string
}

variable "account_name" {
  description = "Snowflake account name"
  type        = string
}

variable "snowflake_user" {
  description = "Snowflake username"
  type        = string
}

variable "snowflake_role" {
  description = "Snowflake role"
  type        = string
  default     = "SYSADMIN"
}

variable "snowflake_password" {
  description = "Snowflake password"
  type        = string
  sensitive   = true
}
