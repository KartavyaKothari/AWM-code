import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

class Cloud(object):
    def __init__(self, nlearn, neval):
        a, b = 1.5, -2.
        self.xLearn = np.random.uniform(-10, 10, nlearn)
        yLearnClean = a * self.xLearn + b
        self.yLearn = yLearnClean + np.random.normal(size=nlearn) * 3.
        self.xEval = np.random.uniform(-10, 10, neval)
        yEvalClean = a * self.xEval + b
        self.yEval = yEvalClean + np.random.normal(size=neval) * 3.

class Regression(object):
    def __init__(self):
        self.x = tf.placeholder(tf.float64, [None])
        self.y = tf.placeholder(tf.float64, [None])
        self.a = tf.Variable(name='a', initial_value=.5, dtype=tf.float64)
        self.b = tf.Variable(name='b', initial_value=.5, dtype=tf.float64)
        yhat = self.a * self.x + self.b
        rowLosses = tf.abs(self.y - yhat)
        self.loss = tf.reduce_mean(rowLosses)
        sgd = tf.train.AdagradOptimizer(.5)
        self.trainop = sgd.minimize(self.loss, var_list=[self.a, self.b])

    def learn(self, sess, cloud):
        sess.run(tf.global_variables_initializer())
        lossLearns, lossEvals, avec, bvec = [], [], [], []
        for xiter in xrange(100):
            _, lossLearn = sess.run([self.trainop, self.loss],
                                    feed_dict = { self.x: cloud.xLearn,
                                                  self.y: cloud.yLearn })
            lossLearns.append(lossLearn)
            lossEval, _a, _b = sess.run([self.loss, self.a, self.b],
                                        feed_dict = { self.x: cloud.xEval,
                                                      self.y: cloud.yEval })
            lossEvals.append(lossEval)
            avec.append(_a)
            bvec.append(_b)
        fig, ax = plt.subplots()
        ax.plot(range(len(lossLearns)), lossLearns, 'r', label='TrainLoss')
        ax.plot(range(len(lossEvals)), lossEvals, 'b', label='TestLoss')
        ax.legend(loc='upper right', shadow=True)
        plt.show()
        fig, ax = plt.subplots()
        ax.plot(range(len(avec)), avec, 'g', label='a')
        ax.plot(range(len(bvec)), bvec, 'y', label='b')
        ax.legend(loc='upper left', shadow=True)
        plt.show()


if __name__ == '__main__':
    cl = Cloud(80, 80)
    fig, ax = plt.subplots()
    ax.scatter(cl.xLearn, cl.yLearn, color='r', label='Train')
    ax.scatter(cl.xEval, cl.yEval, color='b', label='Test')
    ax.legend(loc='upper left', shadow=True)
    plt.show()
    with tf.Session() as sess:
        reg = Regression()
        reg.learn(sess, cl)
