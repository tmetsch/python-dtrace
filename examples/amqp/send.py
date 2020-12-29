#!/usr/bin/env python

"""
Use the Python DTrace consumer and push the data through AMQP as the DTrace
probes fire.

Created on Mar 31, 2012

@author: tmetsch
"""

import dtrace
import pika
import time

# pretty num D script counting syscalls...
SCRIPT = 'syscall:::entry { @num[execname] = count(); }'

# Connection to the broker
connection = pika.BlockingConnection(pika.ConnectionParameters(
                                     host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='dtrace')


def walk(iden, key, value):
    """
    Walker which sends on the data to RabbitMQ as the DTrace probes fire.
    """
    channel.basic_publish(exchange='', routing_key='dtrace',
                          body=bytes({key[0]: value}))


def run_dtrace():
    """
    Runs a DTrace script for 5 seconds...
    """
    thr = dtrace.DTraceConsumerThread(SCRIPT, walk_func=walk)
    thr.start()

    # we will stop the thread after some time...
    time.sleep(5)

    # stop and wait for join...
    thr.stop()
    thr.join()

if __name__ == '__main__':
    run_dtrace()
    connection.close()
