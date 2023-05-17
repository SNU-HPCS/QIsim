from scipy.linalg import expm
from numpy import array, complex128, sqrt, pi, \
    absolute, exp, dot, angle, cos, sin, conj
from sfqlib.euler_angle import decompose_euler


class SfqSequence():
    """Represent a sequence in the form of a bit string,
    where 0 represents free precession for one clock period, and 1 represents
    a SFQ pulse followed by free precession for one clock period.
    """
    def __init__(self, sequence_dec, length):
        """
        :param int sequence_dec: The sequence specified as an integer.
        This will be later converted to a binary as a bit string.
        :apram int length: The length of the bit string.
        If the sequence_dec is too large to be represented by a length bits,
        it will be truncated.
        """
        self.decimal = sequence_dec
        self.length = length
        self.fidelity = 0
        self.qubit = None

    def plot_sequence(self, ax):
        for index, bit in enumerate(self.binary):
            if bit == 1:
                ax.plot([index, index], [0, 1], 'b')
            else:
                ax.plot([index, index], [0, 0], 'b')

    @property
    def binary(self):
        """Return the sequence as a bit string."""
        return list(self.decimal_to_binary(self.decimal, self.length))

    @staticmethod
    def decimal_to_binary(num, digits):
        """Convert a number from decimal to binary (in reversed order).
        e.g. 6 -> [0, 1, 1]"""
        for i in range(digits):
            yield num % 2
            num = num / 2


class SfqQubit(object):
    """Qubit controlled by SFQ pulses. This class is to be subclassed."""
    def __init__(self, d_theta=pi/200, w_clock=2*pi*5e9,
                 w_qubit=(2*pi*5.0e9, 2*pi*9.8e9), theta=pi/2):
        """
        Create a qubit controlled by SFQ pulses.
        :param float d_theta: Angle of single y-rotation.
        :param float w_clock: Clock frequency
        :param (float, float) w_qubit: (Qubit frequency,
        Leakage level frequency)
        :param float theta: Total rotation.
        """
        self.w10, self.w12 = w_qubit
        self.d_theta, self.theta = d_theta, theta
        self.d_phi = self.w10 / w_clock * 2 * pi
        self.d_phi3 = (self.w10 + self.w12) / self.w10 * self.d_phi

    def precess(self):
        """Precess the qubit for one clock period."""
        self.kets = [dot(self.ufr, ket) for ket in self.kets]

    def pulse_and_precess(self):
        """Rotate the qubit for d_theta around y-axes,
        followed by precession for one clock period."""
        self.kets = [dot(self.usfq, ket) for ket in self.kets]
        self.precess()

    def measure_fidelity(self):
        """Measure the fidelity. Implement in subclasses."""
        pass

    def __getattr__(self, attr):
        loc = [i for i, x in enumerate(self.order) if x == attr]
        return self.kets[loc[0]] if loc else None

    def resonance(self):
        """Resonance pulse sequence. The pulses are spaced by d_phi"""
        num_steps = self.theta / self.d_theta
        for step in range(int(num_steps)):
            self.pulse_and_precess()

    def pulse_pattern(self, pattern):
        """
        Evolve the qubit according to a sequence of
        0 (precession) and 1 (sfq pulse_and_precess).
        :param list[int] pattern: The pulse sequence.
        """
        while pattern:
            if pattern.pop() == 1:
                self.pulse_and_precess()
            else:
                self.precess()

    def ideal_rotation(self, ket):
        """
        Rotate the pauli states according to the ideal y-rotation.
        Implement in subclasses.
        :return: The rotated state
        """
        pass


class Sfq3LevelQubit(SfqQubit):
    """Qubit with leakage level."""
    def __init__(self, d_theta=pi/200, w_clock=2*pi*5e9,
                 w_qubit=(2*pi*5.0e9, 2*pi*9.8e9), theta=pi/2):
        super(Sfq3LevelQubit, self).__init__(d_theta, w_clock, w_qubit, theta)
        """Initialize all the kets and operators for the three level qubit."""
        self.g = array([1.0, 0.0, 0.0], dtype=complex128)
        self.e = array([0.0, 1.0, 0.0], dtype=complex128)
        self.p = 1.0/sqrt(2.0)*array([1.0, 1.0, 0.0], dtype=complex128)
        self.p_i = 1.0/sqrt(2.0)*array([1.0, 1.0j, 0.0], dtype=complex128)
        self.m = 1.0/sqrt(2.0)*array([1.0, -1.0, 0.0], dtype=complex128)
        self.m_i = 1.0/sqrt(2.0)*array([1.0, -1.0j, 0.0], dtype=complex128)
        self.order = ['g', 'e', 'm', 'm_i', 'p', 'p_i']
        self.pauli_kets = {'g': self.g, 'e': self.e, 'm': self.m,
                           'm_i': self.m_i, 'p': self.p, 'p_i': self.p_i}
        a = array([[0.0, 1.0, 0.0], [0.0, 0.0, sqrt(2.0)],
                   [0.0, 0.0, 0.0]], dtype=complex128)
        a_dag = array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                       [0.0, sqrt(2.0), 0.0]], dtype=complex128)
        self.ufr = array([[1.0, 0.0, 0.0],
                          [0.0, exp(-1.0j * self.d_phi), 0.0],
                          [0.0, 0.0, exp(-1.0j * self.d_phi3)]],
                         dtype=complex128)
        self.usfq = expm(array(self.d_theta/2.0*(a_dag-a),
                               dtype=complex128))
        self.kets = [self.pauli_kets[key] for key in self.order]
        self.r_kets = [self.ideal_rotation(self.pauli_kets[key])
                       for key in self.order]

    def measure_fidelity(self, ignore_phase=False, ignore_leakage=False):
        kets, r_kets = self.kets, self.r_kets
        if ignore_phase:
            kets = absolute(kets) * exp(1j * angle(r_kets))
        if ignore_leakage:
            kets = [[ket[0], ket[1], 0] for ket in kets]
            r_kets = [[r_ket[0], r_ket[1], 0] for r_ket in r_kets]
        fidelity = [pow(absolute(dot(conj(r_ket), ket)), 2)
                    for r_ket, ket in zip(r_kets, kets)]
        return sum(fidelity)/len(fidelity)

    def ideal_rotation(self, ket):
        ideal_gate = array([[cos(self.theta/2), -sin(self.theta/2), 0],
                            [sin(self.theta/2), cos(self.theta/2), 0],
                            [0, 0, 1]], dtype=complex128)
        return dot(ideal_gate, ket)


