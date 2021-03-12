from task_martirosian_zaven_stackoverflow_analytics import setup_parser, setup_logging, \
    get_queries, get_stopwords

QUERY_FILE_MINI = 'query_mini.csv'
QUESTION_FILE_MINI = 'question_mini.xml'
STOPWORDS_FILE_MINI = 'stop_mini.txt'

setup_logging()
#setup_parser()

stop = get_stopwords(STOPWORDS_FILE_MINI)
get_queries(QUERY_FILE_MINI, stop, QUESTION_FILE_MINI)
