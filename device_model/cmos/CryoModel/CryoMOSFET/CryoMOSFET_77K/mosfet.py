from ptm import *
from temperature_dependency import *
from math import *
import numpy as np
# [1] Chenming Calvin Hu, "modern semiconductor devices for integrated circuits"
# [2] CK Dabhi et.al., "BSIM4 4.8.1 MOSFET Model"
# [3] W. Bludau et.al., Temperature dependence of the band gap of silicon
# [4] W. Jungling et.al., On modeling the intrinsic number and fermi levels for device and process simulation
# [5] H Zhao et.al., "Modeling of a standard 0.35μm CMOS technology operating from 77 K to 300 K"


# Calculate MOSFET and its characteristics (i.e., Ion, Isub, Igate)
# Equations are based on [1],[2]
class mosfet:

    '''INPUT'''
    temperature = None
    node = None
    Vdd = None
    Vth0_300k = None
    # NMOS:1, PMOS:2
    mos_type = None
    # HP: 1, DRAM access: 2
    mos_mode = None


    '''CONSTANTS'''
    BOLTZMANN = 8.6173303e-5
    EOX = 3.453e-11
    ESI = 1.035918e-10
    CHARGE = 1.602e-19
    NMOS_SCATTERING_FACTOR = 2.283*0.825
    PMOS_SCATTERING_FACTOR = 2.283*0.625
    WIDTH = 1e-6
    CEFF = 0.67
    ABACC = 4.97232e-7
    BBACC = 7.45669e+11
    ABINV = 3.75956e-7
    BBINV = 9.82222e+11
    AGCN = 4.97232e-7
    BGCN = 7.45669e+11
    AGCP = 3.42537e-7
    BGCP = 1.16645e+12
    AGSDN = 4.97232e-7
    BGSDN = 7.45669e+11
    AGSDP = 3.42537e-7
    BGSDP = 1.16645e+12


    '''MOSFET variables and their temperature dependency'''
    variables = None
    temperature_dependency = None
    Vth0 = None
    u0 = None
    vsat = None


    '''INTERMEDIATE VARIABLES'''
    ni = None
    Vth_on = None
    Vth_off = None
    Vgs_on = None

    '''OUTPUT'''
    Ion = None
    Isub = None
    Igate = None

    
    def __init__ (self, temperature, node, Vdd, Vth0_300k, mos_type, mosfet_mode):
        self.variables = ptm (node, mos_type)
        self.temperature = temperature
        self.node = node
        self.Vdd = Vdd
        self.Vth0_300k = Vth0_300k
        self.mos_type = mos_type
        self.mos_mode = mosfet_mode
        self.temperature_dependency = temperature_dependency (temperature, node, Vdd, Vth0_300k, mos_type, self.variables)
        self.adopt_temperature_dependency ()
        self.calc_currents ()


    def adopt_temperature_dependency (self):
        self.Vth0 = self.Vth0_300k * self.temperature_dependency.Vth0_rel
        self.u0 = self.variables.u0 * self.temperature_dependency.u0_rel
        self.vsat = self.variables.vsat * self.temperature_dependency.vsat_rel
        #self.debugging ()

    def debugging (self):
        print (self.temperature_dependency.Vth0_rel)
        print (self.temperature_dependency.u0_rel)
        print (self.temperature_dependency.vsat_rel)

    # Temperature depedence of bandgap based on [3]
    def bandgap (self, temperature):
        bandgap_energy = None
        if temperature <= 170:
            bandgap_energy = 1.17 + 1.059e-5*temperature - 6.05e-7*(temperature**2)
        else:
            bandgap_energy = 1.1785 - 9.025e-5*temperature - 3.05e-7*(temperature**2)
        return bandgap_energy

    # Temperature dependence of Ni based on [4]
    def get_intrinsic_carrier_density (self, temperature):
        e_eff_mass = 1.045 + 4.5e-4 * temperature
        h_eff_mass = 0.523 + 1.4e-3 * temperature - 1.48e-6 * (temperature**2)
        ncnv_sqrt = exp (45.13 + 0.75*log (((temperature/300)**2) * (e_eff_mass*h_eff_mass)))
        ni = ncnv_sqrt * exp (-1 * self.bandgap (temperature)/(2*self.BOLTZMANN*temperature))
        return ni


    def get_vth_on (self, temperature, Vdd):
        ni = self.get_intrinsic_carrier_density (temperature)
        surface_potential = 0.4 + self.BOLTZMANN * temperature * log (self.variables.ndep/ni)
        xdep = sqrt (2*self.ESI * surface_potential / (self.CHARGE*self.variables.ndep*1000000))
        lt0 = sqrt (3*self.variables.toxm*xdep)
        V_shift_dibl = -0.5 / (cosh (self.variables.dsub * self.variables.leff / lt0) - 1) * (self.variables.eta0) * Vdd
        V_shift_sch = -0.5 * self.variables.dvt0 / (cosh (self.variables.dvt1 * self.variables.leff / lt0) - 1) * 2*(self.BOLTZMANN * temperature * log (self.variables.ndep * self.variables.nsd / (ni**2)) - surface_potential)
        Vth_on = self.Vth0 + V_shift_dibl + V_shift_sch
        return Vth_on


    def get_vth_off (self, temperature, Vdd):
        ni = self.get_intrinsic_carrier_density (temperature)
        surface_potential = 0.4 + self.BOLTZMANN * temperature * log (self.variables.ndep/ni)
        xdep = sqrt (2*self.ESI * surface_potential / (self.CHARGE*self.variables.ndep*1000000))
        lt0 = sqrt (3*self.variables.toxp*xdep)
        V_shift_dibl = -0.5 / (cosh (self.variables.dsub * self.variables.leff / lt0) - 1) * (self.variables.eta0) * Vdd
        V_shift_sch = -0.5 * self.variables.dvt0 / (cosh (self.variables.dvt1 * self.variables.leff / lt0) - 1) * 2*(self.BOLTZMANN * temperature * log (self.variables.ndep * self.variables.nsd / (ni**2)) - surface_potential)
        Vth_off = self.Vth0 + V_shift_dibl + V_shift_sch
        return Vth_off


    def calc_currents (self):
        # for HP transistor
        if self.mos_mode == 1:
            self.Vth_on = self.get_vth_on (self.temperature, self.Vdd)
            self.Vth_off = self.get_vth_off (self.temperature, self.Vdd)
            self.Vgs_on = self.Vdd
        # for DRAM access transistor
        # Assume the worst performance condition (Vg=Vpp (=Vdd+Vth_on) and Vs=Vdd/2)
        if self.mos_mode == 2:
            self.Vth_on = self.get_vth_on (self.temperature, self.Vdd/2)
            self.Vth_off = self.get_vth_off (self.temperature, self.Vdd)
            self.Vgs_on = self.Vdd/2 + self.Vth_on

        # Mobility
        # "Scattering factor" indicates the aggregated temperature depedency of ua and ub from [5]
        Eeff = (self.Vgs_on + self.Vth_on)/self.variables.toxm/6
        scattering_factor_77k = self.NMOS_SCATTERING_FACTOR if (self.mos_type == 1) else self.PMOS_SCATTERING_FACTOR
        scattering_factor = (1-scattering_factor_77k)/(300-77)*(self.temperature-77) + scattering_factor_77k
        ueff = self.u0 / (1 + self.variables.ua*Eeff + self.variables.ub*(Eeff**2)) / scattering_factor

        # Ion
        ni = self.get_intrinsic_carrier_density (self.temperature)
        surface_potential = 0.4 + self.BOLTZMANN * self.temperature * log (self.variables.ndep/ni)
        Cdep = sqrt (self.CHARGE * self.EOX * 3 * self.variables.ndep * 1e6/2/surface_potential)
        Coxe = self.EOX / self.variables.toxm
        mfactor = 1 + Cdep/Coxe
        Idsat_long = self.WIDTH / (2*mfactor*self.variables.leff) * Coxe * ueff * ((self.Vgs_on - self.Vth_on)**2)
        Idsat_short = Idsat_long / (1 + ueff / 2 * (self.Vgs_on - self.Vth_on) / (mfactor*self.vsat*self.variables.leff))
        Idsat_par = Idsat_short / (1 + self.variables.rdsw * Idsat_short / (self.Vgs_on - self.Vth_on))
        self.Ion = Idsat_par


        # Isub
        I0 = self.u0 * self.WIDTH / self.variables.leff * Cdep * ((self.BOLTZMANN*self.temperature)**2)
        self.Isub = I0 * (1 - exp (-1*self.Vdd/self.BOLTZMANN/self.temperature)) * exp (((-1*self.Vth_off - (self.variables.voff + self.variables.voffl / self.variables.leff))/((1 + (mfactor-1)*self.variables.nfactor)*self.BOLTZMANN*self.temperature)))

        # Igate
        vfbzb = self.variables.vfb 
        vfbzb = vfbzb if (self.mos_type == 1) else -1*vfbzb
        vgsteff = self.Vdd - self.Vth_on
        vgs = self.Vdd
        vgse = self.Vdd
        vgd = self.Vdd
        vgb = self.Vdd
        voxacc = 0.5 * (vfbzb - self.Vdd - 0.02 + sqrt ((vfbzb - self.Vdd - 0.02)**2 + 0.08*vfbzb))
        voxdepinv = self.Vdd - vfbzb - surface_potential
        toxratio = pow ((self.variables.toxref / self.variables.toxm), self.variables.ntox) / self.variables.toxm / self.variables.toxm
        toxratio_edge = pow (self.variables.toxref / self.variables.toxm / self.variables.poxedge, self.variables.ntox) / (self.variables.toxm * self.variables.poxedge) / (self.variables.toxm * self.variables.poxedge)
        vauxacc = self.variables.nigbacc * (self.BOLTZMANN * self.temperature) * log (1 + exp (-1 * (vgb - vfbzb) / self.variables.nigbacc / (self.BOLTZMANN * self.temperature)))
        vauxinv = self.variables.nigbinv * (self.BOLTZMANN * self.temperature) * log (1 + exp (-1 * (voxdepinv - self.variables.eigbinv) / self.variables.nigbinv / (self.BOLTZMANN * self.temperature)))
        vauxigc = self.variables.nigc * (self.BOLTZMANN * self.temperature) * log (1 + exp (-1 * (vgse - self.Vth_on) / self.variables.nigc / (self.BOLTZMANN * self.temperature)))
        igbacc = self.ABACC * toxratio * vgb * vauxacc * exp (-1 * self.BBACC * self.variables.toxm * (self.variables.aigbacc - self.variables.bigbacc * voxacc) * (1 + self.variables.cigbacc * voxacc)) * self.variables.leff * 1e-6
        igbinv = self.ABINV * toxratio * vgb * vauxinv * exp (-1 * self.BBINV * self.variables.toxm * (self.variables.aigbinv - self.variables.bigbinv * voxdepinv) * (1 + self.variables.cigbinv * voxdepinv)) * self.variables.leff * 1e-6
        vfbsd = self.BOLTZMANN * self.temperature * log (self.variables.ngate / self.variables.nsd);
        vgs_primed = pow (pow ((vgs - vfbsd), 2) + 1.0e-4, 0.5);
        vgd_primed = pow (pow ((vgd - vfbsd), 2) + 1.0e-4, 0.5);
        if (self.mos_type == 1):
            igc0 = self.AGCN * toxratio * vgse * vauxigc * exp (-1 * self.BGCN * self.variables.toxm * (self.variables.aigc - self.variables.bigc * voxdepinv) * (1 + self.variables.cigc * voxdepinv)) * self.variables.leff * 1e-6
            igs = self.AGSDN * toxratio_edge * vgs * vgs_primed * exp (-1 * self.BGSDN * self.variables.toxm * self.variables.poxedge * (self.variables.aigsd - self.variables.bigsd * vgs_primed) * (1 + self.variables.cigsd * vgs_primed)) * self.variables.lint * 1e-6
            igd = self.AGSDN * toxratio_edge * vgd * vgd_primed * exp (-1 * self.BGSDN * self.variables.toxm * self.variables.poxedge * (self.variables.aigsd - self.variables.bigsd * vgd_primed) * (1 + self.variables.cigsd * vgd_primed)) * self.variables.lint * 1e-6
        if (self.mos_type == 2):
            igc0 = self.AGCP * toxratio * vgse * vauxigc * exp (-1 * self.BGCP * self.variables.toxm * (self.variables.aigc - self.variables.bigc * voxdepinv) * (1 + self.variables.cigc * voxdepinv)) * self.variables.leff * 1e-6
            igs = self.AGSDP * toxratio_edge * vgs * vgs_primed * exp (-1 * self.BGSDP * self.variables.toxm * self.variables.poxedge * (self.variables.aigsd - self.variables.bigsd * vgs_primed) * (1 + self.variables.cigsd * vgs_primed)) * self.variables.lint * 1e-6
            igd = self.AGSDP * toxratio_edge * vgd * vgd_primed * exp (-1 * self.BGSDP * self.variables.toxm * self.variables.poxedge * (self.variables.aigsd - self.variables.bigsd * vgd_primed) * (1 + self.variables.cigsd * vgd_primed)) * self.variables.lint * 1e-6
        self.Igate = igd + igs + igc0 + igbinv + igbacc


if __name__ == "__main__":
    nmos = mosfet (300, 22, 0.8, 0.50308, 1)
    print ("Vth0:\t\t%.4f [V]" % nmos.Vth0)
    print ("Vth_on:\t\t%.4f [V]" % nmos.Vth_on)
    print ("Vth_off:\t%.4f [V]" % nmos.Vth_off)
    print ("Ion:\t\t%.1f [uA/um]" % (nmos.Ion*1e6))
    print ("Isub:\t\t%.4f [uA/um]" % (nmos.Isub*1e6))
    print ("Igate:\t\t%.4f [uA/um]" % (nmos.Igate*1e6))
