"""
Single Flux Quantum applied to Qubits.
The class SfqQubit, Sfq3LevelQubit, Sfq2LevelQubit are optimized for performance.
Do not change those three classes. Instead, subclass them to implement more features.
"""

from scipy.linalg import expm
from numpy import (array, sqrt, pi, absolute, exp, dot, cos, sin,
                   conj, complex128, transpose, trace)
from sfqlib.euler_angle import decompose_euler
from sfqlib.bloch import Bloch
import matplotlib.pyplot as plt
index_to_states = {0: '$G$', 1: '$E$', 2: '$P$', 3: '$P_I$', 4: '$M$', 5: '$M_I$'}


class MissingAxesException(Exception):
    """Number of axes is not enough for visualization."""
    def __init__(self):
        super(MissingAxesException, self).__init__('Two axes are required.')


class SfqSequence():
    """This class represents a pulse sequence.
    It does decimal to binary conversion and visualization of the pulse sequence."""
    def __init__(self, sequence_dec, length):
        """
        Create a pulse sequence of *length* long using a decimal number>
        If the sequence_dec is too large to be represented by a length bits,
        it will be truncated.

        :param sequence_dec: The sequence specified as an integer.
        :param length: The length of the bit string.

        """
        self.decimal = sequence_dec
        self.length = length
        self.fidelity = 0
        self.qubit = None

    @property
    def binary(self):
        """
        Binary representation of the sequence.

        :return: the sequence as a bit string.
        """
        return list(self.decimal_to_binary(self.decimal, self.length))

    def plot_sequence(self, ax):
        """Plot the pulse sequence as a bar code.

        :param ax: The axis on which the bar code will be plotted.

        """
        for index, bit in enumerate(self.binary):
            if bit == 1:
                ax.plot([index, index], [0, 1], 'b')
            else:
                ax.plot([index, index], [0, 0], 'b')

    @staticmethod
    def decimal_to_binary(num, digits):
        """Convert a number from decimal to binary (in reversed order).
        e.g. 6 -> [0, 1, 1]

        :param num: The decimal number to be converted.
        :param digits: The number of binary digits allowed.

        :rtype: Iterator[:class:`int`]
        """
        for i in range(digits):
            yield num % 2
            num = num / 2


class SfqQubit(object):
    """Qubit controlled by SFQ pulses. *This class is to be subclassed.*"""
    g, e, p, p_i, m, m_i = None, None, None, None ,None, None
    static_kets = [g, e, m, m_i, p, p_i]
    a, a_dag = None, None
    def __init__(self, d_theta=pi/200, w_clock=2*pi*5e9,
                 w_qubit=(2*pi*5.0e9, 2*pi*9.8e9), theta=pi/2):
        """
        Create a qubit controlled by SFQ pulses.

        :param d_theta: Angle of single y-rotation.
        :param w_clock: Clock angular frequency
        :param w_qubit: (Qubit angular frequency, Leakage level angular frequency)
        :param theta: Total rotation.

        """
        self.u_sfq = None
        self.u_free = None
        self.w_10, self.w_02 = w_qubit
        self.w_clock = w_clock
        self.d_theta, self.theta = d_theta, theta
        self.d_phi = self.w_10 / self.w_clock * 2 * pi
        self.d_phi3 = (self.w_10 + self.w_02) / self.w_10 * self.d_phi
        self.resonance_times = int(round(self.w_clock / self.w_10, 0))

    @property
    def kets(self):
        """The 6 cardinal rotated states.

        :return: The 6 cardinal rotated states.
        """
        return [dot(self.u, ket) for ket in self.static_kets]

    def precess(self):
        """Precess the qubit for one clock period."""
        self.u = dot(self.u_free, self.u)

    def _pulse(self):
        """Apply a SFQ pulse to the qubit."""
        self.u = dot(self.u_sfq, self.u)

    def pulse_and_precess(self):
        """Rotate the qubit for d_theta around y-axis,
        then precess for one clock period."""
        self._pulse()
        self.precess()

    def resonance(self):
        """Apply a resonance pulse sequence to the qubit."""
        num_steps = self.theta / self.d_theta
        for step in range(int(num_steps)):
            self.pulse_and_precess()
            for i in range(self.resonance_times-1):
                self.precess()

    def pulse_pattern(self, pattern):
        """
        Evolve the qubit according to a sequence of
        0 (precession) and 1 (sfq pulse_and_precess).

        :param pattern: The pulse sequence.

        """
        while pattern:
            if pattern.pop() == 1:
                self.pulse_and_precess()
            else:
                self.precess()

    def measure_fidelity(self):
        """Measure the fidelity. Implement in subclasses."""
        pass


