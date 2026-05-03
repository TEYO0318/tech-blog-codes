"""Geofabrik GmbHが提供しているOSMのPBF形式のデータを、duckdbを用いてParquet形式に変換するコード。"""

# NOTE:このコードはhttps://zenn.dev/spectee/articles/4bc323b42b0192#geofabrik-gmbh(openstreetmap) で使っているコードです。

import duckdb

# ここはデータ取得時の日付に依存します
input_pbf = "japan-260312.osm.pbf"
output_file = "japan_polygons.parquet"
# duckdbと接続し、udfのような形で処理を実行
con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")
# 読み取るデータをmultipolygonsのみに指定
# INTERLEAVED_READINGにより読み取り方を上からではなく、効率的に読むように変更(そのまま読むと、Featureが多すぎて処理が落ちる為)
con.execute(f"""
    COPY (
        SELECT * FROM ST_Read(
            '{input_pbf}',
            layer='multipolygons',
            open_options=['INTERLEAVED_READING=YES']
        )
    ) TO '{output_file}' (FORMAT 'PARQUET')
""")
