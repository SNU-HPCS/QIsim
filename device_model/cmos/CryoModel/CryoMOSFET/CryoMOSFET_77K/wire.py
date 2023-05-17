import sys


class wire:
    
    '''INPUT'''
    # 1:Bulk, 2:Narrow
    wire_mode = None
    temperature = None
    width = None
    height = None


    '''OUTPUT'''
    Rwire = None


    def bulk_resistivity (self):
        # Copper (Cu)
        res_coeff = 1.724e-8
        temp_coeff = 4.041e-3
        self.Rwire = res_coeff * (1 + (self.temperature - 293) * temp_coeff)*1e8 # [uOhm*cm]

    
    def narrow_resistivity (self):
        if self.width*self.height == 0:
            print ("ERROR: Narrow mode needs the wire width and height as inputs.")
            sys.exit ()
        Rgbsf = 0.0274 + 92/((self.width*self.height)**0.5) # [uOhm*cm] (should 1-digit scale)
        Rbulk = 6.966e-3*self.temperature - 0.3172
        self.Rwire = Rgbsf + Rbulk


    def __init__ (self, wire_mode, temperature, width, height):

        self.wire_mode = wire_mode
        self.temperature = temperature
        self.width = width
        self.height = height
        
        # Bulk
        if wire_mode == 1:
            self.bulk_resistivity ()
        # Narrow
        else:
            self.narrow_resistivity ()

