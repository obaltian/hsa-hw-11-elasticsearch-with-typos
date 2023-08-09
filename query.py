import argparse
import logging
import math

import httpx

logging.basicConfig(level=logging.INFO)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("word")
    parser.add_argument("-e", "--elastic-url", default="http://localhost:9200")
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    max_typo_count = get_max_typo_count_for_word(args.word)
    min_should_match_rate = math.ceil(
        (len(args.word) - max_typo_count) / len(args.word) * 100
    )
    logging.info(f"{max_typo_count=}, {min_should_match_rate=}")

    response = httpx.post(
        f"{args.elastic_url}/words/_search",
        json={
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "word": {
                                    "query": args.word,
                                    "minimum_should_match": f"{min_should_match_rate}%",
                                }
                            }
                        }
                    ],
                    "filter": [
                        {
                            "range": {
                                "word_len": {
                                    "gte": len(args.word) - max_typo_count,
                                    "lte": len(args.word) + max_typo_count,
                                }
                            }
                        },
                    ],
                }
            }
        },
    )
    logging.info(response.json())


def get_max_typo_count_for_word(word: str) -> int:
    if len(word) >= 7:
        typo_count = 3
    elif len(word) >= 5:
        typo_count = 2
    elif len(word) >= 3:
        typo_count = 1
    else:
        typo_count = 0
    return typo_count


if __name__ == "__main__":
    main(parse_args())
