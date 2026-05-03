# Snowflake table definitions

resource "snowflake_table" "sandbox_table" {
  database                    = snowflake_database.sandbox_db.name
  schema                      = "PUBLIC"
  name                        = "SANDBOX_TABLE"
  data_retention_time_in_days = 1

  column {
    name = "ID"
    type = "NUMBER(38,0)"
  }

  column {
    name = "NAME"
    type = "VARCHAR(255)"
  }

  column {
    name = "CREATED_AT"
    type = "TIMESTAMP_NTZ(9)"
  }
}
