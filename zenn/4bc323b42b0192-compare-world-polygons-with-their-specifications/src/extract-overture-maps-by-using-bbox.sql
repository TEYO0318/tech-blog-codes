-- bboxコマンドにより、overtureMapsのデータを西端, 南端, 東端, 北端の順で指定して取得 https://zenn.dev/spectee/articles/4bc323b42b0192#overturemapsで利用

-- 西端, 南端, 東端, 北端に指定した値からファイルを取得し、geoparquet形式で返す(今回はアジアの東側辺りを取得)
-- $ pixi run overturemaps download --bbox=120,20,150,50 --type=division_area --output=asia.geoparquet

-- 日本のADM2だけを抽出(countryの部分を変えれば韓国等も抽出できます。)
COPY (
  SELECT * FROM 'asia.geoparquet'
  WHERE country = 'JP' AND subtype IN ('county', 'district')
) TO 'japan_adm2.geoparquet' (FORMAT 'PARQUET');