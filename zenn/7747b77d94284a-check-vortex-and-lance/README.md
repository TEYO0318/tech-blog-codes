次世代のデータフォーマットVortexを使って地理空間データ分析をやってみた

- [Zennの記事](https://zenn.dev/teyo0318/articles/7747b77d94284a)で用いたコード集になります。
検証に用いているデータは[こちら](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt- N03-2026.html)から取得しています。
環境構築はpixi上で下記のコマンドを用いて行っています。
```bash
# pixiのインストール
curl -fsSL https://pixi.sh/install.sh | sh
pixi init
pixi add duckdb polars geopandas shapely lonboard marimo
# vortexに関してはcondaにない為、pip経由でインストールします
pixi add --pypi vortex-data
# marimoを起動
pixi run marimo edit
```
