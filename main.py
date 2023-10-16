import jira_a_la_pandas


def main():
    with jira_a_la_pandas.context_manager() as jira_pandas:
        pass


if __name__ == '__main__':
    main()
