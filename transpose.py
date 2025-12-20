import numpy as np

def transposebits(v,nbit):
	#print("change")
	#vshaphe=[3,4]
	#print(v)
	nbit2=v.shape[0]
	w2=np.zeros(nbit,dtype=np.uint64)#8 bits plus
	#n=v.shape[1]
	w=np.zeros((nbit,nbit2),dtype=np.uint64)
	#v2=v[:,0:3].reshape((9))
	v2=v
	#v3=v[:,3]
	for i in range(nbit):
		j=nbit-i-1
		w[j,:]=v2%2
		v2=v2//2
	#print(w)
	for i in range(nbit):
		for j in range(nbit2):
			w2[i]=w2[i]*2+w[i,j]

	#print(w2)
	return w2

def	transposebits2(array,nbit): #ruins data in origional "array"

	nbit2=array.shape[-1]
	shape=list(array.shape)
	#print(shape)
	shape1=shape.copy()
	shape1.insert(-1,nbit)
	#print(shape1)
	shape2=shape.copy()
	shape2[-1]=nbit
	#print(shape2)
	#length=array.shape[0]
	dtype=np.uint8
	w=np.zeros(shape1,dtype=dtype)
	arrays2=np.zeros(shape2,dtype=dtype)

	for i in range(nbit):
		w[...,nbit-1-i,:]=array%2
		array=array//2
	a=np.zeros((nbit2,1))
	a[nbit2-1,0]=1
	for i in range(nbit2-1):
		a[nbit2-2-i]=a[nbit2-1-i,0]*2
	#print(w.shape)
	#print(a.shape)
	arrays2=np.matmul(w[...],a)
	arrays2=arrays2[...,0] #[h,w,8,1]-> [h,w,8]
	arrays2=arrays2.astype(dtype)
	return arrays2	
					
def t3_9(array,length,n1,n2):
	n=n2//n1
	
	length2=(length-1)//n+1
	a=np.zeros((length2*n),np.uint16)
	a[:length]=array
	array=a.reshape((length2,n))#[:,3]
	
	
	
	a= (1<<n1)
	arr=array[:,0].astype(np.uint16)
	for i in range(1,n):
		arr=arr*a+array[:,i] 
	array=arr #array[:,0].astype(np.uint16)*64+ array[:,1]*8+ array[:,2] #[:]
	return array,length2


def t9_3(array,length,n1,n2):
	n=n1//n2
	v=[None]*n
	a=(1<<n2)
	for i in range(n):
		v[n-i-1]=array%a
		array=array//a
	array=np.reshape(np.stack(v,axis=1),(-1))
	array=array[:length]
	return array

				

			
def	transposebit3a(array,nbit): #ruins data in origional "array"
	arrays2=[None]*nbit
	for i in range(nbit):
		arrays2[nbit-1-i]=array%2
		array=array//2
	arrays2=np.stack(arrays2,axis=-1)
	return arrays2	

def	transposebit3b(array,nbit): #ruins data in origional "array"
	array2=array[:,:,:,0]
	for i in range(1,nbit):
		array2=array2*2+array[:,:,:,i]

	return array2
	
def t1a(v2d):
	c=(v2d>=128)
	c1=255-v2d
	c1=c1*2+1
	c2=v2d*2
	wun=np.ones((),dtype=np.uint8)
	v2d=(c*c1)+(wun-c)*c2
	return v2d		
	
def t1b(v2d):
	c=v2d%2
	c1=(v2d-1)//2
	c1=255-c1
	c2=v2d//2
	v2d=(c*c1)+(1-c)*c2
	return v2d

