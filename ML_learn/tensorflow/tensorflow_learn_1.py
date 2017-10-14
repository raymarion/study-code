import tensorflow as tf
# import numpy as np
import matplotlib.pyplot as plt


def get_start():
    # getting start of tf
    a = tf.random_normal([2, 1000])
    # a = tf.random_uniform([2, 1000])
    print a
    sess = tf.Session()
    out = sess.run(a)
    x, y = out

    print out

    plt.scatter(x, y)
    plt.show()


def basic_graph():
    # some function is renamed after 1.0.0 release:
    # http://blog.csdn.net/u010700335/article/details/70885689
    # Build our graph nodes, starting from the inputs
    a = tf.constant(5, name="input_a")
    b = tf.constant(3, name="input_b")
    c = tf.multiply(a, b, name="mul_c")
    d = tf.add(a, b, name="add_d")
    e = tf.add(c, d, name="add_e")

    # Open up a TensorFlow Session
    sess = tf.Session()

    # Execute our output node, using our Session
    out = sess.run(e)

    print out

    # Open a TensorFlow SummaryWriter to write our graph to disk
    writer = tf.summary.FileWriter('./my_graph', sess.graph)

    # Close our SummaryWriter and Session objects
    writer.close()
    sess.close()

    # To start TensorBoard after running this file, execute the following command:
    # $ tensorboard --logdir='./my_graph'


# def name_scopes():



if __name__=="__main__":
    # get_start()
    # basic_graph()
