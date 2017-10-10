import tensorflow as tf
# import numpy as np
import matplotlib.pyplot as plt

a = tf.random_normal([2, 1000])
# a = tf.random_uniform([2, 1000])
print a
sess = tf.Session()
out = sess.run(a)
x, y = out

print out

plt.scatter(x, y)
plt.show()