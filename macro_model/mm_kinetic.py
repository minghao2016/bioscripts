import numpy as np


class Kinetic:
    """
    kinetic Q-matrix based model
    """
    def __init__(self, states):
        """
        :param states: vector of model states
        """
        self.states = states
        print("### Starting concentrations:")
        print([state.name for state in self.states])
        print([state.border for state in self.states])
        self.trmn, self.trm = self.trm_create()

    class State:
        def __init__(self, no, name, rates, border, open):
            """
            :param no: state number (0 start convention)
            :param name: state name
            :param rates: vector of transition rates to other states
            :param border: initial probability of the state
            :param open: boolean if state is open
            """
            self.no, self.name, self.rates, self.border, self.open, = no, name, rates, border, open
            print("Name: {} Rates: {} Initial: {} Open: {}".format(
                self.name, [rate.name for rate in self.rates], self.border, self.open))

        class Rate:
            def __init__(self, name, value, stimulus=False):
                """
                :param name: rate name
                :param value: rate value
                :param stimulus: stimulus if rate is time dependant
                """
                self.name, self.value, self.stimulus = name, value, stimulus
                print("Name: {} Value: {} Stimulus: {}".format(self.name, self.value, self.stimulus.__name__ if self.stimulus else "no"))

    def trm_create(self):
        """
        creates transition rate matrix (Q-matrix)
        :return: function returning time dependant transition rate matrix
        """
        trm = [[rate for rate in state.rates] for state in self.states]       # rate object matrix
        trm_r = [[rate.value for rate in row]for row in trm]                  # rate value no time matrix

        print("### Zero time transition rates (i(row) -> j(column):")
        print([state.name for state in self.states])
        print(np.array(trm_r))

        def trm_fn(t):
            trm_tn = np.array([[rate.value * rate.stimulus(t) if rate.stimulus else rate.value for rate in row]
                              for row in trm])                                # rate value with stimulus
            trm_tn[np.diag_indices_from(trm_tn)] = -1 * np.sum(trm_tn, axis=1)   # row normalization
            return trm_tn

        def trm_f(t):
            trm_t = np.array([[rate.value * rate.stimulus(t) if rate.stimulus else rate.value for rate in row]
                              for row in trm])                                # rate value with stimulus
            return trm_t

        return trm_fn, trm_f


class Stimulus:
    """
    stimulus shall be defined as static method returning time dependant function returning single scalar for
    given time, notice, that time value is passed by integrator
    """

    @staticmethod
    def square(a, b, v):
        """
        square stimulus
        :param a: step start time
        :param b: step end time
        :param v: step height (rate multiplication)
        :return: time dependant function
        """
        def square_t(t):
            if a <= t < b:
                return v
            else:
                return 0
        return square_t

    @staticmethod
    def pair_square(a, b, v):
        """
        square stimulus
        :param a: step start times
        :param b: step end times
        :param v: step height (rate multiplication)
        :return: time dependant function
        """
        def square_t(t):
            if a[0] <= t < b[0] or a[1] <= t < b[1]:
                return v
            else:
                return 0
        return square_t




