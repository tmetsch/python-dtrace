Python DTrace consumer and AMQP
===============================

Very simple example to show how you can use the Python DTrace consumer and AMQP.

The scenario is pretty simple - let's say you want to trace data on one machine
and display it on another. Still the data should be up to date - so basically
whenever a DTrace probe fires the data should be transmitted to the other
hosts. This can be done with AMQP.

The examples here assume you have a RabbitMQ server running and have pika
installed.

Start the **receive.py** Python script first. Than start the **send.py** Python
script. You can even start multiple **send.py** scripts on multiple hosts to get
an overall view of the system calls made by processes on all machines :-)

The **send.py** script counts system calls and will send AMQP messages as new
data arrives. You will see in the output of the **receive.py** script that data
arrives almost instantly. Now you can build life updating visualizations of the
data gathered by DTrace.
