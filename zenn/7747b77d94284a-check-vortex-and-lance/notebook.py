import marimo

__generated_with = "0.23.4"
app = marimo.App(width="medium")


@app.cell
def _():
    # duckdb経由での呼び出し
    import duckdb

    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute("INSTALL vortex; LOAD vortex;")

    # GeoJSONをVortex形式に変換（ジオメトリをWKTに変換）
    con.execute("""
      COPY (
        SELECT ST_AsText(geometry) as geometry_wkt, * EXCLUDE (geometry)
        FROM ST_Read('N03-20260101.geojson')
      )
      TO 'N03-20260101.vortex' (FORMAT vortex);
    """)

    # Vortexファイルを読み込み
    df = con.execute("SELECT * FROM read_vortex('N03-20260101.vortex')").df()
    df.head()
    return


@app.cell
def _():
    import geopandas as gpd
    gdf = gpd.read_file("N03-20260101.geojson")
    gdf.to_parquet("N03-20260101.geoparquet")
    return


@app.cell
def _():
    # vortex-data経由での呼び出し

    import pyarrow.parquet as pq
    import vortex as vx

    parquet = pq.read_table(
        "N03-20260101.geoparquet"
    )
    vtx = vx.array(parquet)
    return vtx, vx


@app.cell
def _(vtx, vx):
    vx.io.write(vtx, "N03-20260101.vortex")
    return


@app.cell
def _():
    from os.path import getsize

    getsize("N03-20260101.vortex") / getsize(
        "N03-20260101.geoparquet"
    )
    return


@app.cell
def _(vx):
    # https://docs.vortex.dev/api/python/io
    # scanはVortexファイルをArrayIteratorにします。
    # read_allはchunked_arrayにし、Arrowとのやり取りをできるように変換をします。
    cvtx = vx.open("N03-20260101.vortex").scan().read_all()
    return (cvtx,)


@app.cell
def _(cvtx):
    cvtx
    return


@app.cell
def _(cvtx):
    arrow_data = cvtx.to_arrow_array()

    # 中身を表示
    print(arrow_data)
    return (arrow_data,)


@app.cell
def _(arrow_data):
    import time
    import duckdb
    # DuckDBのセットアップ
    connect = duckdb.connect()
    connect.execute("INSTALL spatial; LOAD spatial;")
    # Vortex/Lance読み込み用の設定
    # ※既にParquetやVortexファイルがある前提、あるいはArrowから直接スキャン
    connect.register("df_arrow", arrow_data)

    start_time_duck = time.time()

    result_df = connect.execute("""
        SELECT 
            N03_001, 
            N03_002, 
            N03_004,
            -- WKBからジオメトリに変換して直接面積を計算
            ST_Area(ST_GeomFromWKB(geometry)) AS area
        FROM df_arrow
        WHERE N03_002 LIKE '%日高振興局%'
    """).pl()

    print(f"Vortex approach: {time.time() - start_time_duck:.4f} sec")
    print(result_df.head())
    return


@app.cell
def _(pyogrio):
    from lonboard import Map, PolygonLayer

    table = pyogrio.raw.read_arrow("output.fgb")[1] # (meta, table) のタプルが返るため[1]を指定

    # 4. Lonboard で表示
    layer = PolygonLayer(table)
    m = Map(layers=[layer])
    m
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
