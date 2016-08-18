from pyqtree import *
import time
import math
arr={}
numbers=[1000000]
for n in numbers:
	sp=Index(bbox=(0,0,n+1,n+1))
	t0=time.time()
	value=int(math.ceil(0.75*n))
	print value,n
	for i in range(value,n,2):
		sp.insert(i,(i,i,i+1,i+1))
	t1=time.time()
	total=t1-t0
	arr[n]=total
print arr

##{1000: 0.11288690567016602, 10000: 1.5429410934448242, 10: 0.00012612342834472656, 100: 0.005457162857055664}

#skewed {1000: 0.030871868133544922, 10000: 0.3902149200439453, 10: 6.29425048828125e-05, 100: 0.0042629241943359375}
#{1000: 0.03163790702819824, 10000: 0.3713109493255615, 10: 6.103515625e-05, 100000: 5.713748931884766, 100: 0.0018301010131835938}
