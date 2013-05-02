# GridIron

GridIron is a selection of demos that are meant to show the possibilities of combining [SendGrid](http://www.sendgrid.com)&apos;s email expertise with [Iron.io]&apos;s infrastructure services to create extremely powerful custom workflows with very little code.

## Examples

### Simple Sending

The simplest possible example, sending email using SendGrid&apos;s API from within an IronWorker worker. The sendGrid authentication information is read from the configuration file and the email information (subject, recipients, sender, etc.) are read from the payload.

### Push Queue Sending

IronMQ push queues can be used to send emails. With their support for multicast, they can be used as powerful brokers. In this example, our message is sent using the Simple Sending example above, but it is also sent as a text message, using Twilio.

### Github Notifications

Github offers email notifications, but offers no way to filter them. This example shows a very basic way to filter Github notifications to get only a subset of those emails, using the Github callbacks and SendGrid.

### Processor Example

Email is a ubiquitous interface; everyone has an email address. This example is a very basic email verification system that shows how to use SendGrid&apos;s webhook support and queues to create a scalable, flexible processing system that gathers input through emails.
