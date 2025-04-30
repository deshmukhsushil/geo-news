{{ config(materialized="table") }}

SELECT
    ra.id AS article_id,
    ra.title,
    ra.url,
    ra.published_at,
    ra.source_name,
    ra.keyword,
    sa.summary,
    sa.generated_at
FROM {{ ref('stg_raw_articles') }} ra
LEFT JOIN {{ source('raw', 'summarized_articles') }} sa
    ON ra.id = sa.raw_article_id