class Sfq3LevelQubit(SfqQubit):
    """Qubit with one leakage level."""
    g = array([1.0, 0.0, 0.0], dtype=complex128)
    e = array([0.0, 1.0, 0.0], dtype=complex128)
    p = 1.0/sqrt(2.0)*array([1.0, 1.0, 0.0], dtype=complex128)
    p_i = 1.0/sqrt(2.0)*array([1.0, 1.0j, 0.0], dtype=complex128)
    m = 1.0/sqrt(2.0)*array([1.0, -1.0, 0.0], dtype=complex128)
    m_i = 1.0/sqrt(2.0)*array([1.0, -1.0j, 0.0], dtype=complex128)
    static_kets = [g, e, m, m_i, p, p_i]
    a = array([[0.0, 1.0, 0.0], [0.0, 0.0, sqrt(2.0)],
               [0.0, 0.0, 0.0]], dtype=complex128)
    a_dag = array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                   [0.0, sqrt(2.0), 0.0]], dtype=complex128)

    def __init__(self, d_theta=pi/200, w_clock=2*pi*5e9,
                 w_qubit=(2*pi*5.0e9, 2*pi*9.8e9), theta=pi/2):
        super(Sfq3LevelQubit, self).__init__(d_theta, w_clock, w_qubit, theta)
        self.u_free = array([[1.0, 0.0, 0.0],
                             [0.0, exp(-1.0j * self.d_phi), 0.0],
                             [0.0, 0.0, exp(-1.0j * self.d_phi3)]],
                            dtype=complex128)

        self.u_sfq = expm(array(self.d_theta / 2.0 * (self.a_dag - self.a),
                                dtype=complex128))
        self.u = array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=complex128)
        self.ideal_gate = array([[cos(self.theta/2), -sin(self.theta/2), 0],
                                 [sin(self.theta/2), cos(self.theta/2), 0], [0, 0, 1]], dtype=complex128)
        #self.ideal_gate = array([[1.0, 0.0, 0.0], [0.0, exp(1.0j * pi/4), 0.0], [0,0,1]], dtype=complex128)
        self.rotated_kets = [dot(self.ideal_gate, ket) for ket in self.static_kets]

    def measure_fidelity(self, method='states', ignore_leakage=False):
        """Measure the fidelity of the rotation applied to the qubit.
        
        :param method: Either 'states' or 'gates'.
        :param ignore_leakage: Do not account for the leakage level when computing fidelity.

        :return: The fidelity.

        """
        if method == 'states':
            kets, rotated_kets = self.kets, self.rotated_kets
            if ignore_leakage:
                kets = [[ket[0], ket[1], 0] for ket in kets]
                rotated_kets = [[r_ket[0], r_ket[1], 0] for r_ket in rotated_kets]
            fidelities = [pow(absolute(dot(conj(r_ket), ket)), 2) for r_ket, ket in zip(rotated_kets, kets)]
            return sum(fidelities)/len(fidelities)
        elif method == 'gates':
            p = array([[1, 0, 0],
                       [0, 1, 0],
                       [0, 0, 0]])
            u_dag_p = dot(transpose(conj(self.u)), p)
            u_p = dot(self.u, p)
            term_i = trace(dot(u_dag_p, u_p))
            term_ii = pow(abs(trace(dot(dot(p, self.ideal_gate), self.u))), 2)
            return (term_i + term_ii) / 6
        else:
            raise Exception('No such method '+method)

    def get_unitary (self):
        return self.u