class Sfq2LevelQubit(SfqQubit):
    def __init__(self, d_theta=pi/200, w_clock=2*pi*5e9,
                 w_qubit=(2*pi*5.0e9, 2*pi*9.8e9), theta=pi/2):
        # The leakage frequency is specified even though
        # leakage level is not present. This is a design error.
        super(Sfq2LevelQubit, self).__init__(d_theta, w_clock, w_qubit, theta)
        """Initialize all the kets and operators for the two level qubit."""
        self.g = array([1.0, 0.0], dtype=complex128)
        self.e = array([0.0, 1.0], dtype=complex128)
        self.p = 1.0/sqrt(2.0)*array([1.0, 1.0], dtype=complex128)
        self.p_i = 1.0/sqrt(2.0)*array([1.0, 1.0j], dtype=complex128)
        self.m = 1.0/sqrt(2.0)*array([1.0, -1.0], dtype=complex128)
        self.m_i = 1.0/sqrt(2.0)*array([1.0, -1.0j], dtype=complex128)
        self.order = ['g', 'e', 'm', 'm_i', 'p', 'p_i']
        self.pauli_kets = {'g': self.g, 'e': self.e, 'm': self.m,
                           'm_i': self.m_i, 'p': self.p, 'p_i': self.p_i}
        self.ufr = array([[1.0, 0.0],
                          [0.0, exp(-1.0j * self.d_phi)]],
                         dtype=complex128)
        a = array([[0.0, 1.0], [0.0, 0.0]], dtype=complex128)
        a_dag = array([[0.0, 0.0], [1.0, 0.0]], dtype=complex128)
        self.usfq = expm(array(self.d_theta/2.0*(a_dag-a), dtype=complex128))
        self.kets = [self.pauli_kets[key] for key in self.order]
        self.r_kets = [self.ideal_rotation(self.pauli_kets[key])
                       for key in self.order]

    def measure_fidelity(self):
        kets, r_kets = self.kets, self.r_kets
        fidelity = [pow(absolute(dot(conj(r_ket), ket)), 2)
                    for r_ket, ket in zip(r_kets, kets)]
        return sum(fidelity)/len(fidelity)

    def ideal_rotation(self, ket):
        ideal_gate = array([[cos(self.theta/2), -sin(self.theta/2)],
                            [sin(self.theta/2), cos(self.theta/2)]],
                           dtype=complex128)
        return dot(ideal_gate, ket)


"""
Euler qubits tracks the euler angles of the rotation
in addition to the state kets.
They are separated from the normal qubits to improve performance
"""


class Sfq2LevelEulerQubit(Sfq2LevelQubit):
    def __init__(self, d_theta=pi/200, w_clock=2*pi*5e9,
                 w_qubit=(2*pi*5.0e9, 2*pi*9.8e9), theta=pi/2):
        super(Sfq2LevelEulerQubit, self).__init__(d_theta, w_clock,
                                                  w_qubit, theta)
        """In addition to the 6 cardinal states,
        we record the euler angles."""
        self.u = array([[1, 0], [0, 1]])
        self.alpha_list = list()
        self.beta_list = list()
        self.gamma_list = list()

    def pulse_pattern(self, pattern):
        while pattern:
            if pattern.pop() == 1:
                self.pulse_and_precess()
            else:
                self.precess()
            # Keep track of the euler angles.
            alpha, beta, gamma = decompose_euler(self.u)
            self.alpha_list.append(alpha)
            self.beta_list.append(beta)
            self.gamma_list.append(gamma)

    def precess(self):
        self.u = dot(self.ufr, self.u)
        super(Sfq2LevelEulerQubit, self).precess()

    def pulse_and_precess(self):
        self.u = dot(self.usfq, self.u)
        super(Sfq2LevelEulerQubit, self).pulse_and_precess()


class Sfq3LevelEulerQubit(Sfq3LevelQubit):
    def __init__(self, d_theta=pi/200, w_clock=2*pi*5e9,
                 w_qubit=(2*pi*5.0e9, 2*pi*9.8e9), theta=pi/2):
        super(Sfq3LevelEulerQubit, self).__init__(d_theta, w_clock,
                                                  w_qubit, theta)
        self.u = array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.alpha_list = list()
        self.beta_list = list()
        self.gamma_list = list()

    def pulse_pattern(self, pattern):
        while pattern:
            if pattern.pop() == 1:
                self.pulse_and_precess()
            else:
                self.precess()
            alpha, beta, gamma = decompose_euler(self.u,
                                                 unimodular_check=False)
            self.alpha_list.append(alpha)
            self.beta_list.append(beta)
            self.gamma_list.append(gamma)

    def precess(self):
        self.u = dot(self.ufr, self.u)
        super(Sfq3LevelEulerQubit, self).precess()

    def pulse_and_precess(self):
        self.u = dot(self.usfq, self.u)
        super(Sfq3LevelEulerQubit, self).pulse_and_precess()
