import numpy as np

def geo_mean(*args: int | float):
    
    e = np.exp(args)
    s = np.sum(e)
    l = np.log(s)

    return float(l)