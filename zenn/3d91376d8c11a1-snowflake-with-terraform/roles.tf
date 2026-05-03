# Snowflake role and grant definitions(追加で渡すプロパティはhttps://docs.snowflake.com/ja/sql-reference/sql/create-role を参照)
#!WARN: ロール作成はSecurity Adminロール以上の権限が必要です。
resource "snowflake_account_role" "sandbox_role" {
  name    = "SANDBOX_ROLE"
  comment = "SANDBOX_DB関連オブジェクトのみ操作可能なロール"
}

# SANDBOX_DB への権限
resource "snowflake_grant_privileges_to_account_role" "sandbox_db_usage" {
  privileges        = ["USAGE"]
  account_role_name = snowflake_account_role.sandbox_role.name
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.sandbox_db.name
  }
}

# SANDBOX_DB.PUBLIC スキーマへの権限
resource "snowflake_grant_privileges_to_account_role" "sandbox_schema_usage" {
  privileges        = ["USAGE", "CREATE TABLE", "CREATE STAGE"]
  account_role_name = snowflake_account_role.sandbox_role.name
  on_schema {
    schema_name = "\"${snowflake_database.sandbox_db.name}\".\"PUBLIC\""
  }
}

# SANDBOX_DB 内の全テーブルへの権限
resource "snowflake_grant_privileges_to_account_role" "sandbox_tables_all" {
  privileges        = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  account_role_name = snowflake_account_role.sandbox_role.name
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_database        = snowflake_database.sandbox_db.name
    }
  }
}

# SANDBOX_DB 内の全ステージへの権限
resource "snowflake_grant_privileges_to_account_role" "sandbox_stages_all" {
  privileges        = ["READ", "WRITE"]
  account_role_name = snowflake_account_role.sandbox_role.name
  on_schema_object {
    all {
      object_type_plural = "STAGES"
      in_database        = snowflake_database.sandbox_db.name
    }
  }
}

# SANDBOX_WH への権限
resource "snowflake_grant_privileges_to_account_role" "sandbox_wh_usage" {
  privileges        = ["USAGE"]
  account_role_name = snowflake_account_role.sandbox_role.name
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.sandbox_wh.name
  }
}

# SYSADMINへのロール階層付与
resource "snowflake_grant_account_role" "sandbox_to_sysadmin" {
  role_name        = snowflake_account_role.sandbox_role.name
  parent_role_name = "SYSADMIN"
}
