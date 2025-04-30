with source as (
  select * from {{ source('raw', 'raw_articles') }}
)

select
  id,
  keyword,
  source_name,
  title,
  published_at::timestamp as published_at,
  content,
  fetched_at
from source
where content is not null
