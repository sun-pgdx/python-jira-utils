# -*- coding: utf-8 -*-

"""Console script for python_jira_utils."""
import sys
import os
import click
import json
import logging
from pgdx.jira.util import Util


LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO

@click.command()
# @click.option('--username', required=True, help="The username to connect to JIRA")
# @click.option('--password', required=True, help="The password to connect to JIRA")
@click.option('--config_file', required=True, help="The configuration file")
@click.option('--logfile', required=False, help="The log file", default="jira_util.log")
@click.option('--project', required=False, help="The JIRA project", default="LO")
@click.option('--issue', required=False, help="Issue id or key e.g.: LO-24")
@click.option('--get_comments', required=False, help="Get comments for issue", is_flag=True, default=False)
@click.option('--check_watchers', required=False, help="Check whether watchers have been set", is_flag=True, default=False)
@click.option('--add_missing_watchers', required=False, help="Add missing watchers", is_flag=True, default=False)
@click.option('--password_file', required=False, help="The password file that contains username and password to connect to JIRA")
def main(config_file, logfile, project, issue, get_comments, check_watchers, add_missing_watchers, password_file):
    """
    Console script for python_jira_utils.
    """

    if not os.path.exists(config_file):
        raise Exception("%s does not exist" % config_file)

    if not os.path.isfile(config_file):
        raise Exception("%s is not a file" % config_file)

    with open(config_file) as json_data_file:
        config = json.load(json_data_file)


    logging.basicConfig(filename=logfile, format=LOGGING_FORMAT, level=LOG_LEVEL)


    username = None
    password = None

    if password_file is None:
        if 'password_file' in config:
            password_file = config['password_file']
            logging.info("Derived password file '%s' from configuration file" % password_file)
        else:
            raise Exception("password_file was not defined")

    with open(password_file) as pfile:
        password_config = json.load(pfile)

        if 'username' in password_config:
            username = password_config['username']
            logging.info("Derived username from the password file")
        else:
            raise Exception("username is not in password file %s" % password_file)

        if 'password' in password_config:
            password = password_config['password']
            logging.info("Derived password from the password file")
        else:
            raise Exception("password is not in password file %s" % password_file)


    util = Util(username=username, password=password, config=config)

    if project is not None:
        util.setProject(project)

    if add_missing_watchers is not None:
        util.setAddMissingWatchers(add_missing_watchers)

    if issue and get_comments:

        util.getComments(issue)

    elif check_watchers:

        util.checkWatchers()
    else:

        util.getReport()

    return 0


if __name__ == "__main__":
    # sys.exit(main())  # pragma: no cover
    main()
