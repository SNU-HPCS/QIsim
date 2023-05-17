# https://github.com/MostafaKhezri/JC-ladder
# To use this code, consider citing following papers
# https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.117.190503
# https://journals.aps.org/pra/abstract/10.1103/PhysRevA.94.012347

import numpy as np
from scipy.optimize import minimize
import math

"""Diagonalize the Jaynes-Cummings ladder of energies"""

def get_order(omega_r, qubit_energy_list):
    """Get the order of eigenenergies that diagonalizer produces.

    Use the bare energy of the system as reference.

    Args:
        omega_r (float): Resonator frequency
        qubit_energy_list (List[float]): Qubit energies

    Returns:
        (List[int]): Indices giving the proper order of the elements in
            qubit_energy_list.
    """
    tmax = len(qubit_energy_list)  # Maximum number of transmon levels
    order = np.zeros(tmax)

    # Bare energies of the system
    diag_bare = np.array([-i*omega_r + qubit_energy_list[i]
                          for i in range(tmax)])
    # Eigenenergies in the order produced by diagonalizer
    eigensolver_order = np.linalg.eigvalsh(np.diag(diag_bare))

    # Find where the diagonalizer puts the energies
    for i in range(tmax):
        index, = np.where(eigensolver_order==diag_bare[i])
        order[i] = index

    #Diagonalizer puts the ith energy level in order[i]th location
    return order.astype(int)

def diagonalize_RWA_strip(tot_excit, omega_r, qubit_energy_list, g_list, order):
    """Diagonalize a single RWA strip

    Args:
        tot_excit (int): Total number of excitations in the strip
        omega_r (float): resonator frequency
        qubit_energy_list (List[float]): list of qubit energies.
        g_list (List[float]): list of qubit to resonator couplings. g_list[i] is
            qubit nearest neighbor between i+1 and i.
        order (List[int]): the order that the eigenstates should be sorted
    """
    # Maximum number of transmon levels, which also sets the size of the RWA
    # strip
    tmax = len(qubit_energy_list)
    # Diagonal elements of the RWA strip Hamiltonian
    diagonal_elements = np.array([(tot_excit-i)*omega_r + qubit_energy_list[i]
                                  for i in range(tmax)])
    # Off-diagonal elements of the RWA strip Hamiltonian
    offdiagonal_elements = np.array(
            [g_list[i]*math.sqrt((tot_excit-i)*(tot_excit-i>0))
             for i in range(tmax-1)])
    # Construct the total Hamiltonian of the RWA strip
    strip_H = (np.diag(diagonal_elements) + np.diag(offdiagonal_elements, 1) +
               np.diag(offdiagonal_elements, -1))
    # Get eigensystem
    eigenvalues, eigenvectors = np.linalg.eigh(strip_H)
    # Sort eigenvalues according to the order
    eigenvalues = np.array([eigenvalues[i] for i in order])
    # Sort eigenstates according to the order
    eigenvectors = np.array([eigenvectors[:,i] for i in order])

    # eigenvalues[q] corresponds to eigenenergy of the RWA strip with resonator
    # state 'tot_excit-q' and qubit state 'q'
    return [eigenvalues, eigenvectors]

def diagonalize_ladder(nmax, omega_r, qubit_energy_list, g_list):
    """Diagonalize the JC ladder.

    Args:
        nmax (int): maximum number of photons in the resonator
        omega_r (float): resonator frequency.
        qubit_energy_list (List[float]): list of qubit energies
        g_list (List[float]): qubit charge matrix elements (qubit nearest
            neighbor couplings)
    """
    # Maximum number of transmon levels
    tmax = len(qubit_energy_list)
    # The order that should be used to sort the eigenenergies
    order = get_order(omega_r, qubit_energy_list)
    eigen_energies = np.zeros((nmax, tmax))
    eigen_vectors = np.zeros((nmax, tmax, tmax))
    # Get the egeinenergies of the whole ladder
    for i in range(nmax):
        eigen_energies[i], eigen_vectors[i] = diagonalize_RWA_strip(
                i, omega_r, qubit_energy_list, g_list, order)
    #First index of eigen_energies signifies the total excitation number of the
    # RWA strip and NOT the resonator state The conversion is: eigenenergy of
    # the system with resonator state 'n' and qubit state
    # 'q' <--> eigen_energies[n+q, q]
    return eigen_energies, eigen_vectors

