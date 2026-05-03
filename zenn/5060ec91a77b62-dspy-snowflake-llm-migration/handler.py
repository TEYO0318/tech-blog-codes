"""DSPy + Snowflake Cortex を使ったLLM移行パイプラインのメインハンドラ。"""

import dspy
from dspy.evaluate import Evaluate
from dspy.teleprompt import BootstrapFewShotWithRandomSearch
from snowflake.snowpark import Session

from src.evaluation import (
    create_semantic_metric,
    validate_label_exact,
)
from src.retriever import load_ground_truth, save_results
from src.signatures import SentimentClassifier
from src.snowflake_config import load_snowflake_credentials
from src.snowflake_lm import SnowflakeCortexLM


def main() -> None:
    """メイン実行関数。"""
    # [Snowflake固有] 接続設定
    # 他のLLMプロバイダを使う場合はこのブロックを差し替えてください
    creds = load_snowflake_credentials()
    snowpark = Session.builder.configs(creds).create()

    # [Snowflake固有] Cortex LM 設定
    # 他のプロバイダの場合は dspy.LM("openai/gpt-4o") 等に置き換え可能
    mistral = SnowflakeCortexLM(session=snowpark, model="mistral-large2")
    dspy.configure(lm=mistral)

    # --- データ読み込み ---
    print("=== データ読み込み ===")
    all_data = load_ground_truth(snowpark)
    print(f"正解データ件数: {len(all_data)}")

    # train / dev 分割（8:2）
    split_idx = int(len(all_data) * 0.8)
    trainset = all_data[:split_idx]
    devset = all_data[split_idx:]
    print(f"Train: {len(trainset)}件, Dev: {len(devset)}件")

    # --- パイプラインテスト（サンプル1件） ---
    print("\n=== 分類テスト（サンプル1件） ===")
    classifier = SentimentClassifier()
    sample = devset[0]
    result = classifier(title=sample.title, content=sample.content)
    print(f"タイトル: {sample.title[:80]}...")
    print(f"予測 label: {result.label}")
    print(f"正解 label: {sample.label}")

    # --- 評価 ---
    print("\n=== 評価（devset） ===")
    evaluate = Evaluate(
        devset=devset, num_threads=1, display_progress=True, display_table=5
    )

    print("\n--- Label Exact Match ---")
    label_score = evaluate(SentimentClassifier(), validate_label_exact)
    print(f"Label Exact Match: {label_score}")

    # [Snowflake固有] セマンティック評価用LMの生成
    # 評価対象と同じモデルで評価するとバイアスがかかるため、別モデル(Claude)を使用
    print("\n--- Semantic Similarity ---")
    judge_lm = SnowflakeCortexLM(session=snowpark, model="claude-3-5-sonnet")
    semantic_metric = create_semantic_metric(judge_lm=judge_lm)
    semantic_score = evaluate(SentimentClassifier(), semantic_metric)
    print(f"Semantic Score: {semantic_score}")

    # --- パイプライン最適化 ---
    print("\n=== パイプライン最適化 ===")
    optimizer = BootstrapFewShotWithRandomSearch(
        metric=validate_label_exact,
        num_candidate_programs=1,
        max_bootstrapped_demos=1,
    )
    optimized = optimizer.compile(SentimentClassifier(), trainset=trainset)

    print("\n--- Optimized Pipeline ---")
    optimized_score = evaluate(optimized, validate_label_exact)
    print(f"Optimized Label Score: {optimized_score}")

    # --- 最適化パイプラインの保存 ---
    optimized.save("optimized_classifier.json")
    print("\n最適化済みパイプラインを optimized_classifier.json に保存しました。")

    # [Snowflake固有] 結果をテーブルに保存
    print("\n=== 結果をSnowflakeに保存 ===")
    classification_results = []
    for example in devset:
        pred = optimized(title=example.title, content=example.content)
        classification_results.append(
            {
                "TITLE": example.title,
                "LABEL": pred.label,
            }
        )
    save_results(snowpark, classification_results)
    print(f"{len(classification_results)}件の結果を保存しました。")

    # --- 結果サマリ ---
    print("\n=== 結果サマリ ===")
    print(f"Label Exact Match:         {label_score}")
    print(f"Semantic Score:            {semantic_score}")
    print(f"Optimized Label:           {optimized_score}")

    snowpark.close()


if __name__ == "__main__":
    main()
