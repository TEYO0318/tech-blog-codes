import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    # marimoの仕様上変数をセルに渡す場合はtupleにする必要がある為、tupleにする
    return (mo,)


@app.cell
def _():
    """1. 接続設定・LM初期化"""
    from snowflake.snowpark import Session
    from src.snowflake_config import load_snowflake_credentials
    from src.snowflake_lm import SnowflakeCortexLM

    import dspy

    creds = load_snowflake_credentials()
    snowpark = Session.builder.configs(creds).create()

    mistral = SnowflakeCortexLM(session=snowpark, model="mistral-large2")
    dspy.configure(lm=mistral)

    print("Snowflake接続完了 / LM設定完了")
    return (snowpark,)


@app.cell
def _(snowpark):
    """2. データ読み込み・分割"""
    from src.retriever import load_ground_truth

    all_data = load_ground_truth(snowpark)
    print(f"正解データ件数: {len(all_data)}")

    split_idx = int(len(all_data) * 0.8)
    train_set = all_data[:split_idx]
    validation_set = all_data[split_idx:]
    print(f"Train: {len(train_set)}件, Validation: {len(validation_set)}件")
    return train_set, validation_set


@app.cell
def _(validation_set):
    """3. サンプル1件で動作確認"""
    from src.signatures import SentimentClassifier

    classifier = SentimentClassifier()
    sample = validation_set[0]
    result = classifier(title=sample.title, content=sample.content)

    print(f"タイトル: {sample.title[:80]}...")
    print(f"予測 label: {result.label}")
    print(f"正解 label: {sample.label}")
    return (SentimentClassifier,)


@app.cell
def _(SentimentClassifier, validation_set):
    """4. 最適化前の評価（Label Exact Match）"""
    from dspy.evaluate import Evaluate
    from src.evaluation import validate_label_exact

    evaluate = Evaluate(
        devset=validation_set, num_threads=1, display_progress=True, display_table=5
    )

    label_score = evaluate(SentimentClassifier(), validate_label_exact)
    print(f"Label Exact Match: {label_score}")
    return evaluate, label_score, validate_label_exact


@app.cell
def _(SentimentClassifier, evaluate, snowpark):
    """5. 最適化前の評価（Semantic Similarity）"""
    from src.evaluation import create_semantic_metric
    from src.snowflake_lm import SnowflakeCortexLM as _LM

    # 評価対象と同じモデルで評価するとバイアスがかかるため、別モデル(Claude)を使用
    judge_lm = _LM(session=snowpark, model="claude-3-5-sonnet")
    semantic_metric = create_semantic_metric(judge_lm=judge_lm)
    semantic_score = evaluate(SentimentClassifier(), semantic_metric)
    print(f"Semantic Score: {semantic_score}")
    return (semantic_score,)


@app.cell
def _(SentimentClassifier, evaluate, train_set, validate_label_exact):
    """6. パイプライン最適化（BootstrapFewShot）"""
    from dspy.teleprompt import BootstrapFewShot

    optimizer = BootstrapFewShot(
        metric=validate_label_exact,
        max_bootstrapped_demos=3,  # 評価をする際にデモ用のデータを3件組み込む
    )
    optimized = optimizer.compile(SentimentClassifier(), trainset=train_set)

    optimized_score = evaluate(optimized, validate_label_exact)
    print(f"Optimized Label Score: {optimized_score}")
    return optimized, optimized_score


@app.cell
def _(optimized):
    """7. 最適化済みパイプラインの保存"""
    optimized.save("optimized_classifier.json")
    print("optimized_classifier.json に保存しました。")
    return


@app.cell
def _(optimized, snowpark, validation_set):
    """8. 結果をSnowflakeに保存"""
    from src.retriever import save_results

    classification_results = []
    for example in validation_set:
        pred = optimized(title=example.title, content=example.content)
        classification_results.append(
            {
                "TITLE": example.title,
                "LABEL": pred.label,
            }
        )
    save_results(snowpark, classification_results)
    print(f"{len(classification_results)}件の結果を保存しました。")
    return


@app.cell
def _(label_score, mo, optimized_score, semantic_score):
    """結果サマリ"""
    mo.md(f"""
    | メトリクス | スコア |
    | :--- | :--- |
    | Label Exact Match | {label_score} |
    | Semantic Score | {semantic_score} |
    | Optimized Label | {optimized_score} |
    """)
    return


if __name__ == "__main__":
    app.run()
