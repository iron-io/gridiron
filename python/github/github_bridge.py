from iron_helper import WorkerArgs
from github import Github
import sendgrid

args = WorkerArgs(webhook=True)
username = args.config["sendgrid_username"]
password = args.config["sendgrid_password"]
gh_un = args.config["github_username"]
gh_pw = args.config["github_password"]

gh = Github(gh_un, gh_pw)
repo = gh.get_repo("%s/%s" % (args.payload["repository"]["owner"]["name"], args.payload["repository"]["name"]))

branch = args.payload["ref"].split("/")[-1]
from_param = (args.config["from"]["address"], args.config["from"]["name"])

s = sendgrid.Sendgrid(username, password, secure=True)

def verifyCommit(commit_id):
    return repo.get_commit(commit_id)

def notifyOfCommit(commit_msg, commit_url, repo_name, repo_url, owner_name, owner_email, committer):
    subject = "New commit on %s" % (repo_name, )
    text_body = "There has been a new commit on the %s branch of %s by %s. The message was %s." % (branch, repo_name, committer, commit_msg)
    html_body = "There has been a new commit on the %s branch of <a href=\"%s\" title=\"View on Github\">%s</a> by %s. The message was <a href=\"%s\" title=\"View commit on Github\">%s</a>" % (branch, repo_url, repo_name, committer, commit_url, commit_msg)

    message = sendgrid.Message(from_param, subject, text_body, html_body)
    message.add_to(owner_email, owner_name)

    s.web.send(message)

if repo.full_name not in args.config["branches"]:
    print "Not watching any branches for this repo."
elif branch not in args.config["branches"][repo.full_name]:
    print "Not watching branch %s" % (branch,)
else:
    for commit in args.payload["commits"]:
        c = verifyCommit(commit["id"])
        message = c.commit.message
        url = c.url
        repository_name = repo.full_name
        repository_url = repo.html_url
        repository_owner_name = repo.owner.name
        repository_owner_email = repo.owner.email
        committer_email = c.commit.committer.email
        notifyOfCommit(message, url, repository_name, repository_url, repository_owner_name, repository_owner_email, committer_email)
