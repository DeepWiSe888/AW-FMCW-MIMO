import numpy as np

class Mti(object):
    def __init__(self,s1,s2):
        self._moving_avg_alpha = 0.6
        self._mti_alpha = 0.5
        self._map_avg = np.zeros((s1,s2))
        
    def get_mti_map(self,map):
        mti_map = map - self._map_avg*self._mti_alpha
        # mti_map[mti_map < 0] = np.mean(mti_map)
        self._map_avg = map*self._moving_avg_alpha + self._map_avg*(1-self._moving_avg_alpha)
        return mti_map