# GridIron

GridIron is a selection of demos that are meant to show the possibilities of combining [SendGrid](http://www.sendgrid.com)&apos;s email expertise with [Iron.io]&apos;s infrastructure services to create extremely powerful custom workflows with very little code.

## Examples

### [Hello, SendGrid](../../tree/master/python/simple_send)

The simplest possible example, sending email using SendGrid&apos;s API from within an IronWorker worker. The sendGrid authentication information is read from the configuration file and the email information (subject, recipients, sender, etc.) are read from the payload.

### [Fanout](../../tree/master/python/push_queue)

IronMQ push queues can be used to send emails. With their support for multicast, they can be used as powerful brokers. In this example, our message is sent using the Hello, SendGrid example above, but it is also sent as a text message, using Twilio.

### [Github Notifications](../../tree/master/python/github)

Github offers email notifications, but offers no way to filter them. This example shows a very basic way to filter Github notifications to get only a subset of those emails, using the Github callbacks and SendGrid.

### [Markov Bot](../../tree/master/python/markov)

Email is a ubiquitous interface; everyone has an email address. This example is a very basic email bot that uses a Markov algorithm to guess the next word in a sentence that is emailed to it. It uses SendGrid's webhook support and IronWorker's webhook endpoints to make a bot that is around when it's being talked to, and gone when nobody talks to it.
