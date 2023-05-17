#!/usr/bin/env python3.8

from subprocess import check_output
import os, re, enum
import pgen_interface_pb2 as pi

@enum.unique
class mosfet_mode(enum.Enum):
    HP = 1
    ACC = 2

re_param = re.compile(r"^(?P<name>[^:]+):\s+(?P<value>\S+)(?:\s*\[(?P<unit>[^\]]+)\])?$")
def parse_param(line):
    m = re_param.match(line)
    return m['name'], float(m['value']), m['unit']

def parse_mosfet(mosfet, lines):
    for line in lines:
        if line:
            name, value, unit = parse_param(line)
            if unit == 'uA/um':
                value *= 1e-6
            setattr(mosfet, name, value)
        else:
            break

def parse_wire(wire, lines):
    name, value, _ = parse_param(next(lines))
    wire.Resistivity = value

def parse_output(output_parameter, lines):
    it = iter(lines.splitlines())

    try:
        while True:
            line = next(it)

            if line.startswith('NMOS'):
                if line.endswith('(Target)'):
                    parse_mosfet(output_parameter.nmos, it)
                elif line.endswith('(Reference)'):
                    parse_mosfet(output_parameter.nmos_ref, it)
            elif line.startswith('PMOS'):
                if line.endswith('(Target)'):
                    parse_mosfet(output_parameter.pmos, it)
                elif line.endswith('(Reference)'):
                    parse_mosfet(output_parameter.pmos_ref, it)
            elif line.startswith('Bulk wire'):
                if line.endswith('(Target)'):
                    parse_wire(output_parameter.wire, it)
                elif line.endswith('(Reference)'):
                    parse_wire(output_parameter.wire_ref, it)
    except StopIteration:
        pass


def run(pgen, mode, temperature, node, vdd, vth):
    pgen_output = pi.PgenOutput()

    pgen_output.user_input.temperature = temperature
    pgen_output.user_input.technology_node = node
    pgen_output.user_input.mode = mode.value
    pgen_output.user_input.Vdd = vdd
    pgen_output.user_input.Vth0 = vth

    cmd = ('python3.8', pgen,
        '--mosfet_mode', str(mode.value),
        '--temperature', str(temperature),
        '--node', str(node),
        '--vdd', str(vdd),
        '--vth', str(vth))
    
    #parse_output(pgen_output.output_parameter, check_output(cmd, text=True, cwd=os.path.dirname(pgen)))
    parse_output(pgen_output.output_parameter, check_output(cmd, text=True))

    return pgen_output

def main():
    pass

if __name__ == '__main__':
    main()
