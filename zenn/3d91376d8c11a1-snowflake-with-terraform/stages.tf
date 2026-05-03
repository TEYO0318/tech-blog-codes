# Snowflake stage definitions(追加で渡すプロパティはhttps://docs.snowflake.com/ja/sql-reference/sql/create-stage を参照)

resource "snowflake_stage_internal" "sandbox_stage" {
  database = snowflake_database.sandbox_db.name
  schema   = "PUBLIC"
  name     = "SANDBOX_STAGE"
  comment  = "Terraform動作検証用の仮ステージ"
}
