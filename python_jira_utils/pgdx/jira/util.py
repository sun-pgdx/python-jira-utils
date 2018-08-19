import sys
import logging
# import colorama
from colorama import Fore, Style
# import pprint
from jira import JIRA

DEFAULT_MAX_RESULTS = 1000

DEFAULT_REPORT_WATCHERS = True

DEFAULT_ADD_MISSING_WATCHERS = True

DEFAULT_BASE_URL = 'https://jira.ad.personalgenome.com'

class Util(object):
    """

    """
    def __init__(self, **kwargs):
        """

        """

        if 'config' in kwargs:
            self._config = kwargs['config']
        else:
            logging.critical("config was not defined")
            raise Exception("config was not defined")

        if 'username' in kwargs:
            self._username = kwargs['username']
        else:
            logging.critical("username was not defined")
            raise Exception("username was not defined")

        if 'password' in kwargs:
            self._password = kwargs['password']
        else:
            logging.critical("password was not defined")
            raise Exception("password was not defined")

        if 'project' in kwargs:
            self._project = kwargs['project']
        else:
            if 'project' in self._config:
                self._project = self._config['project']
                logging.info("project was set to '%s' from the configuration file" % self._project)
            else:
                self._project = DEFAULT_PROJECT
                logging.info("project was set to default '%s'" % self._project)

        if 'base_url' in kwargs:
            self._base_url = kwargs['base_url']
        else:
            if 'base_url' in self._config:
                self._base_url = self._config['base_url']
                logging.info("base_url was set to '%s' from the configuration file" % self._base_url)
            else:
                self._base_url = DEFAULT_BASE_URL
                logging.info("base_url was set to default '%s'" % self._base_url)

        if 'add_missing_watchers' in kwargs:
            self._add_missing_watchers = kwargs['add_missing_watchers']
        else:
            if 'add_missing_watchers' in self._config:
                self._add_missing_watchers = self._config['add_missing_watchers']
                logging.info("add_missing_watchers was set to '%s' from the configuration file" % self._add_missing_watchers)
            else:
                self._add_missing_watchers = DEFAULT_ADD_MISSING_WATCHERS
                logging.info("add_missing_watchers was set to default '%s'" % self._add_missing_watchers)


        self._jira = None
        self._jra = None

        self._initialize()


    def setProject(self, project):
        """

        :param project:
        :return:
        """
        self._project = project


    def setAddMissingWatchers(self, add_missing_watchers):
        """

        :param add_missing_watchers:
        :return:
        """
        self._add_missing_watchers = add_missing_watchers


    def _initialize(self):
        """

        :return:
        """
        print("Attempting to connect to JIRA at '%s'" % self._base_url)
        self._jira = JIRA(self._base_url, basic_auth=(self._username, self._password))

        print("Attempting to retrieve info for project '%s'" % self._project)
        self._jra = self._jira.project(self._project)

    def getReport(self):
        """

        :return:
        """
        self.report_misc()
        self.report_components()
        self.report_roles()
        self.report_versions()
        self.report_open_issues()

    def report_misc(self):
        """

        :return:
        """
        print(Fore.BLUE + "Project name '%s'" % self._jra.name)

        print(Fore.BLUE + "Project lead '%s'" % self._jra.lead.displayName)

        print(Style.RESET_ALL)


    def report_components(self):
        """

        :return:
        """
        components = self._jira.project_components(self._jra)

        if len(components) > 0:

            print(Fore.BLUE + "Here are the components")

            print(Style.RESET_ALL)

            for c in components:
                print(c.name)
        else:
            print(Fore.RED + "There are no components")

        print(Style.RESET_ALL)


    def report_roles(self):
        """

        :return:
        """
        roles = self._jira.project_roles(self._jra)

        if len(roles) > 0:

            print(Fore.BLUE + "Here are the roles")

            print(Style.RESET_ALL)

            for r in roles:
                print(r)
        else:
            print(Fore.RED + "There are no roles")

        print(Style.RESET_ALL)


    def report_versions(self):
        """

        :return:
        """
        versions = self._jira.project_versions(self._jra)

        if len(versions) > 0:

            print(Fore.BLUE + "Here are the versions")

            print(Style.RESET_ALL)

            for v in reversed(versions):
                print(v.name)
        else:
            print(Fore.RED + "There are no versions")

        print(Style.RESET_ALL)


    def report_watchers(self, issue):
        """

        :param issue:
        :return:
        """

        watcher = self._jira.watchers(issue)

        print("Issue '%s' has '%d' watcher(s)" % (issue.key, watcher.watchCount))

        current_watchers_email = {}

        for watcher in watcher.watchers:
            current_watchers_email[watcher.emailAddress] = True
            print("'%s' - '%s'" % (watcher, watcher.emailAddress))
            # watcher is instance of jira.resources.User:
            # print(watcher.emailAddress)

        for watcher_email in self._config['members_email_lookup']:
            if not watcher_email in current_watchers_email:
                print(Fore.RED + "member '%s' needs to be added as a watcher to '%s'" % (watcher_email, issue.key))
                username = self._config['members_email_lookup'][watcher_email]
                print("Need to add username '%s'" % username)
                print(Style.RESET_ALL)
                if self._add_missing_watchers:
                    self._jira.add_watcher(issue, username)
                    print("Exiting")
                    sys.exit(0)

        print(Style.RESET_ALL)


    def checkWatchers(self):
        """

        :return:
        """

        issues = self._jira.search_issues('project= LO AND status !=  Done', maxResults = DEFAULT_MAX_RESULTS)

        if len(issues) > 0:

            for issue in issues:
                self.report_watchers(issue)


    def report_open_issues(self):

        issues = self._jira.search_issues('project= LO AND status !=  Done', maxResults = DEFAULT_MAX_RESULTS)

        if len(issues) > 0:
            print(Fore.BLUE + "Found the following '%d' open issues" % len(issues))

            print(Style.RESET_ALL)

            for issue in issues:
                summary = issue.fields.summary
                id = issue.id
                key = issue.key
                print("id '%s' key '%s' summary : '%s'" % (id, key, summary))
                if DEFAULT_REPORT_WATCHERS:
                    self._report_watchers(issue)

        print(Style.RESET_ALL)


    def getComments(self, key):
        """

        :param key:
        :return:
        """
        logging.info("Attempting to retrieve the issue with key '%s'" % key)

        issues = self._jira.search_issues('key = ' + key)
        if len(issues) > 1:
            raise Exception("Expected only one issue for '%s' but found '%d'" % (key, len(issues)))

        if len(issues) == 1:
            # comments = issues[0].fields.comment.comments
            # comments = issues[0].raw['fields']['comment']['comments']
            comments = self._jira.comments(issues[0])

            if len(comments) > 0:
                print("Found the following '%d' comments" % len(comments))
                comment_ctr = 0
                for comment_id in comments:
                    print("-----------------------------------")
                    comment_ctr += 1
                    comment = self._jira.comment(key, comment_id)
                    author = comment.author.displayName
                    date_created = comment.created
                    body = comment.body
                    print(Fore.BLUE + "%d. author '%s' date '%s'" %(comment_ctr, author, date_created))
                    print(Style.RESET_ALL)
                    print(body)
                    # print(comment)

                    # print(comment.body)
                    # sys.exit(0)
