"""Snowflakeデータローダーモジュール。"""

import dspy
from snowflake.snowpark import Session

# TODO: テーブル名は環境に合わせて変更してください
GROUND_TRUTH_TABLE = "SANDBOX_DB.PUBLIC.GROUND_TRUTH_DATA"
TEST_TABLE = "SANDBOX_DB.PUBLIC.TEST_DATA"
RESULT_TABLE = "SANDBOX_DB.PUBLIC.TEST_RESULT"


def load_ground_truth(session: Session, limit: int | None = None) -> list[dspy.Example]:
    """正解データをDSPy Exampleとして読み込む。"""
    sql = f"""
        SELECT TITLE, CONTENT, LABEL
        FROM {GROUND_TRUTH_TABLE}
        WHERE LABEL IS NOT NULL
    """
    if limit is not None:
        sql += f" LIMIT {limit}"

    rows = session.sql(sql).collect()
    examples = []
    for row in rows:
        example = dspy.Example(
            title=row["TITLE"] or "",
            content=row["CONTENT"] or "",
            label=row["LABEL"] or "",
        ).with_inputs("title", "content")
        examples.append(example)
    return examples


def save_results(
    session: Session,
    results: list[dict[str, str]],
) -> None:
    """分類結果をSnowflakeの結果テーブルに書き込む。"""
    if not results:
        return

    df = session.create_dataframe(
        results,
        schema=["TITLE", "LABEL"],
    )
    df.write.mode("overwrite").save_as_table(RESULT_TABLE)
