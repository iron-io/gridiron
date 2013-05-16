# GridIron

GridIron is a collection of examples that showcase the benefits of using [SendGrid](http://www.sendgrid.com) and [Iron.io](http://www.iron.io) together to deliver powerful and scalable email solutions.

## Fanout Example

In this example, we're building a simple workflow using the multicast support in [IronMQ's Push Queues](http://dev.iron.io/mq/reference/push_queues). Given a payload of data, the push queue will start up two workers using their webhook endpoints&mdash;one will use SendGrid to email the data to the specified recipient, the other will use [Twilio](http://twilio.com) to text the specified recipient.

The purpose of this example is to demonstrate how powerful IronMQ is at creating complex workflows without writing any code at all, while keeping each part of your workflow separate from the others. Each worker knows nothing about the other, and adding a new worker (say, a worker that sends an IM to the specified user) is as simple as uploading the worker and adding another endpoint to the push queue. By keeping processing separated like this, it makes it very easy to modify entire portions of your application without affecting unrelated portions.

### Configuration

The fanout example consists of two extremely simple workers that exist mainly as clients of SendGrid's web API and Twilio's API. It has only a few dependencies:

1. The `iron_worker` [CLI](http://dev.iron.io/worker/reference/cli/) is used to deploy the worker to the IronWorker cloud. It can be installed using `gem install iron_worker_ng`
2. The [SendGrid library](http://pypi.python.org/pypi/sendgrid) for Python is used to interface with SendGrid's Web API. It can be installed using `pip install sendgrid`
3. The [Twilio library](http://pypi.python.org/pypi/twilio) for Python is used to interface with Twilio's API. It can be installed using `pip install twilio`

**Note**: You'll also need to upload the [simple_send worker](../simple_send) from the Hello, SendGrid example, as it will be responsible for sending the email through SendGrid.

Once the dependencies are installed, you'll need three configuration files.

#### twilio.worker

`twilio.worker` is a worker manifest file that defines your worker for the `iron_worker` CLI. You should be able to use it without any modification. For more information, check out the documentation on the [.worker file format](http://dev.iron.io/worker/reference/dotworker).

#### twilio_config.json

`twilio_config.json` is a configuration file that will be uploaded with your worker to define the parameters that every task run against your worker will use&mdash;in this case, your Twilio credentials. You can find a sample configuration file in the `twilio_config.json` file located in the repository.

#### iron.json

`iron.json` is a configuration file for the `iron_worker` CLI. It should contain the project ID and token you want to use as authentication credentials with Iron.io. You can download your `iron.json` file from [the HUD](https://hud.iron.io) or you can check [the documentation](http://dev.iron.io/worker/reference/configuration) for more information about the format. A minimal configuration file looks like this:

	{
	  "token": "Your private OAuth token",
	  "project_id": "Your project ID, obtained from https://hud.iron.io"
	}

### Deploying

Once your configuration files are created, deploying your Twilio worker is as simple as running `iron_worker upload twilio --worker-config twilio_config.json`. The `iron_worker` tool will read your `twilio.worker` file, install the necessary dependencies, and upload it to the IronWorker cloud. If you check [the HUD](https://hud.iron.io), you should see the worker `twilio` has been created in your project.

To set up the push queue, you need to create the queue, first. To do so, run `python push_queue_post.py`, which will post a message to a "notifier" queue in your project. When a queue that doesn't exist is pushed to, the queue is created and the message put on it. Now that you have a queue, load it up [in the HUD](https://hud.iron.io). At the bottom of the page, you'll see a "Push Information" box and a "Subscribers" box. In the "Push Information" box, select "multicast", and leave the retries and retries delay at their default, then hit "Update Queue". In the Subscribers box, use the "Worker Webhook" dropdown to select "twilio", and hit "Add". Then use the dropdown to select "simple\_send" and hit "Add". It's important to note that push queues can push to non-workers as well; just enter any HTTP endpoint in the text input, and hit add, and the push queue will send a POST request to that URL when a message is put on the queue.

Finally, to put messages on the queue, just edit the `twilio_payload.json` file to contain your information, and run `python push_queue_post.py`. The information in `twilio_payload.json` will be put on the queue.

### How It Works

When a message lands on your push queue, the push queue takes the body of the message and turns it into a POST request to your endpoints. If you set your push queue to be "unicast", a single endpoint will be selected at random. Because our queue is set to "multicast", each of our endpoints will receive a POST request containing our message data.

Because one of our endpoints is the [simple_send](../simple_send) worker, that worker will be queued up, with our message body as the payload of the worker.

Our other endpoint is the Twilio worker we just uploaded, so that worker, too, will be queued up, with our message body as the payload of the worker.

Payloads in IronWorker are stored as files in the worker's environment, with the location of that file passed in the `-payload` parameter. The `iron_helper.py` file provides a `WorkerArgs` class that finds the payload and parses it, then makes it available at `WorkerArgs.payload` as a dict. Likewise, the configuration file that you included in the `--worker-config` argument when uploading the worker is available in the worker environment, and its location passed under the `-config` argument to your worker. `iron_helper.py`'s `WorkerArgs` class also parses this, and makes it available as a dict through `WorkerArgs.config`.

When your task is executed, the file listed under the `exec` keyword in your `.worker` file is executed&mdash;in this case, `twilio_send.py` is executed. It immediately loads up your configuration and payload information and parses them. Then it instantiates a client for the Twilio API using the `twilio` module and sets up some variables to configure the text that will be sent. We use the same body that will be sent in an email using the simple\_send worker, but text messages are a lot shorter than emails. So we just split out the first 140 characters in the email, and use that as the text body.

Finally, we just send the text using Twilio's API. It's that simple&mdash;you just interact with the API the way you normally would. To add another API, it's a simple matter of just writing a worker that does what you want, uploading it, and adding it as a subscriber to the push queue. You can add mobile push notifications, IM push, Twitter posting, or any other type of notification by simply _adding the notification_. The notifications never need to know about each other, and you can add and remove them at will.
