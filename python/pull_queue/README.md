# GridIron

GridIron is a collection of examples that showcase the benefits of using [SendGrid](http://www.sendgrid.com) and [Iron.io](http://www.iron.io) together to deliver powerful and scalable email solutions.

## Queue-Based Emailing

In this example, we're showing how IronWorker and IronMQ can be used to send emails using SendGrid. This is the [Hello, SendGrid](../simple_send) example, except now the payload is separated from the task and placed on a message queue. The worker will pull each message off the queue, in order, and use SendGrid to send an email based on the message's body. Then it will move on to the next message, until the queue is empty or the worker times out.

The purpose of this example is to demonstrate how message queues can be used to separate _the data being processed_ from _the workers processing it_. This allows your worker to run into errors and fail without losing data, and allows you to control the rate at which data is processed (and emails sent) by simply adding or killing worker processes.

### Configuration

The Queue-Based Emailing example consists of a slight modification to the [Hello, SendGrid](../simple_send) worker that simply pulls messages off a queue and then sends them using SendGrid's web API. It has only a few dependencies:

1. The `iron_worker` [CLI](http://dev.iron.io/worker/reference/cli/) is used to deploy the worker to the IronWorker cloud. It can be installed using `gem install iron_worker_ng`
2. The [SendGrid library](http://pypi.python.org/pypi/sendgrid) for Python is used to interface with SendGrid's Web API. It can be installed using `pip install sendgrid`
3. The [IronMQ library](http://pypi.python.org/pypi/iron-mq) for Python is used to retrieve messages from the IronMQ queue. It can be installed using `pip install iron-mq`

Once the dependencies are installed, you'll need three configuration files.

#### pull_queue.worker

`pull_queue.worker` is a worker manifest file that defines your worker for the `iron_worker` CLI. You should be able to use it without any modification. For more information, check out the documentation on the [.worker file format](http://dev.iron.io/worker/reference/dotworker).

#### pull_queue_config.json

`pull_queue_config.json` is a configuration file that will be uploaded with your worker to define the parameters that every task run against your worker will use&mdash;in this case, your SendGrid credentials and the name of the IronMQ queue you want to read messages from. You can find a sample configuration file in the `pull_queue_config.json` file located in the repository.

#### iron.json

`iron.json` is a configuration file for the `iron_worker` CLI. It should contain the project ID and token you want to use as authentication credentials with Iron.io. You can download your `iron.json` file from [the HUD](https://hud.iron.io) or you can check [the documentation](http://dev.iron.io/worker/reference/configuration) for more information about the format. A minimal configuration file looks like this:

	{
	  "token": "Your private OAuth token",
	  "project_id": "Your project ID, obtained from https://hud.iron.io"
	}

### Deploying

Once your configuration files are created, deploying your worker is as simple as running `iron_worker upload pull_queue --worker-config pull_queue_config.json`. The `iron_worker` tool will read your `pull_queue.worker` file, install the necessary dependencies, and upload it to the IronWorker cloud. If you check [the HUD](https://hud.iron.io), you should see the worker `pull_queue` has been created in your project.

Now that your worker is uploaded, we want to run it every so often to check for new messages on the queue. You can do this by running `iron_worker schedule pull_queue --run-every 60`. This will set the worker to be run every 60 seconds, or every minute. You can change that number to suit your needs and preferences.

Finally, we need to put some messages on the queue that your worker can use to send emails. Edit the `pull_queue_payload.json` file to include your information&mdash;the name and email address the email should be sent from, the email address that should be set as the "Reply To" for the email, the subject of the email, the text and HTML bodies of the email, and the recipient of the email. Once your information is plugged in, just run `python pull_queue_post.py`, which will add the contents of `pull_queue_payload.json` to the message queue specified in `pull_queue_config.json` as a new message.

### How It Works

The configuration file that you included in the `--worker-config` argument when uploading your worker is available in the worker's environment, and its location is passed to the worker using the `-config` argument. The `iron_helper.py` file provides a `WorkerArgs` class that finds the configuration file and parses it, then makes it available at `WorkerArgs.config` as a dict.

When your task is executed, the file listed under the `exec` keyword in your `.worker` file is executed&mdash;in this case, `pull_queue_send.py` is executed. It immediately loads up your configuration information and parses it. Then it instantiates a client for the SendGrid web API using the `sendgrid` module and a client for the IronMQ API using the `iron-mq` module. It selects the queue you specified in your configuration file.

Next, the worker just keeps reading messages off the queue, until there are no messages left. Each message sets up some variables to configure the email that will be sent, based on the body of the message, then sends the message using SendGrid's web API. Finally, each message is deleted after the worker has successfully processed it. That's important because IronMQ uses a put-get-delete paradigm. Each message, when popped off the queue, is reserved for that client for a configurable amount of time. After that time expires, if the client hasn't deleted the message yet, the message returns to the queue for another client to process. This means that a worker that fails halfway through processing a message won't lead to the message being lost; it will simply be retried by another worker.

When the queue runs out of messages to be processed, it shuts itself down gracefully. If we wanted to increase the rate at which we were sending emails, we could just queue up another worker to process the queue. If we wanted to slow down the rate at which we were sending emails, we could just kill a worker process. The workers don't need to know anything about each other, and each message will only be sent once. This gives you full control over the rate at which your data is processed, without each processor needing to know anything about the rate.

That's it! That's all it takes to get a robust, scalable email sending system using SendGrid and Iron.io.
