import numpy as np

class Myopic(object):
    def __init__(self, _emission, _transition, _sequence, _must):
        self.emission = _emission
        self.transition = _transition
        self.sequence = _sequence
        self.a = _must
        self.M = np.shape(self.transition)[0]
        self.T = len(self.sequence)
        self.V, self.B = None, None

    def reset(self):
        self.V = np.zeros((self.T, self.M), dtype=np.float)
        self.B = - np.ones((self.T, self.M), dtype=np.int)

    def summary(self):
        print 'V=\n', self.V
        print 'B=\n', self.B
        state = np.argmax(self.V[self.T-1,:])
        for t in xrange(self.T-1,0,-1):
            print '\ty_{', t, '}=', state
            state = self.B[t, state]

    def wdotphi(self, t, pm, m):
        return self.transition[pm, m] * self.emission[m, self.sequence[t]]

    def unconstrainedInternal(self, upto):
        self.reset()
        self.V[0, 0] = 1
        for t in xrange(1, upto):
            for m in xrange(self.M):
                for pm in xrange(self.M):
                    val = self.V[t-1,pm] * self.wdotphi(t,pm,m)
                    if self.V[t,m] < val:
                        self.V[t,m] = val
                        self.B[t,m] = pm

    def unconstrained(self):
        self.unconstrainedInternal(self.T)
        print 'Unconstrained'
        self.summary()

    def visitedStates(self, t, state):
        '''Up to and including time t.'''
        vs = set()
        for tx in xrange(t,0,-1):
            vs.add(state)
            state = self.B[t, state]
        return vs

    def veryGreedy(self):
        self.unconstrainedInternal(self.T-1)
        print 'Greedy last step'
        print 'V=\n', self.V
        bestSecondLastState = np.argmax(self.V[self.T-2,:])
        print 'bestSecondLastState=',bestSecondLastState
        visitedUptoBestSecondLastState = \
                self.visitedStates(self.T-2, bestSecondLastState)
        print 'visitedUptoBestSecondLastState=', visitedUptoBestSecondLastState
        if self.a in visitedUptoBestSecondLastState:
            for m in xrange(self.M):
                self.V[self.T-1,m] = self.V[self.T-2,bestSecondLastState] * \
                                     self.wdotphi(self.T-1,
                                                  bestSecondLastState, m)
                self.B[self.T-1,m] = bestSecondLastState
        else:
            print 'force=', self.a
            for m in xrange(self.M):
                self.V[self.T-1,m] = 0
                self.B[self.T-1,m] = -1
            print 't=', self.T-1, 'a=', self.a, \
                      self.V[self.T-2,bestSecondLastState], \
                      self.transition[bestSecondLastState, self.a],\
                      self.emission[self.a, self.sequence[self.T-1]]
            self.V[self.T-1,self.a] = self.V[self.T-2,bestSecondLastState]\
                                      * self.wdotphi(self.T-1,
                                                     bestSecondLastState,
                                                     self.a)
            self.B[self.T-1,self.a] = bestSecondLastState
        self.summary()

    def slightlyGreedy(self):
        self.unconstrainedInternal(self.T-1)
        print 'Slightly greedy'
        for m in xrange(self.M):
            for pm in xrange(self.M):
                val = 0.0
                visited = self.visitedStates(self.T-2, pm)
                if self.a in visited:
                    val = self.V[self.T-2,pm] * self.wdotphi(self.T-1,pm,m)
                else:
                    if m == self.a:
                        val = self.V[self.T-2,pm] * \
                              self.wdotphi(self.T-1,pm,self.a)
                    else:
                        val = 0.0
                #print 'pt=',self.T-2,'pm=',pm,'m=',m,\
                #           'visited=',visited,'val=',val
                if self.V[self.T-1,m] < val:
                    self.V[self.T-1,m] = val
                    self.B[self.T-1,m] = pm
        self.summary()

    def objectiveForStateSequence(self, states):
        obj = self.emission[states[0], self.sequence[0]]
        for t in xrange(1,self.T):
            obj = obj * self.emission[states[t], self.sequence[t]]
            obj = obj * self.transition[states[t-1], states[t]]
        return obj

