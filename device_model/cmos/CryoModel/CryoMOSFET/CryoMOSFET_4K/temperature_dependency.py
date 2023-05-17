import numpy as np

# [1] M Shin et.al., "Low temperature characterization of 14nm FDSOI CMOS devices"
# [2] H Zhao et.al., "Modeling of a standard 0.35μm CMOS technology operating from 77 K to 300 K"

class temperature_dependency:
    
    '''INPUT'''
    temperature = None
    node = None
    Vdd = None
    Vth0_300k = None
    # NMOS:1, PMOS:2
    mos_type = None

    '''OUTPUT'''
    # relative scale of major MOSFET variables
    Vth0_rel = None # = Vth0_{temperature,node,Vth0,300k,mos_type} / Vth0_300k
    u0_rel = None # = u0_{temperature,node,Vth0,300k,mos_type} / u0_300k
    vsat_rel = None # = vsat_{temperature,node,Vth0,300k,mos_type} / vsat_300k


    def __init__ (self, temperature, node, Vdd, Vth0_300k, mos_type, variables):
        self.Vth0_rel = self.vth0_model (temperature)
        self.u0_rel = self.u0_model (temperature, mos_type, variables)
        self.vsat_rel = self.vsat_model (temperature, mos_type)


    # Model Vth0 dependency based on our measurement (i.e., 180nm sample)
    def vth0_model (self, temperature):
        vth0_300k_ref = 0.54
        vth0_4k_ref = 0.7
        Vth0_temperature = ((vth0_300k_ref - vth0_4k_ref) / 296 * (temperature - 300) + vth0_300k_ref)/vth0_300k_ref;
        return Vth0_temperature

    
    # Model u0 dependency based on [1]
    def u0_model (self, temperature, mos_type, variables):

        leffs = [300, 3000]
        u0n_cryo = [273.4, 193]
        u0p_cryo = [273.4, 193]
        u0n = [107, 91]
        u0p = [107, 91]
        
        leff = variables.leff
        u0_temperature = None
        u0_4k = None
        u0_300k = None

        # in case the target leff exists in our db (leffs)
        if leff in leffs:
            index_ = leffs.index (leff)
            if mos_type == 1:
                u0_4k = u0n_cryo [index_]
                u0_300k = u0n [index_]
            elif mos_type == 2:
                u0_4k = u0p_cryo [index_]
                u0_300k = u0p [index_]
        
        # in case the target leff doesn't exist in our range
        elif leff > max (leffs):
            if mos_type == 1:
                u0_4k = u0n_cryo [-1]
                u0_300k = u0n [-1]
            elif mos_type == 2:
                u0_4k = u0p_cryo [-1]
                u0_300k = u0p [-1]
            
        elif leff < min (leffs):
            if mos_type == 1:
                u0_4k = u0n_cryo [0]
                u0_300k = u0n [0]
            elif mos_type == 2:
                u0_4k = u0p_cryo [0]
                u0_300k = u0p [0]
        
        # in case the target leff exist in our range
        # we conduct linear interpolation to find u0_300k,77k
        else:
            high_index = None
            low_index = None

            for i in range (len(leffs)):
                if leff < leffs[i]:
                    high_index = i
                    low_index = i-1
                    break
            
            weight_ = [leffs[high_index] - leff, leff - leffs[low_index]]
            weight_ = [i/sum(weight_) for i in weight_]

            if mos_type == 1:
                u0_4k = np.average ([u0n_cryo[low_index], u0n_cryo[high_index]], weights=weight_)
                u0_300k = np.average ([u0n[low_index], u0n[high_index]], weights=weight_)
            elif mos_type == 2:
                u0_4k = np.average ([u0p_cryo[low_index], u0p_cryo[high_index]], weights=weight_)
                u0_300k = np.average ([u0p[low_index], u0p[high_index]], weights=weight_)

        # linear interpolation to find u0_temperature between u0_300k and u0_77k
        weight_ = [300-temperature, temperature-4]
        weight_ = [i/sum(weight_) for i in weight_]
        u0_temperature = np.average ([u0_4k, u0_300k], weights=weight_)/u0_300k
        return u0_temperature


    # Model vsat dependency based on [2]
    def vsat_model (self, temperature, mos_type):
        if mos_type == 1:
            pvsat0 = 1.27e+05
            pvsat1 = 2.93e+03
            pvsat2 = -25.116
            pvsat3 = 0.0722
            pvsat4 = -7.24e-05
            vsat_ref = 1.08e+05

        elif mos_type == 2:
            pvsat0 = 1.69e+05
            pvsat1 = -514.68
            pvsat2 = 6.365
            pvsat3 = -0.0328
            pvsat4 = 4.94e-05
            vsat_ref = 1.02e+05

        # as saturation velocity does not meaningfully increase below 77K...
        if temperature < 77:
            temperature = 77
        vsat_temperature = (pvsat0 + pvsat1 * temperature + pvsat2 * pow (temperature, 2) + pvsat3 * pow (temperature, 3) + pvsat4 * pow(temperature, 4))/vsat_ref;
        return vsat_temperature


