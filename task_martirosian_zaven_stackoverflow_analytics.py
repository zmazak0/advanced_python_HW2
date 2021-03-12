#!/usr/bin/env python3
""" stackoverflow analytics """

import re
import sys
import json
import logging

from collections import defaultdict
from argparse import ArgumentParser

from lxml import etree


APPLICATION_NAME = "stack_overflow"
LOGGER = logging.getLogger(APPLICATION_NAME)


def setup_parser(parser):
    """ stackoverflow analytics parser"""
    parser.add_argument(
        "-q", "--questions", dest='questions',
        help='path to questions',
        required=True, nargs=1
    )
    parser.add_argument(
        "-s", "--stop-words", dest='stop_words',
        help='path to stop-words',
        required=True, nargs=1
    )
    parser.add_argument(
        "-r", "--queries", dest='queries',
        help='path to queries',
        required=True, nargs=1
    )


def get_stopwords(path_to_stop_words):
    """ stackoverflow analytics stopwords """
    stopwords = []
    with open(path_to_stop_words, 'r', encoding='koi8-r') as stwordsio:
        for line in stwordsio:
            stopwords.append(line.strip())
    return stopwords


def get_top_n(path_to_questions, stopwords, start, stop, top_n):
    """ stackoverflow analytics topn """
    words = defaultdict(lambda: 0)
    LOGGER.debug(f'got query "{start},{stop},{top_n}"')
    with open(path_to_questions, 'r', encoding='utf-8', ) as fin:
        for line in fin:
            cnake = etree.fromstring(line)
            if ((cnake.attrib['PostTypeId'] == "1") &
                    (int(cnake.attrib['CreationDate'][:4]) >= int(start)) &
                    (int(cnake.attrib['CreationDate'][:4]) <= int(stop))):
                list_str = re.findall("\\w+", cnake.attrib['Title'].lower())
                list_str = set(list_str)
                list_str = list(list_str)
                for word in list_str:
                    if word not in stopwords:
                        words[word] = words[word] + int(cnake.attrib['Score'])
    json_dict = {
        "start": int(start),
        "end": int(stop),
        "top": []}
    for i in sorted(words.items(), key=lambda t: (-t[1], t[0]), reverse=False)[:int(top_n)]:
        json_dict['top'].append([i[0], i[1]])
    find = len(json_dict['top'])
    if find < int(top_n):
        LOGGER.warning(
            f'not enough data to answer, found {find} words out of {top_n} for period "{start},{stop}"'
        )
    json_object = json.dumps(json_dict)
    print(json_object, file=sys.stdout)


def get_queries(path_to_queries, stopwords, path_to_questions):
    """ stackoverflow analytics queries"""
    with open(path_to_queries, 'r', encoding='utf-8') as queries_list:
        for line in queries_list:
            information = line.strip().split(',')
            start = information[0]
            stop = information[1]
            top_n = information[2]
            get_top_n(path_to_questions=path_to_questions,
                      stopwords=stopwords, start=start, stop=stop,
                      top_n=top_n)
    LOGGER.info('finish processing queries')


def setup_logging():
    """ stackoverflow analytics logging """
    simple_formatter = logging.Formatter(
        fmt='%(levelname)s: %(message)s',
        datefmt=None
    )

    file_handler = logging.FileHandler(
        filename='stackoverflow_analytics.log',
    )
    warn_handler = logging.FileHandler(
        filename='stackoverflow_analytics.warn',
    )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(simple_formatter)

    warn_handler.setLevel(logging.WARNING)
    warn_handler.setFormatter(simple_formatter)

    LOGGER = logging.getLogger(APPLICATION_NAME)
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(warn_handler)


def main():
    """ stackoverflow analytics main """
    setup_logging()
    parser = ArgumentParser(
        description='stack overflow analytics'
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    stop_words = get_stopwords(arguments.stop_words[0])
    LOGGER.info('process XML dataset, ready to serve queries')
    get_queries(path_to_queries=arguments.queries[0],
                path_to_questions=arguments.questions[0],
                stopwords=stop_words)


if __name__ == "__main__":
    main()
