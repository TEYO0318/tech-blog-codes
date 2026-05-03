# JupyterからMarimoへ：AI特化のノートブックへの移行ガイド


- [Zennの記事](https://zenn.dev/teyo0318/articles/1570b950183dab)で用いたコード集になります。
- 動作確認用には[国土数値情報の行政区域の2026年版のデータ](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html)(CC BY4.0+出典の明記が必要)を用いています。

```bash
# pixiのインストール。インストール後は一度ターミナルを再起動しましょう。
# 詳しくは https://pixi.prefix.dev/latest/installation/
curl -fsSL https://pixi.sh/install.sh | sh
# pixi の初期の環境構築
pixi init
# 下記は任意実行
# jupyter notebookのインストール
# pixi add jupyter
# jupyter notebookの起動
# pixi run jupyter-lab
# jupyterのデータ(.ipynb)をHTML形式で保存
# pixi run jupyter nbconvert --to html your_notebook.ipynb
# .ipynbの出力結果を初期化(コードは消えない)
# pixi run jupyter nbconvert --clear-output --inplace your_notebook.ipynb

# marimoのインストール
pixi add marimo
# marimo用のノートブックにjupyterのノートブックを変換(元のノートブックは消えない)
pixi run marimo convert your_notebook.ipynb -o your_notebook.py
# marimoの立ち上げ
pixi run marimo edit
```
