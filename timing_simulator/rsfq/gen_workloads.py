import supermarq as sm
import supermarq.benchmarks.vqe_proxy
import cirq, os, multiprocessing

workloads = ['ghz', 'bitcode', 'hamiltonian', 'merminbell', \
            'phase', 'qaoa_fermionic', 'qaoa_vanilla', 'vqe']

def supermarq_to_openqasm (workload, nq):

    circuit = None

    if os.path.isfile ("workloads/{}_{}".format (workload, nq)):
        return

    # quantum circuit setup.
    print ("{} with {} qubits".format (workload, nq))
    if workload == 'ghz':
        circuit = sm.benchmarks.ghz.GHZ (nq).circuit ()
    elif workload == 'bitcode':
        init_state = [1 for _ in range (nq)]
        circuit = sm.benchmarks.bit_code.BitCode (nq, 2, init_state).circuit ()
    elif workload == 'hamiltonian':
        circuit = sm.benchmarks.hamiltonian_simulation.HamiltonianSimulation (nq).circuit ()
    elif workload == 'merminbell':
        circuit = sm.benchmarks.mermin_bell.MerminBell (nq).circuit ()
    elif workload == 'phase':
        init_state = [1 for _ in range (nq)]
        circuit = sm.benchmarks.phase_code.PhaseCode (nq, 2, init_state).circuit ()
    elif workload == 'qaoa_fermionic':
        circuit = sm.benchmarks.qaoa_fermionic_swap_proxy.QAOAFermionicSwapProxy (nq).circuit ()
    elif workload == 'qaoa_vanilla':
        circuit = sm.benchmarks.qaoa_vanilla_proxy.QAOAVanillaProxy (nq).circuit ()
    elif workload == 'vqe':
        circuit = supermarq.benchmarks.vqe_proxy.VQEProxy (nq).circuit ()[0]

    # Qubit setup.
    if workload == 'bitcode' or workload == 'phase':
        qubits = cirq.LineQubit.range (2*nq-1)
    else:
        qubits = cirq.LineQubit.range (nq)

    # cirq to OpenQASM.
    qasm_output = str (cirq.QasmOutput ((circuit.all_operations ()), qubits))
    file_name = "{}_{}".format (workload, nq)
    file = open ("workloads/{}".format (file_name), "w")
    file.write (qasm_output)
    file.close ()
    return


def main ():
    ps = list ()
    for nq in range (1, 11):
        for workload_ in workloads:
            p = multiprocessing.Process (target=supermarq_to_openqasm, args=(workload_, 2**nq))
            p.start ()
            ps.append (p)

    for p_ in ps:
        p_.join ()


if __name__ == "__main__":
    main ()