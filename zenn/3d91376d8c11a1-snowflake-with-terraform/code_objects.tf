# Snowflake code objects (tasks, functions, procedures)
# SQL files are stored in code_objects/ directory, organized by language.
#
# code_objects/
#   sql/
#     tasks/       ... SQLタスク定義
#     functions/   ... SQL UDF
#     procedures/  ... SQLストアドプロシージャ
#   python/
#     tasks/       ... Pythonタスク定義
#     functions/   ... Python UDF
#     procedures/  ... Pythonストアドプロシージャ
#   javascript/
#     tasks/       ... JavaScriptタスク定義
#     functions/   ... JavaScript UDF
#     procedures/  ... JavaScriptストアドプロシージャ

# --- Tasks ---

resource "snowflake_task" "sandbox_task" {
  database      = snowflake_database.sandbox_db.name
  schema        = "PUBLIC"
  name          = "SANDBOX_TASK"
  warehouse     = snowflake_warehouse.sandbox_wh.name
  started       = false
  sql_statement = file("${path.module}/code_objects/sql/tasks/sandbox_task.sql")
  comment       = "Terraform動作検証用の仮タスク"

  schedule {
    minutes = 60
  }
}

# --- Functions ---

resource "snowflake_function_sql" "sandbox_function" {
  database            = snowflake_database.sandbox_db.name
  schema              = "PUBLIC"
  name                = "SANDBOX_FUNCTION"
  return_type         = "VARCHAR"
  return_results_behavior = "IMMUTABLE"
  function_definition = file("${path.module}/code_objects/sql/functions/sandbox_function.sql")
  comment             = "Terraform動作検証用の仮UDF"

  arguments {
    arg_name      = "INPUT_TEXT"
    arg_data_type = "VARCHAR"
  }
}

# --- Procedures ---

resource "snowflake_procedure_sql" "sandbox_procedure" {
  database             = snowflake_database.sandbox_db.name
  schema               = "PUBLIC"
  name                 = "SANDBOX_PROCEDURE"
  return_type          = "VARCHAR"
  procedure_definition = file("${path.module}/code_objects/sql/procedures/sandbox_procedure.sql")
  comment              = "Terraform動作検証用の仮プロシージャ"
}
