import configparser
import contextlib
from typing import List

import pandas as pd
from jira import JIRA
from pandas import DataFrame


class JiraFacade:
    HEADER = 'CONFIGURATION'
    ISSUE_COLS = ['id', 'key']
    FIELDS_COLS = ['aggregatetimeestimate', 'aggregatetimeoriginalestimate', 'aggregatetimespent', 'assignee',
                   'components', 'created', 'creator', 'description', 'duedate', 'environment', 'fixVersions',
                   'issuetype', 'labels', 'lastViewed', 'priority', 'project', 'reporter', 'resolution',
                   'resolutiondate', 'security', 'status', 'statuscategorychangedate', 'subtasks', 'summary',
                   'timeestimate', 'timeoriginalestimate', 'timespent', 'updated', 'versions', 'votes', 'workratio']
    COMMENT_COLS = ['author', 'body', 'created', 'id', 'jsdPublic', 'self', 'updateAuthor', 'updated']

    def __init__(self):
        config = configparser.ConfigParser()
        config.read_file(open('configuration.ini'))
        token = config[self.HEADER]['token']
        user = config[self.HEADER]['user']
        url = config[self.HEADER]['url']
        self.__jira = JIRA(url, basic_auth=(user, token))

    def get_all_issues_from_query(self, query) -> DataFrame:
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
        return self.__issues_to_df(issues, self.ISSUE_COLS, self.FIELDS_COLS)

    def comments(self, issue) -> DataFrame:
        return self.__iterable_to_df(self.__jira.comments(issue), self.COMMENT_COLS)

    def issue(self, id_, fields=None, expand=None) -> DataFrame:
        issue = self.__jira.issue(id_, fields, expand)
        return self.__issues_to_df([issue], self.ISSUE_COLS, self.FIELDS_COLS)

    def close(self):
        return self.__jira.close()

    @staticmethod
    def __obj_to_list(obj, cols) -> List:
        res = []
        for field in dir(obj):
            if not field.startswith('_'):
                if field in cols:
                    value = getattr(obj, field)
                    res.append(value)
        return res

    def __iterable_to_df(self, iterable, cols=None):
        items = []
        if cols is None and len(iterable) > 0:
            cols = [f for f in dir(iterable[0]) if not f.startswith('_')]
        for item in iterable:
            items.append(self.__obj_to_list(item, cols))
        return pd.DataFrame(items, columns=cols)

    def __issues_to_df(self, issues, issue_cols, field_cols) -> DataFrame:
        issues_df = self.__iterable_to_df(issues, issue_cols)
        fields = [issue.fields for issue in issues]
        fields_df = self.__iterable_to_df(fields, field_cols)
        return pd.concat([issues_df, fields_df], axis=1, copy=False).set_index('id')


@contextlib.contextmanager
def context_manager():
    jira_facade = JiraFacade()
    yield jira_facade
    jira_facade.close()
