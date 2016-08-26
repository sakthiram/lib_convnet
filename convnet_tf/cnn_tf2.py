import numpy as np
import time
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
import tensorflow as tf

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)
  
def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],strides=[1, 2, 2, 1], padding='SAME')

x = tf.placeholder(tf.float32, [None, 784])
y_ = tf.placeholder(tf.float32, [None, 10])

with tf.device('/cpu:0'):
    W_conv1 = weight_variable([5, 5, 1, 32])
    b_conv1 = bias_variable([32])
    x_image = tf.reshape(x, [-1,28,28,1])
    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)
    W_conv2 = weight_variable([5, 5, 32, 64])
    b_conv2 = bias_variable([64])
    
    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)
    
    W_fc1 = weight_variable([7 * 7 * 64, 1024])
    b_fc1 = bias_variable([1024])
    
    h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
W_fc2 = weight_variable([1024, 10])
b_fc2 = bias_variable([10])

y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)
cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y_conv), reduction_indices=[1]))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

sess = tf.Session()
sess.run(tf.initialize_all_variables())
epoch_num=0
inference_time = []
conv1_time = []
pool1_time = []
conv2_time = []
pool2_time = []
fc1_time = []
for i in range(50):
    batch = mnist.train.next_batch(64)
    if i%500 == 0:  
        train_loss = cross_entropy.eval(session=sess,feed_dict={x:batch[0], y_: batch[1], keep_prob: 1.0})
        print("step %d, training loss %g"%(i, train_loss))

        start_time = time.clock()
        _ = h_conv1.eval(session=sess,feed_dict={x:mnist.validation.images, y_: mnist.validation.labels, keep_prob: 1.0})
        end_time = time.clock()
        conv1_time.append(end_time-start_time)

        start_time = time.clock()
        _ = h_pool1.eval(session=sess,feed_dict={x:mnist.validation.images, y_: mnist.validation.labels, keep_prob: 1.0})
        end_time = time.clock()
        pool1_time.append(end_time-start_time)

        start_time = time.clock()
        _ = h_pool2.eval(session=sess,feed_dict={x:mnist.validation.images, y_: mnist.validation.labels, keep_prob: 1.0})
        end_time = time.clock()
        conv2_time.append(end_time-start_time)

        start_time = time.clock()
        _ = h_pool2.eval(session=sess,feed_dict={x:mnist.validation.images, y_: mnist.validation.labels, keep_prob: 1.0})
        end_time = time.clock()
        pool2_time.append(end_time-start_time)

        start_time = time.clock()
        _ = h_fc1.eval(session=sess,feed_dict={x:mnist.validation.images, y_: mnist.validation.labels, keep_prob: 1.0})
        end_time = time.clock()
        fc1_time.append(end_time-start_time)

        test_loss = cross_entropy.eval(session=sess,feed_dict={x:mnist.validation.images, y_: mnist.validation.labels, keep_prob: 1.0})
        print("Epoch %d, testing loss %g"%(epoch_num, test_loss))
        epoch_num+=1 
    train_step.run(session=sess,feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})
print("test accuracy %g"%accuracy.eval(session=sess,feed_dict={x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0}))
#print "Average Inference Time: ", np.mean(inference_time)        
print "Average conv1 execution time: ", np.mean(conv1_time)
print "Average pool1 execution time: ", np.mean(pool1_time)
print "Average conv2 execution time: ", np.mean(conv2_time)
print "Average pool2 execution time: ", np.mean(pool2_time)
print "Average fc1 execution time: ", np.mean(fc1_time)
