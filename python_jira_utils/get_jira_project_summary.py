import sys
import colorama
from colorama import Fore, Style
import pprint
from jira import JIRA

MAX_RESULTS = 1000

REPORT_WATCHERS = True

ADD_MISSING_WATCHERS = True

baseURL = 'https://jira.ad.personalgenome.com'
username = 'jsundaram'
password = ''
project = 'LO'
jira = None
jra = None

labops_members_email_lookup = {'jsundaram@pgdx.com' : 'jsundaram', 'mbrenner@pgdx.com' : 'mbrenner', 'panderson@pgdx.com' : 'panderson'}#, 'dswan@pgdx.com')

def report_misc():

    print(Fore.BLUE + "Project name '%s'" % jra.name)

    print(Fore.BLUE + "Project lead '%s'" % jra.lead.displayName)

    print(Style.RESET_ALL)

def report_components():
    
    components = jira.project_components(jra)

    if len(components) > 0:

        print(Fore.BLUE + "Here are the components")

        print(Style.RESET_ALL)

        for c in components:
            print(c.name)
    else:
        print(Fore.RED + "There are no components")
            
    print(Style.RESET_ALL)
            

def report_roles():

    roles = jira.project_roles(jra)

    if len(roles) > 0:

        print(Fore.BLUE + "Here are the roles")

        print(Style.RESET_ALL)

        for r in roles:
            print(r)
    else:
        print(Fore.RED + "There are no roles")
        
    print(Style.RESET_ALL)


def report_versions():

    versions = jira.project_versions(jra)

    if len(versions) > 0:

        print(Fore.BLUE + "Here are the versions")

        print(Style.RESET_ALL)

        for v in reversed(versions):
            print(v.name)
    else:
        print(Fore.RED + "There are no versions")

    print(Style.RESET_ALL)


def report_watchers(issue):

    watcher = jira.watchers(issue)
    print("Issue has {} watcher(s)".format(watcher.watchCount))
    current_watchers_email  = {}
    for watcher in watcher.watchers:
        current_watchers_email[watcher.emailAddress] = True
        print("'%s' - '%s'" % (watcher, watcher.emailAddress))
        # watcher is instance of jira.resources.User:
        #print(watcher.emailAddress)

    for watcher_email in labops_members_email_lookup:
        if not watcher_email in current_watchers_email:
            print(Fore.RED + "LabOpsIT member '%s' needs to be added as a watcher to '%s'" % (watcher_email,issue.key))
            username = labops_members_email_lookup[watcher_email]
            print("Need to add username '%s'" % username)
            print(Style.RESET_ALL)
            if ADD_MISSING_WATCHERS:
                jira.add_watcher(issue, username)
                print("Exiting")
                sys.exit(0)


    print(Style.RESET_ALL)
    
def report_open_issues():

    issues = jira.search_issues('project= LO AND status !=  Done', maxResults=MAX_RESULTS)
    if len(issues) > 0:
        print(Fore.BLUE + "Found the following '%d' open issues" % len(issues))

        print(Style.RESET_ALL)

        for issue in issues:
            summary = issue.fields.summary
            id = issue.id
            key = issue.key
            print("id '%s' key '%s' summary : '%s'" % (id, key, summary))
            if REPORT_WATCHERS:
                report_watchers(issue)

    print(Style.RESET_ALL)    

#jira = JIRA(baseURL)
print("Attempting to connect to JIRA at '%s'" % baseURL)
jira = JIRA(baseURL, basic_auth=(username, password))

print("Attempting to retrieve info for project '%s'" % project)
jra = jira.project(project)

# report_misc()
# report_components()
# report_roles()
# report_versions()
report_open_issues()

# issue = jira.issue('LO-27')
# summary = issue.fields.summary
# #title = issue.fields.title
# print("summary : '%s'" % summary)
# #print("title : '%s'" % title)
# pprint.pprint(issue.fields, depth=2)


# ticket = '/rest/api/2/issue/LO-27'
# loginURL = 'https://jira.ad.personalgenome.com/rest/api2/login'

# #conn = httplib2.HTTPConnection(baseURL)
# conn = httplib2.Http(baseURL)
# print("A1")
# args=urllib.parse.urlencode({'userName':username, 'password':password})
# print("A2")
# headers={'accept':'application/json'}
# print("A3")
# conn.request("post", loginURL, args, headers)
# print("A4")
# r = conn.getresponse()
# print("A5")
# if r.status not in (200, 304):
#     raise Exception("Problems getting a token from JIRA. %s %s" % (r.status, r))
# print("A6")
# token = json.loads(r.read())["token"]
# print("A7")
# token=urllib.urlencode({'LO':token}).replace("%3A", ":")
# print("A8")
# req = conn.request("get", ticketURL % token, None, headers)
# print("A9")
# r3 = conn.getresponse()
# print("A10")
# status = r3.status
# print("A11")
# json_ob=json.loads(r3.read())
# print(json_ob)
