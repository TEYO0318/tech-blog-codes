import marimo

__generated_with = "0.23.4"
app = marimo.App()


@app.cell
def _():
    import geopandas as gpd

    return (gpd,)


@app.cell
def _(gpd):
    # 国土数値情報の全国の行政区域のデータ(2026)
    # https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html
    gdf = gpd.read_file("N03-20260101.shp")
    return (gdf,)


@app.cell
def _(gdf):
    gdf.head(10)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
