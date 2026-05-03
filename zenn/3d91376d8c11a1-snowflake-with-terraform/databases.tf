// Snowflake database definitions(追加で渡すプロパティはhttps://docs.snowflake.com/ja/sql-reference/sql/create-database を参照)
resource "snowflake_database" "sandbox_db" {
  name                        = "SANDBOX_DB"
  comment                     = "Terraform動作検証用の仮DB"
  data_retention_time_in_days = 1
}

resource "snowflake_database" "test_db" {
  name                        = "TEST_DB"
  data_retention_time_in_days = 1
}
