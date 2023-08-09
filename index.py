import argparse
import logging
import multiprocessing.dummy
from functools import partial

import httpx
from nltk.corpus import words

logging.basicConfig(level=logging.INFO)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("words", nargs="*")
    parser.add_argument("-c", "--concurrency", type=int, default=100)
    parser.add_argument("-e", "--elastic-url", default="http://localhost:9200")
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    httpx.put(
        f"{args.elastic_url}/_ingest/pipeline/save_word_len",
        json={
            "processors": [{"script": {"source": "ctx.word_len = ctx.word.length();"}}]
        },
    )
    index_response = httpx.put(
        f"{args.elastic_url}/words",
        json={
            "mappings": {
                "properties": {
                    "word": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer",
                    }
                }
            },
            "settings": {
                "analysis": {
                    "tokenizer": {
                        "autocomplete_tokenizer": {
                            "type": "edge_ngram",
                            "min_gram": 1,
                            "max_gram": 25,
                            "token_chars": ["letter", "digit"],
                        }
                    },
                    "analyzer": {
                        "autocomplete_analyzer": {
                            "type": "custom",
                            "tokenizer": "autocomplete_tokenizer",
                        }
                    },
                },
            },
        },
    )
    logging.info(index_response.json())

    pool = multiprocessing.dummy.Pool(args.concurrency)
    indexed_words = enumerate(args.words or words.words())
    for _ in pool.imap_unordered(partial(add_word_to_index, args), indexed_words):
        pass


def add_word_to_index(args: argparse.Namespace, indexed_word: tuple[int, str]) -> None:
    i, word = indexed_word
    httpx.put(
        f"{args.elastic_url}/words/_doc/{i}",
        params={"pipeline": "save_word_len"},
        json={"word": word},
    )


if __name__ == "__main__":
    main(parse_args())
