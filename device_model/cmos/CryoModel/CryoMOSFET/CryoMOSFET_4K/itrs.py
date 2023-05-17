import sys

# Vdd, Vth0_n, Vth0_p of itrs-standard transistors 
class itrs:
    
    '''INPUT'''
    node = None

    '''OUTPUT'''
    Vdd = None
    Vth_n = None
    Vth_p = None


    def __init__ (self, node):

        if (node == 16):
            self.Vdd = 0.7
            self.Vth_n = 0.47965
            self.Vth_p = 0.43121
        
        elif (node == 22):
            self.Vdd = 0.8
            self.Vth_n = 0.50308
            self.Vth_p = 0.4606
        
        elif (node == 32):
            self.Vdd = 0.9
            self.Vth_n = 0.49396
            self.Vth_p = 0.49155
        
        elif (node == 45):
            self.Vdd = 1.0
            self.Vth_n = 0.46893
            self.Vth_p = 0.49158
        
        elif (node == 65):
            self.Vdd = 1.1
            self.Vth_n = 0.423
            self.Vth_p = 0.365
        
        elif (node == 90):
            self.Vdd = 1.2
            self.Vth_n = 0.397
            self.Vth_p = 0.339
        
        elif (node == 130):
            self.Vdd = 1.3
            self.Vth_n = 0.3782
            self.Vth_p = 0.321
        
        elif (node == 180):
            self.Vdd = 1.8
            self.Vth_n = 0.3999
            self.Vth_p = 0.42
        
        else:
            print ("pgen doesn't support %dnm technology yet." % node)
            sys.exit ()