class Sfq2LevelQubit(SfqQubit):
    """Ideal two level qubit."""
    g = array([1.0, 0.0], dtype=complex128)
    e = array([0.0, 1.0], dtype=complex128)
    p = 1.0/sqrt(2.0)*array([1.0, 1.0], dtype=complex128)
    p_i = 1.0/sqrt(2.0)*array([1.0, 1.0j], dtype=complex128)
    m = 1.0/sqrt(2.0)*array([1.0, -1.0], dtype=complex128)
    m_i = 1.0/sqrt(2.0)*array([1.0, -1.0j], dtype=complex128)
    static_kets = [g, e, m, m_i, p, p_i]
    a = array([[0.0, 1.0], [0.0, 0.0]], dtype=complex128)
    a_dag = array([[0.0, 0.0], [1.0, 0.0]], dtype=complex128)

    def __init__(self, d_theta=pi/200, w_clock=2*pi*5e9,
                 w_qubit=(2*pi*5.0e9, 2*pi*9.8e9), theta=pi/2):
        """
        The leakage frequency is specified even though 
        leakage level is not present. This is a design error.
        """
        super(Sfq2LevelQubit, self).__init__(d_theta, w_clock, w_qubit, theta)
        self.u_free = array([[1.0, 0.0], [0.0, exp(-1.0j * self.d_phi)]], dtype=complex128)
        self.u_sfq = expm(array(self.d_theta / 2.0 * (self.a_dag - self.a), dtype=complex128))
        self.u = array([[1, 0], [0, 1]], dtype=complex128)
        self.ideal_gate = array([[cos(self.theta/2), -sin(self.theta/2)],
                                 [sin(self.theta/2), cos(self.theta/2)]], dtype=complex128)
        self.rotated_kets = [dot(self.ideal_gate, ket) for ket in self.static_kets]

    def measure_fidelity(self, method='states'):
        """Measure the fidelity of the rotation applied to the qubit.

        :param method: Currently only `states` is implemented. TODO Implement 'gates'.

        :return: The fidelity.

        """
        kets, rotated_kets = self.kets, self.rotated_kets
        fidelity = [pow(absolute(dot(conj(r_ket), ket)), 2) for r_ket, ket in zip(rotated_kets, kets)]
        return sum(fidelity)/len(fidelity)


class SfqFancyQubit(SfqQubit):
    """Qubit enhanced with additional features, which are separated from the basic qubits to preserve their speed."""
    def __init__(self, d_theta=pi/200, w_clock=2*pi*5e9,
                 w_qubit=(2*pi*5.0e9, 2*pi*9.8e9), theta=pi/2):
        """This constructor is not intended to be used. Do not call this."""
        super(SfqFancyQubit, self).__init__(d_theta, w_clock,
                                                  w_qubit, theta)

    def _fancy_init(self, axes):
        """Initialize necessary settings for fancy features. This should be implemented in subclasses.

        :param axes: One, or a list of axes that will be used for visualization.

        """
        self.alpha_list = list()  # Doc: List of Euler angles Alpha.
        self.beta_list = list()  # Doc: List of Euler angles Alpha.
        self.gamma_list = list()  # Doc: List of Euler angles Alpha.

    def set_plot_kets(self, plot_kets=None):
        """Choose which kets to plot. Plotting too many kets may lead to performance issues.

        :param plot_kets: A list of kets to plot. The followings are supported.

        * 'G': Ground (+z)
        * 'E': Excited (-z)
        * 'P': (+x)
        * 'P_I': (+y)
        * 'M': (-x)
        * 'M_I': (-y)

        For example, to plot the ground state and the excited state, pass in ['G', 'E'].
        """
        state_to_index = {'G': 0, 'E': 1, 'P': 2, 'P_I': 3, 'M': 4, 'M_I': 5}
        if plot_kets is None:
            self.kets_to_plot_index = list(range(6))
        else:
            self.kets_to_plot_index = [state_to_index[ket.upper()] for ket in plot_kets]
        self._update_bloch_sphere()

    def precess(self):
        super(SfqFancyQubit, self).precess()
        self._set_projection_source('z-axis')
        self._update_bloch_sphere()
        self._record_euler()

    def _pulse(self):
        super(SfqFancyQubit, self)._pulse()
        self._set_projection_source('origin')
        self._update_bloch_sphere()
        self._record_euler()

    def _set_projection_source(self, source):
        pass

    def _update_bloch_sphere(self):
        pass

    def _record_euler(self):
        alpha, beta, gamma = decompose_euler(self.u, unimodular_check=False)
        self.alpha_list.append(alpha)
        self.beta_list.append(beta)
        self.gamma_list.append(gamma)


