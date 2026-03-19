import numpy as np

def encodepixeldif(rgb1,rgb2):

	d1=np.expand_dims(rgb2.astype(np.int16)[...,0]-rgb1[...,0],axis=-1)
	
	rgb12=rgb1.astype(np.int16)
	rgb12[...,1:3]=rgb12[...,1:3]+d1
	rgb12[...,1:3]=np.maximum(0,np.minimum(255,rgb12[...,1:3])).astype(np.uint8)

	d123=np.zeros_like(rgb1,np.uint8)
	d123=rgb2-rgb12
	d123=d123.astype(np.uint8)
	return d123

def decodepixeldif(rgb1,d123):

	d1=d123[...,0:1]
	d23=d123[...,1:3]

	rgb2=rgb1+d1
	d1=rgb2.astype(np.int16)[...,0:1]-rgb1[...,0:1]
	rgb2=rgb1.astype(np.int16)+d1
	
	rgb2=np.maximum(0,np.minimum(255,rgb2)).astype(np.uint8)
	rgb2[...,1:3]=rgb2[...,1:3]+d23

	return rgb2



def paeth2(A,B,C):
	AB=np.stack([A,B],axis=-1)
	p=(A.astype(np.int16)+B-C)
	max1=np.max(AB,axis=-1)
	min1=np.min(AB,axis=-1)
	c=np.maximum(min1,np.minimum(max1,p)).astype(np.uint8)

	return c

def paeth1(A,B,C,D):
	ABD=np.stack([A,B,D],axis=-1)
	p=(A.astype(np.int16)+B-C)
	max1=np.max(ABD,axis=-1)
	min1=np.min(ABD,axis=-1)
	c=np.maximum(min1,np.minimum(max1,p)).astype(np.uint8)


	return c
			
def paeth1left(A,B,C,D):
	return A
	
def paeth1up(A,B,C,D):
	return B
	
def paeth2left(A,B,C):
	return A
	
def paeth2up(A,B,C):
	return B
	
def getmidcolor(avg):	
	if avg[0]>avg[1]:
		if avg[0]<avg[2]:
			return 0
		elif avg[1]>avg[2]:
			return 1
		else:
			return 2
	else:
		if avg[1]<avg[2]:
			return 1
		elif avg[0]>avg[2]:
			return 0
		else:
			return 2
			
			
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
	
def	transposebits2(array,nbit):
	w=np.unpackbits(np.expand_dims(array,axis=-2),axis=-2)
	arrays2=np.packbits(w,axis=-2)
	return arrays2	
					
def t3_9(array,n1,n2):
	n=n2//n1
	length=array.shape[-1]
	length2=(length-1)//n+1 #round up
	a=np.zeros((length2*n),np.uint16)
	a[:length]=array
	array=a.reshape((length2,n))#[:,3]
	
	
	
	a= (1<<n1)
	arr=array[:,0].astype(np.uint16)
	for i in range(1,n):
		arr=arr*a+array[:,i] 
	array=arr #array[:,0].astype(np.int16)*64+ array[:,1]*8+ array[:,2] #[:]
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

				

			
def	transposebit3a(array,nbit): #ruins data in original "array"

	return np.unpackbits(array[...,np.newaxis],axis=-1)

def	transposebit3b(array,nbit): #ruins data in original "array"
	return np.packbits(array,axis=-1)[...,0]
