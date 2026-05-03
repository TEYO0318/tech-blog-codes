import gc
import os
import time
from os.path import getsize

import duckdb
import geopandas as gpd
import numpy as np
import psutil
import pyarrow as pa
import pyarrow.parquet as pq
import vortex as vx

geojson_path = "N03-20260101.geojson"


def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB


def setup_duckdb(table_source):
    con = duckdb.connect()
    con.execute("INSTALL spatial; INSTALL vortex; LOAD spatial; LOAD vortex;")
    con.register("input_data", table_source)

    # Create files for DuckDB benchmark
    con.execute(
        "COPY (SELECT * FROM input_data) TO 'duck_data.parquet' (FORMAT PARQUET);"
    )
    con.execute(
        "COPY (SELECT * FROM input_data) TO 'duck_data.vortex' (FORMAT vortex);"
    )
    return con


def benchmark_duckdb_query(con, file_path):
    start = time.time()
    # Removed ST_Transform as the source is already EPSG:6668
    query = f"""
        SELECT
            N03_001, N03_004,
            ST_Area(ST_GeomFromWKB(geometry)) AS area
        FROM "{file_path}"
        WHERE N03_002 LIKE '%日高振興局%'
    """
    con.execute(query).fetchall()
    return time.time() - start


def benchmark_iteration(table_source, duck_con):
    results = {}

    # --- Basic Write Benchmark ---
    start = time.time()
    pq.write_table(table_source, "tmp.parquet")
    results["pq_write_time"] = time.time() - start

    start = time.time()
    vtx_array = vx.array(table_source)
    vx.io.write(vtx_array, "tmp.vortex")
    results["vx_write_time"] = time.time() - start

    # --- File Sizes ---
    results["pq_size"] = getsize("tmp.parquet") / 1024 / 1024
    results["vx_size"] = getsize("tmp.vortex") / 1024 / 1024

    # --- Basic Read Benchmark ---
    gc.collect()
    base_mem_pq = get_memory_usage()
    start = time.time()
    table_pq = pq.read_table("tmp.parquet")
    results["pq_read_time"] = time.time() - start
    results["pq_mem_rss"] = get_memory_usage() - base_mem_pq
    results["pq_nbytes"] = table_pq.nbytes / 1024 / 1024
    del table_pq
    gc.collect()

    base_mem_vx = get_memory_usage()
    start = time.time()
    vtx_opened = vx.open("tmp.vortex")
    vtx_data = vtx_opened.scan().read_all()
    results["vx_read_time"] = time.time() - start
    results["vx_mem_rss"] = get_memory_usage() - base_mem_vx
    results["vx_nbytes"] = vtx_data.nbytes / 1024 / 1024
    del vtx_data
    gc.collect()

    # --- DuckDB Spatial Query Benchmark ---
    results["duck_pq_time"] = benchmark_duckdb_query(duck_con, "duck_data.parquet")
    results["duck_vx_time"] = benchmark_duckdb_query(duck_con, "duck_data.vortex")

    # Cleanup iteration files
    if os.path.exists("tmp.parquet"):
        os.remove("tmp.parquet")
    if os.path.exists("tmp.vortex"):
        os.remove("tmp.vortex")

    return results


def main():
    num_runs = 5
    print(f"--- Dataset: {geojson_path} ---")
    print(f"Loading GeoJSON (Initial setup)...")
    gdf = gpd.read_file(geojson_path)
    # Convert to WKB for spatial consistency in DuckDB
    table_source = pa.Table.from_pandas(gdf.to_wkb())
    del gdf
    gc.collect()

    print("Setting up DuckDB and preparing benchmark files...")
    duck_con = setup_duckdb(table_source)

    all_results = []
    for i in range(num_runs):
        print(f"Running iteration {i + 1}/{num_runs}...")
        res = benchmark_iteration(table_source, duck_con)
        all_results.append(res)

    # Calculate averages
    avg = {key: np.mean([r[key] for r in all_results]) for key in all_results[0].keys()}

    print(f"\n[Averaged Results over {num_runs} runs (No ST_Transform)]")
    print(f"1. Basic IO Performance:")
    print(f"   Write (Parquet): {avg['pq_write_time']:.4f}s")
    print(f"   Write (Vortex):  {avg['vx_write_time']:.4f}s")
    print(f"   Read  (Parquet): {avg['pq_read_time']:.4f}s")
    print(f"   Read  (Vortex):  {avg['vx_read_time']:.4f}s")

    print(f"\n2. DuckDB Spatial Query Performance:")
    print(f"   (Filter -> Area Calculation)")
    print(f"   DuckDB + Parquet: {avg['duck_pq_time']:.4f}s")
    print(f"   DuckDB + Vortex:  {avg['duck_vx_time']:.4f}s")
    print(f"   Speedup (Vortex): {avg['duck_pq_time'] / avg['duck_vx_time']:.2f}x")

    print(f"\n3. File Sizes:")
    print(f"   Parquet: {avg['pq_size']:.2f} MB")
    print(f"   Vortex:  {avg['vx_size']:.2f} MB")

    print(f"\n4. Memory Consumption (Basic Read):")
    print(f"   Parquet RSS Increase: {avg['pq_mem_rss']:.2f} MB")
    print(f"   Vortex RSS Increase:  {avg['vx_mem_rss']:.2f} MB")

    print(f"\n--- Final Summary (Averages) ---")
    print(
        f"Query Speed: Vortex is {avg['duck_pq_time'] / avg['duck_vx_time']:.1f}x faster in DuckDB spatial queries"
    )
    print(
        f"Read Speed:  Vortex is {avg['pq_read_time'] / avg['vx_read_time']:.1f}x faster in basic Arrow reading"
    )
    print(
        f"RSS Memory:  Vortex uses {avg['pq_mem_rss'] / avg['vx_mem_rss']:.1f}x less RSS during read"
    )

    # Cleanup DuckDB files
    if os.path.exists("duck_data.parquet"):
        os.remove("duck_data.parquet")
    if os.path.exists("duck_data.vortex"):
        os.remove("duck_data.vortex")


if __name__ == "__main__":
    main()
