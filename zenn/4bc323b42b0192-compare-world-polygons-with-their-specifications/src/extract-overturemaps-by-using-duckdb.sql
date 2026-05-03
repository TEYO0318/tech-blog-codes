
-- DuckDBを使用して、S3に公開されているOverture Mapsの行政区画データを抽出し、Parquet形式で保存するSQLスクリプト。 https://zenn.dev/spectee/articles/4bc323b42b0192#overturemapsで利用
INSTALL spatial;
INSTALL httpfs;
LOAD spatial;
LOAD httpfs;
-- S3公開バケットへのアクセス設定
SET s3_region='us-west-2';
COPY (
  SELECT -- 取得したいプロパティの設定
    id,
    division_id,
    names.primary AS name,
    subtype,
    region,
    country,
    geometry
  FROM --効率的なデータ転送の為に、hive_partitioningの利用
    read_parquet('s3://overturemaps-us-west-2/release/2026-02-18.0/theme=divisions/type=division_area/*', hive_partitioning=1)
  WHERE
    country = 'JP'                -- 日本を指定
    AND (
      subtype = 'county'          -- 市、東京23区など
      OR subtype = 'district'     -- 郡など
    )
) TO 'japan_adm2.geoparquet' (FORMAT 'PARQUET');