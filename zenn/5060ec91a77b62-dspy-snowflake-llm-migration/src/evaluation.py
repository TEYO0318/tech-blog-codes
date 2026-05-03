"""評価メトリクスモジュール。"""

import dspy


class SemanticJudge(dspy.Signature):
    """予測された分類結果が正解と意味的に同等か判定する。"""

    field_name = dspy.InputField(desc="評価対象のフィールド名")
    ground_truth = dspy.InputField(desc="正解値")
    prediction = dspy.InputField(desc="予測値")
    is_equivalent: bool = dspy.OutputField(
        desc="意味的に同等ならTrue、そうでなければFalse"
    )


def validate_label_exact(
    example: dspy.Example, pred: dspy.Prediction, trace: object = None
) -> bool:
    """感情ラベルの完全一致による評価。"""
    return _normalize(pred.label) == _normalize(example.label)


def create_semantic_metric(judge_lm: dspy.LM) -> callable:
    """セマンティック類似度による評価メトリクスを生成する。"""
    judge = dspy.ChainOfThought(SemanticJudge)

    def semantic_metric(
        example: dspy.Example, pred: dspy.Prediction, trace: object = None
    ) -> float:
        """感情ラベルをセマンティック評価し、スコアを返す。"""
        with dspy.context(lm=judge_lm):
            result = judge(
                field_name="label",
                ground_truth=example.label,
                prediction=pred.label,
            )
            return 1.0 if "true" in str(result.is_equivalent).lower() else 0.0

    return semantic_metric


def _normalize(text: str) -> str:
    """テキストを正規化する（前後空白除去、小文字化）。"""
    return text.strip().lower()
