# GridIron

GridIron is a collection of examples that showcase the benefits of using [SendGrid](http://www.sendgrid.com) and [Iron.io](http://www.iron.io) together to deliver powerful and scalable email solutions.

## Hello, SendGrid Example

In this example, we're showing how IronWorker can be used to send emails using SendGrid. Given a payload of data, the worker will use SendGrid to send the email dictated by the payload.

The purpose of this example is to demonstrate the simplest possible integration of SendGrid with IronWorker. It shows how to send a single email from within a worker, a pattern that is a simple building block for more complex and powerful workflows.

### Configuration

The Hello, SendGrid example consists of an extremely simple worker that exists mainly as a client of SendGrid's web API. It has only a few dependencies:

1. The `iron_worker` [CLI](http://dev.iron.io/worker/reference/cli/) is used to deploy the worker to the IronWorker cloud. It can be installed using `gem install iron_worker_ng`
2. The [SendGrid library](http://pypi.python.org/pypi/sendgrid) for Python is used to interface with SendGrid's Web API. It can be installed using `pip install sendgrid`

Once the dependencies are installed, you'll need three configuration files.

#### simple_send.worker

`simple_send.worker` is a worker manifest file that defines your worker for the `iron_worker` CLI. You should be able to use it without any modification. For more information, check out the documentation on the [.worker file format](http://dev.iron.io/worker/reference/dotworker).

#### simple_send_config.json

`simple_send_config.json` is a configuration file that will be uploaded with your worker to define the parameters that every task run against your worker will use&mdash;in this case, your SendGrid credentials. You can find a sample configuration file in the `simple_send_config.json` file located in the repository.

#### iron.json

`iron.json` is a configuration file for the `iron_worker` CLI. It should contain the project ID and token you want to use as authentication credentials with Iron.io. You can download your `iron.json` file from [the HUD](https://hud.iron.io) or you can check [the documentation](http://dev.iron.io/worker/reference/configuration) for more information about the format. A minimal configuration file looks like this:

	{
	  "token": "Your private OAuth token",
	  "project_id": "Your project ID, obtained from https://hud.iron.io"
	}

### Deploying

Once your configuration files are created, deploying your worker is as simple as running `iron_worker upload simple_send --worker-config simple_send_config.json`. The `iron_worker` tool will read your `simple_send.worker` file, install the necessary dependencies, and upload it to the IronWorker cloud. If you check [the HUD](https://hud.iron.io), you should see the worker `simple_send` has been created in your project.

To try out your worker, edit the `simple_send_payload.json` file to include your information&mdash;the name and email address the email should be sent from, the email address that should be set as the "Reply To" for the email, the subject of the email, the text and HTML bodies of the email, and the recipient of the email. Once your information is plugged in, just run `iron_worker queue simple_send --payload-file simple_send_payload.json`, which will queue up a task with the contents of the file as your payload.

### How It Works

Payloads in IronWorker are stored as files in the worker's environment, with the location of that file passed in the `-payload` parameter. The `iron_helper.py` file provides a `WorkerArgs` class that finds the payload and parses it, then makes it available at `WorkerArgs.payload` as a dict. Likewise, the configuration file that you included in the `--worker-config` argument when uploading the worker is available in the worker environment, and its location passed under the `-config` argument to your worker. `iron_helper.py`'s `WorkerArgs` class also parses this, and makes it available as a dict through `WorkerArgs.config`.

When your task is executed, the file listed under the `exec` keyword in your `.worker` file is executed&mdash;in this case, `simple_send.py` is executed. It immediately loads up your configuration and payload information and parses them. Then it instantiates a client for the SendGrid web API using the `sendgrid` module and sets up some variables to configure the email that will be sent, based on the payload.

Finally, we just send the email using SendGrid's web API. It's that simple&mdash;you just interact with the API the way you normally would. Each worker has its own, unique environment, which is destroyed as soon as your task is finished executing. There are some very basic [restrictions](http://dev.iron.io/worker/reference/environment) on your environment&mdash;things like memory usage, the amount of time your task can spend executing, etc.&mdash;but you should be able to interact with any API, database, or source of data you like.

That's it! That's all it takes to get a very simple integration using SendGrid and IronWorker.
