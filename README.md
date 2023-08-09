# hsa-hw-11-elasticsearch-with-typos

Create ES index that will serve autocomplete needs with leveraging typos and errors (max 3 typos if word length is bigger than 7).

## Usage

### Prepare index

```sh
docker-compose up -d

# install poetry
curl -sSL https://install.python-poetry.org | python3 -

# OPTIONAL – index is in repo; fill index with english words (237K)
./delete.sh && poetry run python index.py
```

### Query

This index can do autocomplete with typos, but because of the way it is implemented,
it can do autcorrection only for the last ~3 characters in query.

Also, it may possibly do autocorrection of more than 3 characters in query
due to fact that we calculate `minimum_should_match` based on query length, not result length.
So, we need to allow user to find 13-character word with 10-character query, but at the
same we may also need to find 7-character word. Maybe some kind of result postprocessing
is required here but I didn't do it in this homework.

Maybe

```sh
poetry run python query.py caterpilrin  # caterpillar with typos

INFO:root:max_typo_count=3, min_should_match_rate=73
INFO:httpx:HTTP Request: POST http://localhost:9200/words/_search "HTTP/1.1 200 OK"
INFO:root:{'took': 6, 'timed_out': False, '_shards': {'total': 1, 'successful': 1, 'skipped': 0, 'failed': 0}, 'hits': {'total': {'value': 2, 'relation': 'eq'}, 'max_score': 56.557564, 'hits': [{'_index': 'words', '_type': '_doc', '_id': '31642', '_score': 56.557564, '_source': {'word_len': 11, 'word': 'caterpillar'}}, {'_index': 'words', '_type': '_doc', '_id': '31643', '_score': 52.321903, '_source': {'word_len': 13, 'word': 'caterpillared'}}]}}
```
