# Snowflake warehouse definitions(追加で渡すプロパティはhttps://docs.snowflake.com/ja/sql-reference/sql/create-warehouse を参照)

resource "snowflake_warehouse" "sandbox_wh" {
  name           = "SANDBOX_WH"
  warehouse_size = "XSMALL"
  warehouse_type = "STANDARD"
  auto_suspend   = 60
  auto_resume    = true
  comment        = "Terraform動作検証用の仮WH"
}
