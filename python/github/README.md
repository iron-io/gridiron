# GridIron

GridIron is a collection of examples that showcase the benefits of using [SendGrid](http://www.sendgrid.com) and [Iron.io](http://www.iron.io) together to deliver powerful and scalable email solutions.

## Github Notifications

In this example, we're building a simple Worker that will process event callbacks from Github's [Post-Receive Hooks](https://help.github.com/articles/post-receive-hooks), filter for commits to a configurable set of branches on configurable repositories, and email a summary to the repository owner for each commit to that branch.

The purpose of this example is to demonstrate how simple IronWorker's ability to [queue tasks from a webhook](http://dev.iron.io/worker/webhooks) makes creating customized workflows from services that support webhooks.

### Configuration

The Github notification example is an extremely simple worker that exists mainly as glue between the Github API and SendGrid's web API. It has only a few dependencies:

1. The `iron_worker` [CLI](http://dev.iron.io/worker/reference/cli/) is used to deploy the worker to the IronWorker cloud. It can be installed using `gem install iron_worker_ng`
2. The [PyGithub](http://pypi.python.org/pypi/PyGithub) Python module is used to interface with Github's API. It can be installed using `pip install PyGithub`
3. The [SendGrid library](http://pypi.python.org/pypi/sendgrid) for Python is used to interface with SendGrid's Web API. It can be installed using `pip install sendgrid`

Once the dependencies are installed, you'll need three configuration files.

#### github_bridge.worker

`github_bridge.worker` is a worker manifest file that defines your worker for the `iron_worker` CLI. You should be able to use it without any modification. For more information, check out the documentation on the [.worker file format](http://dev.iron.io/worker/reference/dotworker).

#### github_config.json

`github_config.json` is a configuration file that will be uploaded with your worker to define the parameters that every task run against your worker will use&mdash;in this case, your Github credentials, your SendGrid credentials, the branches and repositories to monitor, and the email address and name the notifications should be sent from. You can find a sample configuration file in the `github_config.json` file located in the repository.

#### iron.json

`iron.json` is a configuration file for the `iron_worker` CLI. It should contain the project ID and token you want to use as authentication credentials with Iron.io. You can download your `iron.json` file from [the HUD](https://hud.iron.io) or you can check [the documentation](http://dev.iron.io/worker/reference/configuration) for more information about the format. A minimal configuration file looks like this:

	{
	  "token": "Your private OAuth token",
	  "project\_id": "Your project ID, obtained from https://hud.iron.io"
	}

### Deploying

Once your configuration files are created, deploying is as simple as running `iron_worker upload github_bridge --worker-config github_config.json`. The `iron_worker` tool will read your `github_bridge.worker` file, install the necessary dependencies, and upload it to the IronWorker cloud. If you check [the HUD](https://hud.iron.io), you should see the worker `github_bridge` has been created in your project.

To hook up a Github repository to your worker, run the command `iron_worker webhook github_bridge`. The CLI will print a URL to your terminal. Copy that URL, and use it as the webhook URL when [adding a webhook to your repository](https://help.github.com/articles/post-receive-hooks#adding-a-webhook). You're all set!

### How It Works

When you push commits to a repository that has your worker's webhook URL set up, Github will send a payload to your worker's webhook endpoint. This will queue a task for your worker, with the payload as the body of the request. Payloads in IronWorker are stored as files in the worker's environment, with the location of that file passed in the `-payload` parameter. The `iron_helper.py` file provides a `WorkerArgs` class that finds the payload and parses it (use the argument `webhook=True` when instantiating the class to parse Github webhooks), then makes it available at `WorkerArgs.payload` as a dict. Likewise, the configuration file the you included in the `--worker-config` argument when uploading the worker is available in the worker environment, and its location passed under the `-config` argument to your worker. `iron_helper.py`'s `WorkerArgs` class also parses this, and makes it available as a dict through `WorkerArgs.config`.

When your task is executed, the file listed under the `exec` keyword in your `.worker` file is executed&mdash;in this case, `github_bridge.py` is executed. It immediately loads up your configuration and payload information and parses them. Then it instantiates a client for the Github API using the PyGithub library and a client for the SendGrid Web API using the `sendgrid` module.

Once everything is instantiated, the worker checks if the data came from a repo that has branches configured in its configuration file. If not, it prints out a debug message and the worker shuts down. Otherwise, it checks if the branch is one of the branches the worker is configured to watch for. If not, it prints out a debug message and the worker shuts down.

If the data comes from a repository and branch the worker is configured to look for, it loops through each commit in the payload. For each commit, the worker fetches the commit's data from Github's API. While the information is available in the payload, it's advisable to verify (over HTTPS, if possible) the information the worker retrieved with the "source of truth"&mdash;Github's API, in this case. If there's no way to verify with the source of truth, or if the process is costly, it's still secure to trust payload data&mdash;tasks can only be created when the request includes your Iron.io credentials, so if those are known to an attacker, the system has been compromised pretty badly. However, the extra level of security you gain by verifying with a source of truth can limit the damage caused by even the most intrusive attacks, and it's a good idea to implement it when cost-effective.

Once the commit's data has been verified with the source of truth, the worker pulls information from the commit data and uses it to populate an email message. The worker then uses the commit data to get the email address and name of the owner of the repository, and sends the prepared emails to the owner. Once this has been accomplished, the worker shuts down.

That's everything that happens. It's a very simple system that runs only when you need it, turns off when it's idling, and supports extremely customizable integrations.
