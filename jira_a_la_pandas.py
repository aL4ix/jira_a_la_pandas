import configparser
import contextlib

from jira import JIRA


class JiraFacade:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read_file(open('jira_credentials.ini'))
        HEADER = 'CREDENTIALS'
        TOKEN = config[HEADER]['TOKEN']
        USER = config[HEADER]['USER']
        URL = config[HEADER]['URL']
        self.__jira = JIRA(URL, basic_auth=(USER, TOKEN))

    def get_all_issues_from_query(self, query):
        issues = []
        page_num = 0
        while True:
            page_size = 50
            page_of_issues = self.__jira.search_issues(query,
                                                       maxResults=page_size,
                                                       startAt=page_size * page_num)
            issues.extend(page_of_issues)
            if len(page_of_issues) != page_size:
                break
            page_num += 1
        return issues

    def comments(self, issue):
        return self.__jira.comments(issue)

    def issue(self, id, fields=None, expand=None):
        return self.__jira.issue(id, fields, expand)

    def close(self):
        return self.__jira.close()


@contextlib.contextmanager
def context_manager():
    jira_facade = JiraFacade()
    yield jira_facade
    jira_facade.close()
