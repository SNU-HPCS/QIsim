"""Operations associated with euler angles of (spin 1/2)"""
from numpy import conj, absolute, arccos, log, pi, exp, cos, sin, array, angle


class NotUnimodularException(Exception):
    """Raised when attempt to decompose a non-unimodular 2x2 matrix"""
    def __init__(self, d, *args, **kwargs):
        print(d)
        Exception.__init__(self, *args, **kwargs)


def decompose_euler(d, unimodular_check=True):
    """Decomposition of a unimodular 2x2 matrix into euler angles.
    :param 2x2 complex array d: the rotation matrix.
    :param Bool unimodular_check: whether unimodular check should be performed.
    This should be disabled when approximating the decompositiion of a matrix
    that is not unimodular. For example, three level qubit rotation.
    :return float alpha, beta, gamma: the euler angles."""
    d = unimodularize(d)
    a, b = d[0][0], d[0][1]
    if unimodular_check:
        if round(absolute(conj(a)-d[1][1]), 4) != 0:
            raise NotUnimodularException(d, "d[0][0] != conj(d[1][1])")
        elif round(absolute(conj(b)+d[1][0]), 4) != 0:
            raise NotUnimodularException(d, "d[1][0] != conj(d[0][1])")
        elif absolute(pow(absolute(a), 2) + pow(absolute(b), 2) - 1) > 1e-4:
            raise NotUnimodularException(d, "|a|^2 + |b|^2 != 1")

    if round(absolute(a), 7) == 0:  # A pi rotation
        alpha, beta, gamma = 0, pi, -2j * log(-b)
    elif round(absolute(b), 7) == 0:  # A precession
        alpha, beta, gamma = 0, 0, 2j * log(a)
    else:  # A regular rotation
        alpha = 1j * log(-(a * b) / (absolute(a) * absolute(b)))
        beta = 2 * arccos(absolute(a))
        gamma = 1j * log(-(a / b) / (absolute(a) / absolute(b)))
    return float(abs(alpha)), float(abs(beta)), float(abs(gamma))


def compose_euler(alpha, beta, gamma):
    """Compose a unimodular 2x2 matrix from euler angles.
    This is written mostly for testing decompose euler
    :param float alpha, beta, gamma: the euler angles
    :return 2x2 complex array d: the rotation matrix.
    """
    a = exp(-1j * (alpha+gamma)/2)*cos(beta/2)
    b = -exp(-1j * (alpha-gamma)/2)*sin(beta/2)
    return array([[a, b], [-conj(b), conj(a)]])


def unimodularize(d):
    """Give d a conventional phase factor so that d[0][0] == conj(d[1][1])."""
    d00, d11 = d[0][0], d[1][1]
    phase_d00, phase_d11 = angle(d00), angle(d11)
    phase_append = -(phase_d00 + phase_d11) / 2
    d = d * exp(1j * phase_append)
    return d
