import marimo

__generated_with = "0.23.4"
app = marimo.App()


@app.cell
def _():
    return


@app.cell
def _():
    import duckdb

    con = duckdb.connect()
    con.execute("INSTALL spatial; INSTALL vortex; LOAD spatial; LOAD vortex;")

    # Vortexファイルを読み込み、4326に変換してGeoParquetとして出力
    # ※元データが6668とのことですので、表示用に4326へTransformします
    con.execute("""
        COPY (
            SELECT 
                * EXCLUDE(geometry), 
                ST_Transform(ST_GeomFromWKB(geometry), 'EPSG:6668', 'EPSG:4326') AS geometry
            FROM 'N03-20260101.vortex'
        ) TO 'N03_20260101.geoparquet' (FORMAT PARQUET);
    """)
    return


@app.cell
def _():
    import pyarrow.parquet as pq
    from lonboard import Map, PolygonLayer

    # 1. GeoParquetをArrow Tableとして読み込む
    # これにより、Lonboardが求める「GeoArrowメタデータ」が自動的に付与されます
    table = pq.read_table("N03_20260101.geoparquet")

    # 2. レイヤーの作成
    # 建物データなど量が多い場合は、等透過度などを設定すると見やすくなります
    layer = PolygonLayer(
        table,
        get_fill_color=[100, 150, 250, 200], # 青系
        get_line_color=[255, 255, 255],      # 白枠
        line_width_min_pixels=0.5
    )

    # 3. 表示
    m = Map(layers=[layer])
    m
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
