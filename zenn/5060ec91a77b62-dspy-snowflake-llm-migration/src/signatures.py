"""DSPy Signature & Module定義。"""

import dspy


class ClassifySentiment(dspy.Signature):
    """Amazonレビューのタイトルと本文を分析し、感情ラベルを返す。"""

    title = dspy.InputField(desc="Amazonレビューのタイトル")
    content = dspy.InputField(desc="Amazonレビューの本文")
    label = dspy.OutputField(
        desc="レビューの感情を '1'(positive) または '0'(negative) で返す"
    )


class SentimentClassifier(dspy.Module):
    """感情分類パイプライン。ChainOfThoughtを使用。"""

    def __init__(self) -> None:
        super().__init__()
        self.classify = dspy.ChainOfThought(ClassifySentiment)

    def forward(self, title: str, content: str) -> dspy.Prediction:
        """Amazonレビューの感情を分類する。"""
        result = self.classify(title=title, content=content)
        return dspy.Prediction(
            label=result.label,
        )
