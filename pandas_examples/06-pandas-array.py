import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

p = pd.Period("2018-03-11", freq='H')
print(p.day)
p = pd.Period('2012-1-1', freq='D')
print(p.start_time)
print(p.end_time)