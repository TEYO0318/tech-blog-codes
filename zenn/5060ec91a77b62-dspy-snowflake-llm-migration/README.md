
# DSPyでSnowflake上のLLMモデルの移行を試してみた

Snowflake×DSPyのコード

- [Zennの記事](https://zenn.dev/spectee/articles/5060ec91a77b62)で用いたコード集になります。
- DSPy3.0で書かれている為、時間が経っていると動作しない可能性があります。
- 検証に用いているデータは[こちら](https://huggingface.co/datasets/fancyzhx/amazon_polarity)から取得しています。
- 環境構築は[pixi](https://pixi.prefix.dev/latest/installation/)上で下記のコマンドを用いて行っています。

```bash
# pixiのインストール
curl -fsSL https://pixi.sh/install.sh | sh
# 作業ディレクトリへ移動し、初期の環境設定
pixi init
pixi add dspy snowflake-snowpark-python python-dotenv datasets marimo
# marimoの起動
pixi run marimo edit

```