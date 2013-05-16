# GridIron

GridIron is a collection of examples that showcase the benefits of using [SendGrid](http://www.sendgrid.com) and [Iron.io](http://www.iron.io) together to deliver powerful and scalable email solutions.

## Markov Bot

In this example, we're building a simple worker that will construct a Markov chain based on input obtained using SendGrid's [Inbound Parse API](http://sendgrid.com/docs/API_Reference/Webhooks/parse.html). In short, this will create a bot that guesses the next word in the sentence you email to it.

The purpose of this example is to demonstrate how powerful SendGrid's ability to trigger webhooks based on inbound email is. When combined with IronWorker's ability to start up and shut down a processor using a webhook endpoint, it's really simple to build extremely complex and powerful workflows with very little code.

### Configuration

The Markov bot example is an extremely simple worker that exists mainly as glue between a simplistic Markov algorithm, SendGrid's Inbound Parse API, and SendGrid's web API. It has only a few dependencies:

1. The `iron_worker` [CLI](http://dev.iron.io/worker/reference/cli/) is used to deploy the worker to the IronWorker cloud. It can be installed using `gem install iron_worker_ng`
2. The [SendGrid library](http://pypi.python.org/pypi/sendgrid) for Python is used to interface with SendGrid's Web API. It can be installed using `pip install sendgrid`

Once the dependencies are installed, you'll need three configuration files.

#### bot.worker

`bot.worker` is a worker manifest file that defines your worker for the `iron_worker` CLI. You should be able to use it without any modification. For more information, check out the documentation on the [.worker file format](http://dev.iron.io/worker/reference/dotworker).

#### bot_config.json

`bot_config.json` is a configuration file that will be uploaded with your worker to define the parameters that every task run against your worker will use&mdash;in this case, your SendGrid credentials and the email address and name the email replies should be sent from. You can find a sample configuration file in the `bot_config.json` file located in the repository.

#### iron.json

`iron.json` is a configuration file for the `iron_worker` CLI. It should contain the project ID and token you want to use as authentication credentials with Iron.io. You can download your `iron.json` file from [the HUD](https://hud.iron.io) or you can check [the documentation](http://dev.iron.io/worker/reference/configuration) for more information about the format. A minimal configuration file looks like this:

	{
	  "token": "Your private OAuth token",
	  "project_id": "Your project ID, obtained from https://hud.iron.io"
	}

### Deploying

Once your configuration files are created, deploying is as simple as running `iron_worker upload bot --worker-config bot_config.json`. The `iron_worker` tool will read your `bot.worker` file, install the necessary dependencies, and upload it to the IronWorker cloud. If you check [the HUD](https://hud.iron.io), you should see the worker `bot` has been created in your project.

To hook up an email address to your worker (the email address people should email to contact the bot), run the command `iron_worker webhook bot`. The CLI will print a URL to your terminal. Copy that URL, and use it as the webhook URL when [adding a webhook to your SendGrid account](http://sendgrid.com/docs/API_Reference/Webhooks/parse.html#-Setup). You're all set!

### How It Works

When someone emails the email address you set up in SendGrid's Inbound Parse API settings, SendGrid will send a webhook containing the information included in that email to your worker's webhook endpoint. This will queue a task for your worker, with the payload as the body of the request. Payloads in IronWorker are stored as files in the worker's environment, with the location of that file passed in the `-payload` parameter. The `iron_helper.py` file provides a `WorkerArgs` class that finds the payload and parses it (use the argument `multipart=True` when instantiating the class to parse multipart SendGrid messages), then makes it available at `WorkerArgs.payload` as a dict. Likewise, the configuration file that you included in the `--worker-config` argument when uploading the worker is available in the worker environment, and its location passed under the `-config` argument to your worker. `iron_helper.py`'s `WorkerArgs` class also parses this, and makes it available as a dict through `WorkerArgs.config`.

When your task is executed, the file listed under the `exec` keyword in your `.worker` file is executed&mdash;in this case, `bot.py` is executed. It immediately loads up your configuration and payload information and parses them. Then it instantiates a client for the SendGrid Web API using the `sendgrid` module and sets up some variables to configure the reply that will be sent. It then prints out some debug information: the sender of the email that started the task, and the body of the email that started the task. You can view this debug information in the task's log in [the HUD](https://hud.iron.io).

Once the email is all configured, we need to predict the next word in the email chain. Rather than writing our own Markov algorithm, we found [this great algorithm](https://github.com/thomasboyt/python-markov/blob/master/examples/AChristmasMarkov/markov.py) on Github and adapted it to our needs. Markov algorithms need training data, so we used the text of "A Christmas Carol" to train our bot&mdash;you can see the source text as `markov_source.txt` in the Github repository. Once we have a source text, we need to parse it into data that the algorithm can use. To do that, we run `python markov_generator.py`, which spits out `markov_source.json`. Because `file "markov_source.json"` is included in our `bot.worker` file, when that worker is uploaded, the `markov_source.json` file is included in the worker environment and can be loaded from within your worker. If you just want to get things up and running, you can just use the pre-generated `markov_source.json` file in the Github repository.

Now that we have an algorithm in place to predict the next word, we need to feed in the sentence we want to predict. We pull the _first line_ from the email's text body&mdash;we only want the first line, because a lot of people have signatures, and we don't want those. We sanitize that a bit (remove leading and trailing whitespace), and then generate another word using our algorithm. We print out the new text as debug information for later use.

Finally, we parse the sender information from SendGrid's webhook, parse it into a name and email address, and send the email. And that's it, we've made our very own email-powered bot! It only consumes resources when you interact with it, and it can scale to handle 1 incoming email or 1 million incoming emails _without you doing anything_.
