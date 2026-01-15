# Meilisearch


## add index

```
curl \
  -X POST 'http://47.83.215.203:9001/indexes/movies/documents' \
  -H 'Content-Type: application/json' \
  --data-binary '[
    { "id": 1, "title": "Justice League", "genre": ["Action", "Adventure"] },
    { "id": 2, "title": "Wonder Woman", "genre": ["Action", "Fantasy"] },
    { "id": 3, "title": "The Avengers", "genre": ["Action", "Sci-Fi"] },
    { "id": 4, "title": "Inception", "genre": ["Action", "Sci-Fi", "Thriller"] },
    { "id": 5, "title": "The Dark Knight", "genre": ["Action", "Crime", "Drama"] }
  ]'
```
