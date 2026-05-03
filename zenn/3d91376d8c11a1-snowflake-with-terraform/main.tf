terraform {
  required_providers {
    snowflake = {
      source  = "snowflakedb/snowflake"
      version = "~> 2.14"
    }
  }
}

provider "snowflake" {
  organization_name = var.organization_name
  account_name      = var.account_name
  user              = var.snowflake_user
  role              = var.snowflake_role
  password          = var.snowflake_password
  authenticator     = "UsernamePasswordMFA"

  preview_features_enabled = [
    "snowflake_stage_internal_resource",
    "snowflake_table_resource",
    "snowflake_function_sql_resource",
    "snowflake_procedure_sql_resource",
  ]
}
