import argparse
import json
import logging
from io import TextIOWrapper
from time import time

from joblib import Parallel, delayed
from typing import Optional, List

from Resolver import Resolver

BATCH_SIZE = 200


def run(input_file: TextIOWrapper, output_file: TextIOWrapper, jobs: int, max_articles: Optional[int]) -> None:
    log.info("Import done, now starting work")

    current_articles = []

    nb_batches = 0

    for i, line in enumerate(input_file):
        current_articles.append(line)

        if (i + 1) % BATCH_SIZE == 0:
            log.info("Starting batch %9d", nb_batches + 1)
            result = Parallel(n_jobs=jobs)(delayed(_run)(a) for a in current_articles)

            current_articles = []

            append_to(output_file, result, end="\n")
            nb_batches += 1
            log.info("%9d batches done", nb_batches)

    if len(current_articles) > 0:
        if nb_batches == 0:
            log.info("There is only one batch to process")
        result = Parallel(n_jobs=jobs)(delayed(_run)(a) for a in current_articles)

        if len(result) > 0:
            append_to(output_file, result, end="")

    input_file.close()
    output_file.close()


def append_to(output_file: TextIOWrapper, outlist: List[str], end: str = "") -> None:
    output_file.write("\n".join(outlist) + end)
    log.debug("%10d articles written", len(outlist))


def _run(article: str) -> str:
    json_article = json.loads(article)

    passages = []

    try:
        substitutions = Resolver.resolve(json_article['text'], json_article['id'])
        substituted_text, resolved_sentences = Resolver.substituteInText(json_article['text'], substitutions)

        entity_links = Resolver.getEntityLinks(json_article['id'], json_article['links'])

        passages_and_linked_entities = Resolver.getPassagesAndLinkedEntities(substitutions,
                                                                             resolved_sentences,
                                                                             entity_links)

        for p in passages_and_linked_entities:

            for linked_entity_term, linked_entity_id in p.linkedEntities.items():
                passages.append(
                    {
                        'passage': resolved_sentences[p.resolvedPassage].strip(),
                        'id': linked_entity_id,
                        'term': linked_entity_term.strip(),
                        'type': ''  # making importer happy
                    }
                )

    except Exception as e:
        log.error("Article #'%s'# gave the error: %s", json_article['id'], str(e))

    return json.dumps(passages)


def positive_integer(string: str) -> int:
    try:
        value = int(string)
    except TypeError:
        raise argparse.ArgumentTypeError("The number of jobs must be an integer.")

    if value < 1:
        raise argparse.ArgumentTypeError("The number of jobs must be greater than 0.")

    return value


if __name__ == '__main__':
    cli = argparse.ArgumentParser()

    cli.add_argument(
        "-f", "--input",
        help="Input JSON file with one json per line",
        required=True,
        type=argparse.FileType('r')
    )

    cli.add_argument(
        "-o", "--output",
        help="Output JSON file with one json per line",
        required=True,
        type=argparse.FileType('w')
    )

    cli.add_argument(
        "-j", "--jobs",
        help="Number of parallel jobs, default: 1",
        default=1,
        type=positive_integer
    )

    cli.add_argument(
        "-n", "--maxArticles",
        help="Number of Articles to work on, default is all",
        type=positive_integer
    )

    cli.add_argument(
        "-ll", "--loglevel",
        help="Log level",
        choices=['debug', 'info', 'warning', 'error'],
        default='info'
    )

    cli.add_argument(
        "-lo", "--logfile",
        help="Log file, if empty, no file is written",
        type=str
    )

    args = cli.parse_args()

    log_conf = dict(
        level=getattr(logging, args.loglevel.upper(), None),
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    )

    if args.logfile:
        logging.basicConfig(filename=args.logfile, filemode='w', **log_conf)
        console = logging.StreamHandler()
        console.setLevel(log_conf['level'])
        console.setFormatter(logging.Formatter(log_conf['format']))
        logging.getLogger(__name__).addHandler(console)
    else:
        logging.basicConfig(**log_conf)

    log = logging.getLogger(__name__)

    log.info(
        "Starting coreference resolution on file '{}' with {} parallel jobs (on {} articles). "
        "output will be written to '{}'".format(
            args.input.name,
            args.jobs,
            'all' if args.maxArticles is None else args.maxArticles,
            args.output.name))

    started = time()

    run(input_file=args.input, output_file=args.output, jobs=args.jobs, max_articles=args.maxArticles)

    log.info("All done after {:.2f} minutes".format((time() - started) / 60))
