
# ハサミで肉を切らないためのポリゴン選定ガイド Pixi×DuckDBによる実務で使える世界の行政区域オープンデータの徹底比較


- [Zennの記事](https://zenn.dev/spectee/articles/4bc323b42b0192)で用いたコード集になります。
- 商用利用の可否は執筆時と変わっている可能性があるので、データ取得時に確認をお願いします。

```bash
# pixiのインストール
curl -fsSL https://pixi.sh/install.sh | sh
# 作業ディレクトリへ移動し、初期の環境設定
pixi init
# libgdal-arrow-parquet(QGISでGeoParquetを読み込むパッケージ)と後述のoverturemaps処理に必要なパッケージを入れる
pixi add qgis libgdal-arrow-parquet duckdb overturemaps
# QGISの立ち上げ
pixi run qgis
```
