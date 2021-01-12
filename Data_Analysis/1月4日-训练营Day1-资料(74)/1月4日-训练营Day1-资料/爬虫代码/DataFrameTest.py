import numpy as np
import pandas as pd
print(np.array([1,2,3,4,5]))

print(np.arange(1,10,1))
print(np.array(np.arange(10)))
myList = [[0,1],[1,2],[2,3]]
print(np.array(myList))
myList1= [[0,5],[1,6],[2,7]]
print(np.array(myList1))
List1 = np.array(myList)
List2 = np.array(myList1)
print(List1+List2)
print(np.concatenate((List1,List2),axis=1))
print(np.hstack((List1,List2)))

ser1 = np.array([1,2,3,4,5])
pd1 = pd.Series(ser1,index=np.arange(5))
print(pd1)


ser2 = np.array([6,7,8,9,10])
pd2 = pd.Series(ser2,index=np.arange(5))
print(pd2)

print(pd.DataFrame(ser2,index=np.arange(5),columns=['apple']))


print(pd.Series([3,2,0,1],index=np.arange(4)))
print(pd.Series([0,3,7,2],index=np.arange(4)))


myList2 = [[3,0],[2,3],[0,7],[1,2]]
print(pd.DataFrame(myList2,index=np.arange(4),columns=['apples','oranges']))