class Sfq2LevelFancyQubit(Sfq2LevelQubit, SfqFancyQubit):
    def __init__(self, axes, d_theta=pi/200, w_clock=2*pi*5e9,
                 w_qubit=(2*pi*5.0e9, 2*pi*9.8e9), theta=pi/2):
        """Call the constructor of Sfq2LevelQubit.
        Then prepare the visualization on the provided axes.

        :param axes: Axes on which visualization will be made.

         """
        super(Sfq2LevelFancyQubit, self).__init__(d_theta, w_clock, w_qubit, theta)
        self._fancy_init(axes)

    def _fancy_init(self, axes):
        super(Sfq2LevelFancyQubit, self)._fancy_init(axes)
        self.bloch = Bloch(axes=axes)
        self.bloch.axes.text(1, 0, 0, 'X', fontsize=20)
        self.bloch.axes.text(0, 1, 0, 'Y', fontsize=20)
        self.bloch.axes.text(0, 0, 1.1, r'$\left|0\right>$', fontsize=20)
        self.bloch.axes.text(0, 0, -1.1, r'$\left|1\right>$', fontsize=20)

    def _set_projection_source(self, source):
        self.bloch.set_projection_source(source)

    def _update_bloch_sphere(self):
        for index, ket in enumerate(self.kets):
            if index in self.kets_to_plot_index:
                self.bloch.shovel_ket(ket, id=index, trace=True, text=index_to_states[index])


class Sfq3LevelFancyQubit(Sfq3LevelQubit, SfqFancyQubit):
    def __init__(self, axes, d_theta=pi/200, w_clock=2*pi*5e9,
                 w_qubit=(2*pi*5.0e9, 2*pi*9.8e9), theta=pi/2):
        """Call the constructor of Sfq3LevelQubit.
        Then prepare the visualization on the provided axes.

        :param axes: Axes on which visualization will be made.

        """
        super(Sfq3LevelFancyQubit, self).__init__(d_theta, w_clock, w_qubit, theta)
        self._fancy_init(axes)

    def _fancy_init(self, axes):
        super(Sfq3LevelFancyQubit, self)._fancy_init(axes)
        if len(axes) != 2:
            raise MissingAxesException()
        self.alpha_list, self.beta_list, self.gamma_list = list(), list() ,list()

        self.bloch_01 = Bloch(axes=axes[0])
        self.bloch_01.axes.text(1, 0, 0, 'X', fontsize=10)
        self.bloch_01.axes.text(0, 1, 0, 'Y', fontsize=10)
        self.bloch_01.axes.text(0, 0, 1.1, r'$\left|0\right>$', fontsize=10)
        self.bloch_01.axes.text(0, 0, -1.1, r'$\left|1\right>$', fontsize=10)

        self.bloch_12 = Bloch(axes=axes[1])
        self.bloch_12.axes.text(1, 0, 0, 'X', fontsize=10)
        self.bloch_12.axes.text(0, 1, 0, 'Y', fontsize=10)
        self.bloch_12.axes.text(0, 0, 1.1, r'$\left|1\right>$', fontsize=10)
        self.bloch_12.axes.text(0, 0, -1.1, r'$\left|2\right>$', fontsize=10)

    def _set_projection_source(self, source):
        self.bloch_01.set_projection_source(source)
        self.bloch_12.set_projection_source(source)

    def _update_bloch_sphere(self):
        kets_01 = [[ket[0], ket[1]] for ket in self.kets]
        kets_12 = [[ket[1], ket[2]] for ket in self.kets]

        for index, ket in enumerate(kets_01):
            if index in self.kets_to_plot_index:
                self.bloch_01.shovel_ket(ket, id=index, trace=True, text=index_to_states[index])

        for index, ket in enumerate(kets_12):
            if index in self.kets_to_plot_index:
                self.bloch_12.shovel_ket(ket, id=index, trace=True, text=index_to_states[index])