def get_fan_diagram(eigen_energies, omega_r):
    """Produce the 'fan diagram' of the JC ladder

    Args:
        eigen_energies (List[float]): eigenenergies produced by the
            diagonalize_ladder(params)
        omega_r (float): resonator frequency
    """
    # Maximum number of photons, maximum number of transmon levels
    nmax, tmax = len(eigen_energies), len(eigen_energies[0])
    fan = [np.array([eigen_energies[n,q] - n*omega_r
           for n in range(0, nmax)])
           for q in range(tmax)]

    #fan[q][n] is the 'q'th level fan diagram energy at 'n' photons
    return fan

def get_qubit_transitions(eigen_energies):
    """Produce the qubit transition frequencies in the JC ladder

    Args:
        eigen_energies (List[float]): eigenenergies produced by the
            diagonalize_ladder(params)
    """

    # Maximum number of photons, maximum number of transmon levels
    nmax, tmax = len(eigen_energies), len(eigen_energies[0])
    transitions = [np.array([eigen_energies[n+q+1,q+1] - eigen_energies[n+q,q]
                   for n in range(0, nmax-q-1)])
                   for q in range(tmax-1)]

    # transitions[q][n] is the qubit transition frequency between qubit levels
    # 'q+1' and 'q' (omega_{q+1,q}) at 'n' photons
    return transitions

def get_res_response(eigen_energies):
    """Produce the readout resonator frequencies at each qubit state

    Args:
        eigen_energies (List[float]): eigenenergies produced by the
            diagonalize_ladder(params)
    """
    # Maximum number of photons, maximum number of transmon levels
    nmax, tmax = len(eigen_energies), len(eigen_energies[0])
    response = [np.array([eigen_energies[n+q+1,q] - eigen_energies[n+q,q]
                for n in range(0, nmax-q-1)])
                for q in range(tmax)]

    #response[q][n] is the resonator frequency at 'n' photons when the qubit is
    # in state 'q'
    return response

def transmon_perturbative(tmax, omega_q, eta, g):
    """Produce energies and cuplings of the transmon perturbatively
    
    Uses an anharmonic approximation of the transmon to get the energies

    Args:
        tmax (int): maximum number of transmon levels
        omega_q (float): qubit frequency, eta: transmon anharmonicity (defined
            positive).
        g (float): coupling normalization. Value of the coupling between levels
            0 and 1.
    """
    qubit_energy_list = [omega_q*q -
                          q*(q-1)/2*eta -
                          q*(q-1)*(q-2)/4*eta**2/omega_q
                          for q in range(tmax)]
    g_list = [g*math.sqrt(q+1)*(1-q/2*eta/omega_q) for q in range(tmax-1)]
    
    #qubit_energy_list[q] is transmon energy for level 'q'
    #g_list[q] is transmon charge matrix element between levels 'q+1' and 'q'
    return [qubit_energy_list, g_list]


def transmon_numerical(tmax, omega_q, eta, g, qmax=20):
    nmax = 2*qmax + 1
    n = np.diag([i for i in range(-qmax, qmax + 1)])
    # charge displacement operator by 1
    d1 = np.diag([1 for i in range(1, nmax)], -1)

    def get_h(EC, EJ):
        H = 4*EC*(n @ n) -EJ*(d1 + d1.T)/2
        return H

    def obj_function(params, *args):
        omega_q, eta = args
        EC, EJ = params
        H = get_h(EC, EJ)
        e = np.linalg.eigh(H)[0]
        omega_q_calc = e[1]-e[0]
        eta_calc = (e[1]-e[0]) - (e[2]-e[1])
        return (omega_q_calc - omega_q)**2 + (eta_calc - eta)**2
    # find appropriate EC and EJ to give the desired frequency and anharmonicity
    sol = minimize(obj_function, [0.2, 20], args=(omega_q, eta),
                   method='Nelder-Mead', tol=1e-16)
    EC, EJ = sol.x

    H = get_h(EC, EJ)
    e, v = np.linalg.eigh(H)

    qubit_energy_list = e[0:tmax] - e[0]
    g_norm = v[:,0].T.conj() @ n @ v[:,1]
    # taking absolute value by hand here
    g_list = np.array([g/g_norm*np.abs(v[:,q].T.conj() @ n @ v[:,q+1])
                       for q in range(tmax-1)])
    # qubit_energy_list[q] is transmon energy for level 'q'
    # g_list[q] is transmon charge matrix element between levels 'q+1' and 'q'
    return [qubit_energy_list, g_list]