"""Snowflake接続設定モジュール。"""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_snowflake_credentials(env_path: Path | None = None) -> dict[str, str]:
    """.envファイルからSnowflakeの接続情報を読み込む。"""
    if env_path is None:
        env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path, override=True)

    return {
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "password": os.environ["SNOWFLAKE_PASSWORD"],
        "role": os.environ["SNOWFLAKE_ROLE"],
        "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
        "database": os.environ["SNOWFLAKE_DATABASE"],
        "schema": os.environ["SNOWFLAKE_SCHEMA"],
    }
