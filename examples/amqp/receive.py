#!/usr/bin/env python

'''
Receives up to date data from the DTrace consumer.

Created on Mar 31, 2012

@author: tmetsch
'''
import ast
import pika

# Connection to the broker.
connection = pika.BlockingConnection(pika.ConnectionParameters(
                                          host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='dtrace')

# The aggregated data :-)
data = {}


def callback(ch, method, properties, body):
    '''
    Callback which picks up the DTrace messages.
    '''
    tmp = ast.literal_eval(body)
    key = tmp.keys()[0]
    val = tmp.values()[0]
    if key in data:
        data[key] += val
    else:
        data[key] = val
    # Print instead of doing print you could life update a chart...msg will
    # come as DTrace fires them
    print 'Received: ', key, val

if __name__ == '__main__':
    channel.basic_consume(callback,
                          queue='dtrace',
                          no_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        connection.close()
        # You could use Google chart to create a plot aferwards...
        # from GChartWrapper import Pie
        # G = Pie(data.values())
        # G.label(*data.keys()).size(400,300).title('Syscalls counter chart')
        # G.save()
