import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import itertools

class Cloud(object):
    def __init__(self, nlearn, neval):
        self.dim = 2
        model = np.array([1., -1.])
        self.xLearn = np.random.rand(nlearn, self.dim) * 10. - 5.
        yLearnClean = np.sign(np.dot(self.xLearn, model))
        yLearnNoise = np.random.choice(a=[-1,1], p=[.05,.95], size=nlearn)
        # np.ones_like(yLearnClean)
        self.yLearn = np.expand_dims(yLearnClean * yLearnNoise, axis=1)
        self.xEval = np.random.rand(neval, self.dim) * 10. - 5.
        yEvalClean = np.sign(np.dot(self.xEval, model))
        yEvalNoise = np.random.choice(a=[-1,1], p=[.05,.95], size=neval)
        # np.ones_like(yEvalClean)
        self.yEval = np.expand_dims(yEvalClean * yEvalNoise, axis=1)

class Svm(object):
    def __init__(self, cl):
        self.X = tf.placeholder(tf.float64, [None, cl.dim])
        self.y = tf.placeholder(tf.float64, [None, 1])
        self.w = tf.Variable(name='w', initial_value=[0, 0], dtype=tf.float64)
        yhat = tf.matmul(self.X, tf.expand_dims(self.w,1))
        ones, zeros = tf.ones_like(self.y), tf.zeros_like(self.y)
        hinge = tf.maximum(zeros, ones - self.y * yhat)
        self.rowLosses = tf.reduce_sum(hinge, axis=1)
        self.loss = tf.reduce_mean(self.rowLosses)
        sgd = tf.train.AdagradOptimizer(.5)
        self.trainop = sgd.minimize(self.loss, var_list=[self.w])

    def learn(self, sess, cl):
        sess.run(tf.global_variables_initializer())
        lossLearns, lossEvals = [], []
        for xiter in xrange(50):
            _, rowLosses, lossLearn = sess.run([self.trainop, self.rowLosses,
                                                self.loss],
                                    feed_dict = { self.X: cl.xLearn,
                                                  self.y: cl.yLearn })
            lossLearns.append(lossLearn)
            lossEval = sess.run(self.loss, feed_dict = { self.X: cl.xEval,
                                                         self.y: cl.yEval })
            lossEvals.append(lossEval)
        _w = sess.run(self.w)
        print _w
        fig, ax = plt.subplots()
        ax.plot(range(len(lossLearns)), lossLearns, 'r', label='TrainLoss')
        ax.plot(range(len(lossEvals)), lossEvals, 'b', label='TestLoss')
        legend = ax.legend(loc='upper right', shadow=True)
        plt.show()


if __name__ == '__main__':
    cl = Cloud(40, 40)
    cLearn = ["red" if cl.yLearn[i] > 0 else "blue"
              for i in range(len(cl.yLearn))]
    plt.scatter(cl.xLearn[:,0], cl.xLearn[:,1], c=cLearn, marker='o')
    cEval = ["red" if cl.yEval[i] > 0 else "blue"
             for i in range(len(cl.yEval))]
    plt.scatter(cl.xEval[:,0], cl.xEval[:,1], c=cEval, marker='x')
    plt.show()
    with tf.Session() as sess:
        svm = Svm(cl)
        svm.learn(sess, cl)