class ConstrainedOptimal(object):
    def __init__(self, _emission, _transition, _sequence, _must):
        self.emission = _emission
        self.transition = _transition
        self.sequence = _sequence
        self.a = _must
        self.M = np.shape(self.transition)[0]
        self.T = len(self.sequence)
        self.V, self.B = None, None

    def wdotphi(self, t, pm, m):
        return self.transition[pm, m] * self.emission[m, self.sequence[t]]

    def summary(self, that):
        obj = np.max(self.V[self.T-1, :])
        state = np.argmax(self.V[self.T-1,:])
        print 'RunFix y(t_hat=', that, ')=', self.a, ' obj=', obj
        print 'V=\n', self.V
        print 'B=\n', self.B
        for t in xrange(self.T-1,0,-1):
            print '\ty_{', t, '}=', state
            state = self.B[t, state]

    def runFixThat(self, that):
        '''At time step that, state must be self.a'''
        self.V = np.zeros((self.T, self.M), dtype=np.float)
        self.B = - np.ones((self.T, self.M), dtype=np.int)
        self.V[0, 0] = 1
        for t in xrange(1, self.T):
            if t == that:
                for m in xrange(self.M):
                    self.V[t,m] = 0
                    self.B[t,m] = -1
                for pm in xrange(self.M):
                    val = self.V[t-1,pm] * self.wdotphi(t,pm,self.a)
                    if self.V[t, self.a] < val:
                        self.V[t,self.a] = val
                        self.B[t,self.a] = pm
            else:
                for m in xrange(self.M):
                    for pm in xrange(self.M):
                        val = self.V[t-1,pm] * self.wdotphi(t,pm,m)
                        if self.V[t,m] < val:
                            self.V[t,m] = val
                            self.B[t,m] = pm
        return np.max(self.V[self.T-1, :])

    def runSlow(self):
        bestScore = 0.
        bestThat = -1
        for that in xrange(1,self.T):
            score = self.runFixThat(that)
            if bestScore < score:
                bestScore = score
                bestThat = that
        self.runFixThat(bestThat)
        self.summary(bestThat)

if __name__ == '__main__':
    # Example 1: Start + 2 states;
    # veryGreedy is wrong, slightlyGreedy is right.
    # emission = np.matrix('0, 0, 0, 1; .3, .5, .2, 0; 0, .4, .1, .5')
    # transition = np.matrix('0, 1, 0; 0, .5, .5; 0, .5, .5')
    # sequence = [3, 0, 1, 2]
    # magicStateSeq = [0, 1, 2, 1]
    # must = 2

    # Example 2: Start + 3 states;
    # both veryGreedy and slightlyGreedy are wrong.
    # emission = np.matrix([[0, 0, 0, 1],
    #                       [.3, 0, .4, .3],
    #                       [0, 1, 0, 0],
    #                       [.2, 0, .1, .7]], dtype=np.float)
    # transition = np.matrix([[0, 1./3, 1./3, 1./3],
    #                         [0, 1./3, 1./3, 1./3],
    #                         [0, 1./3, 1./3, 1./3],
    #                         [0, 1./3, 1./3, 1./3]],
    #                        dtype=np.float)
    # sequence = [3, 0, 1, 2]
    # magicStateSeq = [0, 3, 2, 1]
    # must = 3

    # Example 3: Start + 2 states;
    # both veryGreedy and slightlyGreedy should be wrong.
    emission = np.matrix([[0,    0,  0,  1],
                          [.3,  .3, .4,  0],
                          [ .3,   0,  .3,  .4]], dtype=np.float)
    transition = np.matrix([[0, .5, .5],
                            [0, .5, .5],
                            [0, .5, .5]], dtype=np.float)
    sequence = [3, 0, 1, 2]
    magicStateSeq = [0, 2, 1, 1]
    must = 2

    myopic = Myopic(emission, transition, sequence, must)
    myopic.unconstrained()
    myopic.veryGreedy()
    myopic.slightlyGreedy()
    print 'magic', magicStateSeq, \
        myopic.objectiveForStateSequence(magicStateSeq)
    opt = ConstrainedOptimal(emission, transition, sequence, must)
    opt.runSlow()
