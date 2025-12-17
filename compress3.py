from PIL import Image
import numpy as np
from bitstream import bitstream
from huff0 import huff0
from huffman import huffman
from lzs import lzs
#from lz77 import lz77
from lz0 import lz0
import math
from deflate2 import deflate2 as deflate

class compress():
	def __init__(self,image,filename):
		self.image=image
		self.filename=filename
		self.compres=False
		self.kthreshold=9#6 #significant bit threashold
		self.jthreshold=2#2#pyramid threshold
		self.i2threshold=True # true means compress i2==1
		
		self.size1=[[512,64,64],[64,8,8]]
		#self.size2=[[8,8,8],[2,1,1]]
		self.size2=[[9,9,9],[3,3,3]]
		#self.bits=[[9,6,6],[3,3,3]]
		self.bits=[[8,8,8],[2,1,1]]
		self.lz=True
		
	def compress(self):
		image=self.image
		self.bitstream=bitstream(self.filename,'wb')

		w=image.shape[1]
		h=image.shape[0]
		print([w,h])
	
		self.w=w
		self.h=h
		
		n=max(w,h).bit_length()-1
		self.n=n

		self.bitstream.write(w,32)
		self.bitstream.write(h,32)


				
		lengths=None

		image=self.createpyramid2(image)
		im=Image.fromarray(image.astype(np.uint8))
		im.save("/home/andrew/Desktop/asadf/out/"+"asdfa2"+".png")
		#image=self.createpyramid2(image)
		image=image.astype(np.uint8)
		
		image=self.transpose(image)

		image=image.transpose((1,0))
		image=image.reshape((w*h*8))
		#print(np.sum(image==0))
		#print(np.sum(image[:w*h*2]==0))
		#print(np.sum(image[:w*h*4]==0)-np.sum(image[:w*h*2]==0))
		#print(np.sum(image[:w*h*6]==0)-np.sum(image[:w*h*4]==0))
		#print(np.sum(image[:w*h*8]==0)-np.sum(image[:w*h*6]==0))
		#print(w*h*8)
	
		#image,lengths=

		#self.lzencode(image,lengths)
		self.huffman(image,lengths)
		
		#for i in range(n):
			#print(self.images[i][:,:,:,4].shape)
			#
			#
			#im=Image.fromarray(self.pyramid[i][:,:,:,5])
			#im.save("/home/andrew/Desktop/asadf/asdfb"+str(i)+".png")


		self.bitstream.close()
		return image,lengths,self.bits

	
	def decompress(self,image,lengths,nbits):
		#print("decompress")
		self.bitstream=bitstream(self.filename,'rb')
		w=self.bitstream.read(32)
		h=self.bitstream.read(32)
		self.file=self.bitstream
		self.w=w
		self.h=h

		self.bits=nbits

		
		image,lengths=self.dehuffman()
		#image=self.lzdecode(image,lengths)

		image=image.reshape((8,w*h))
		image=image.transpose((1,0))
		image=self.detranspose(image)
		image=image.reshape((h,w,3))
		#image=self.decompress2(image)
		image=self.decompress2(image)
			
		self.file.close()
		
		return image
	

	
	def paeth(self,A,B,C):
		
		p=A.astype(np.int16)+B-C
		a=np.stack([A,B,C],axis=1)
		pa=abs(a.astype(np.int16)-p)
		ind=np.argmin(pa,axis=1)
		
		c=np.asarray([ a[0,ind[0]],a[1,ind[1]],a[2,ind[2]] ])
		return c
		
	def paeth2(self,A,B,C,D):
		p=(A.astype(np.int16)+B-C).reshape((3,1))
	#	p2=(A.astype(np.int16)+D - B).reshape((3,1))
		a=np.stack([A,B,C,D],axis=1)
		#a2=np.stack([A,B,D],axis=1)
		#print(a)
		pa=abs(a.astype(np.int16)-p)
		#pa2=abs(a2.astype(np.int16)-p2)
		#pa=np.concatenate((pa,pa2),axis=1)
		#a=np.concatenate((a,a2),axis=1)
		
		ind=np.argmin(pa,axis=1)
		c=np.asarray([ a[0,ind[0]],a[1,ind[1]],a[2,ind[2]] ])
		#c=np.maximum(0,np.minimum(255,p)).astype(np.uint8).reshape((3))
		
		#print(c.shape)
		return c
		
	def paeth2a(self,A,B,C,D):
		p=(A.astype(np.int16)+B-C).reshape((3,1))
		a=np.stack([A,B,C,D],axis=1)
		#print(a)
		pa=abs(a.astype(np.int16)-p)
		ind=np.argmin(pa,axis=1)
		c=np.asarray([ a[0,ind[0]],a[1,ind[1]],a[2,ind[2]] ])
		return c
			
	def paeth2b(self,A,B,C,D,E):
		p=(A.astype(np.int16)+B-C).reshape((3,1))
		a=np.stack([A,B,C,D,E],axis=1)
		#print(a)
		pa=abs(a.astype(np.int16)-p)
		
		ind=np.argmin(pa,axis=1)
		c=np.asarray([ a[0,ind[0]],a[1,ind[1]],a[2,ind[2]] ])
			
		#print(a)
		#print(p)
		return c
				
	def paeth3(self,A,B,C,D):
		c=((A.astype(np.int16)+B-C)).reshape((3))
		c=np.maximum(0,np.minimum(255,c)).astype(np.uint8)
	
		#print(a)
		#print(p)
		return c
	


	def paeth4(self,A,B,C,D):
		dy=C.astype(np.int16)-A.astype(np.int16)
		dx=B.astype(np.int16)-C.astype(np.int16)
		p=(A.astype(np.int16)+B-C).reshape((1,3))
		p2=(B.astype(np.int16)+(A.astype(np.int16)-C)*(D.astype(np.int16)-B)//(B.astype(np.int16)-C)).reshape((1,3))
		#p2=(A.astype(np.int16)+D - B).reshape((3,1))
		a=np.stack([A,B,C,D],axis=0)
		#a2=np.stack([A,B,C,D],axis=1)
		b=(((A-C)*dx)>0).reshape((1,3))
		p=p*(1-b)+b*p2
		#print(a)
		pa=abs(a.astype(np.int16)-p)
		#pa2=abs(a2.astype(np.int16)-p2)
		#p=np.concatenate((pa,pa2),axis=1)
		#a=np.concatenate((a,a2),axis=1)
		
		ind=np.argmin(pa,axis=0)
		c=np.asarray([ a[ind[0],0],a[ind[1],1],a[ind[2],2] ])
		return c
	
	def paeth5(self,A,B,C,D):
		p=(A.astype(np.int16)+B-C).reshape((3,1))
		#p2=(B.astype(np.int16)+(A.astype(np.int16)-C)*(D.astype(np.int16)-B)//(B.astype(np.int16)-C)).reshape((3,1))
		#p2=(A.astype(np.int16)+D - B).reshape((3,1))
		a=np.stack([A,B,C,D],axis=1)
		#a2=np.stack([A,B,C,D],axis=1)
		b=(((A-C)*(B-C))>=0).reshape((1,3))
		#p=p*(1-b)+b*p2
		#print(a)
		pa=abs(a.astype(np.int16)-p)
		
		#pa2=abs(a2.astype(np.int16)-p2)
		#p=np.concatenate((pa,pa2),axis=1)
		#a=np.concatenate((a,a2),axis=1)
		
		ind=np.argmin(pa,axis=1)
		c=np.asarray([ a[0,ind[0]],a[1,ind[1]],a[2,ind[2]] ]).reshape((1,3))
		#print(D.reshape((1,3)))
		#print(b)
		#print(c)
		c=c*(1-b)+D.reshape((1,3))*b
		#print(c)
		return c
	


	
	def paeth8(self,A1,A2,A3,A4,A5,B1,B2,B3,B4,B5,C1,C2,flag=False):
		
		dx1=abs(A1.astype(np.int16)-B2)
		dx2=abs(A3.astype(np.int16)-B3)
		dx3=abs(A5.astype(np.int16)-B4)
		dx4=abs(C1.astype(np.int16)-C2)
		
		
	

	
		a=np.stack([C2,B3,B2,B4],axis=0)#
		#print(a)
		pa=np.stack([dx4,dx2,dx1,dx3],axis=0)#,dC,dD

		ind=np.argmin(pa,axis=0)
		c=np.asarray([ a[ind[0],0],a[ind[1],1],a[ind[2],2] ])
		

	
		return c
	
								
	def createpyramid2(self,image):
		
		w=self.w
		h=self.h
	
		
		image2=np.zeros((h,w,3),np.int16)
		#print(image[:,0])
		image2[0,0,:]=image[0,0,:]
		for i in range(1,w):
			image2[0,i,:]=image[0,i,:].astype(np.int16)-image[0,i-1,:]
			
		for j in range(1,h):
			image2[j,0,:]=image[j,0,:].astype(np.int16)-image[j-1,0,:]	
		
		for j in range(1,h):	
			for i in range(1,w):
				#
				if  i<w-1 and j>1:
					#D=self.paeth6(image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:],image[j-1,i+1,:],image[j-2,i+1,:],image[j,i,:])
					D=self.paeth2(image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:],image[j-1,i+1,:])
				elif  i<w-2:
					#D=self.paeth8(image[j-2,i-2,:],image[j-2,i-1,:],image[j-2,i,:],image[j-2,i+1,:],image[j-2,i+2,:],   image[j-1,i-2,:],image[j-1,i-1,:],image[j-1,i,:],image[j-1,i+1,:],image[j-1,i+2,:], image[j,i-2,:],image[j,i-1,:])
					D=self.paeth2(image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:],image[j-1,i+1,:])
				elif i<w-1:
					#print("dfgh")
					D=self.paeth2(image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:],image[j-1,i+1,:])
				else:
					D=self.paeth(image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:])
				
				#print([j,i,image[j,i,:],D,image2[j,i,:]])

				image2[j,i,:]=image[j,i,:].astype(np.int16)-D
					
	
		#print(image2[:,0])
		
		return image2
		


	def decompress2(self,image):
		w=self.w
		h=self.h
	
		for i in range(1,w):
			image[0,i,:]=image[0,i,:]+image[0,i-1,:]
		for j in range(1,h):
			image[j,0,:]=image[j,0,:]+image[j-1,0,:]
		for j in range(1,h):
			for i in range(1,w):
				if  i<w-1 and j>1:
					#D=self.paeth6(image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:],image[j-1,i+1,:],image[j-2,i+1,:],None)
					D=self.paeth2(image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:],image[j-1,i+1,:])
				elif i<w-2 :
					#D=self.paeth8(image[j-2,i-2,:],image[j-2,i-1,:],image[j-2,i,:],image[j-2,i+1,:],image[j-2,i+2,:],   image[j-1,i-2,:],image[j-1,i-1,:],image[j-1,i,:],image[j-1,i+1,:],image[j-1,i+2,:], image[j,i-2,:],image[j,i-1,:])
					D=self.paeth2(image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:],image[j-1,i+1,:])
				elif i<w-1:
					D=self.paeth2(image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:],image[j-1,i+1,:])
				else:
					D=self.paeth(image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:])
				#print([j,i,image[j,i,:],D])
				image[j,i,:]=image[j,i,:]+D
			
				
		#print(image[:,0])
	
		
		return image

	
	def transposebits(self,v,nbit):
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

	def	transposebits2(self,array,nbit): #ruins data in origional "array"
		nbit2=array.shape[1]
		length=array.shape[0]
		dtype=np.uint8
		w=np.zeros((length,nbit,nbit2),dtype=dtype)
		arrays2=np.zeros((length,nbit),dtype=dtype)

		for i in range(nbit):
			w[:,nbit-1-i,:]=array%2
			array=array//2
		a=np.zeros((1,nbit2,1))
		a[0,nbit2-1,0]=1
		for i in range(nbit2-1):
			a[0,nbit2-2-i]=a[0,nbit2-1-i,0]*2

		arrays2=np.matmul(w[:,:,:],a)[:,:,0]
		arrays2=arrays2.astype(dtype)
		return arrays2	
						

				
						
	def t1a(self,v2d):
		c=(v2d>=128)
		c1=255-v2d
		c1=c1*2+1
		c2=v2d*2
		v2d=(c*c1)+(1-c)*c2
		return v2d		
		
	def t1b(self,v2d):
		c=v2d%2
		c1=(v2d-1)//2
		c1=255-c1
		c2=v2d//2
		v2d=(c*c1)+(1-c)*c2
		return v2d
		
	def transpose(self,image):
		#print("transpose")
		w=self.w
		h=self.h

		image1=self.t1a(image)
		im=Image.fromarray(image1.astype(np.uint8))
		im.save("/home/andrew/Desktop/asadf/out/asdfa3"+".png")
		image1=image1.reshape((w*h,3))
		image2=self.transposebits2(image1,8)	

		return image2
						
	def detranspose(self,image):
		#print("detranspose")
		w=self.w
		h=self.h
		image2=self.transposebits2(image,3)
		image2=self.t1b(image2)

		return image2
	
			
	


				
	def t3_9(self,array,length,n1,n2): #group symbols of n1 bits into symbols of n2 bits
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


	def t9_3(self,array,length,n1,n2): #split symbols of n1 bits into symbols of n2 bits
		n=n1//n2
		v=[None]*n
		a=(1<<n2)
		for i in range(n):
			v[n-i-1]=array%a
			array=array//a
		array=np.reshape(np.stack(v,axis=1),(-1))
		array=array[:length]
		return array

	
	
	def huffman(self,array,length):
		#print("huffman")
		w=self.w
		h=self.h
		#print(length)
		n=2
		
	
		bits2=6
		size1=(1<<bits2)
		arrays=[None]*n
		lengths=[None]*n
		for i in range(n):
			arrays[i]=array[w*h*(i)*8//n:w*h*(i+1)*8//n]
			lengths[i]=w*h*8//n
			arrays[i],lengths[i]=self.t3_9( arrays[i],lengths[i],3,bits2)

		
		a=0
		for i in range(n):
		#	print(np.sum(arrays[i]==0))
		#	print(np.sum(arrays[i][:w*h*1]==0))
	#		print(np.sum(arrays[i][:w*h*2]==0)-np.sum(arrays[i][:w*h*1]==0))
			a=a+np.sum(arrays[i]==0)/(lengths[i])
			#print(np.sum(arrays[i]==0)/(lengths[i]))
		#print(a/4)
		#image,lengths=
		#print(arrays2.tolist())
		
		freq=[None]*n
		for i in range(n):
			freq[i]=[0]*size1
			
	
		
		for i in range(n):
			for j in range(lengths[i]):
				v=arrays[i][j]
				#print([v,i])
				freq[i][v]=freq[i][v]+1
			#print(freq[i])
		huf=[None]*n

		for i in range(n):#n
			#print(arrays[i].tolist())
			huf[i]=deflate(bits2)
			huf[i].encode(self.bitstream,arrays[i],lengths[i])
			#print(lengths[i])
				
	

		
	def dehuffman(self):
		#print("huffman2")

		n=2
		dtype=np.uint8
		bits1=6
		w=self.w
		h=self.h
		huf=[None]*n
		arrays=[None]*n
		length=[None]*n
	
		for i in range(n):#n
			huf[i]=deflate(bits1)
			arrays[i],length[i]=huf[i].decode(self.bitstream)
			arrays[i]=self.t9_3( arrays[i] , w*h*8//n,bits1,3)
			
		array=np.concatenate(arrays,axis=0)
		length=w*h
		#print(array.shape)
		return array,length


	
	
								
								
def main():
	#print("Asf")
	im = Image.open("/home/andrew/Desktop/asadf/text256.png")
	im =im.convert("RGB")
	image1=np.asarray(im).astype(np.uint8)
	
	a=compress(image1,"/home/andrew/Desktop/asadf/out/asdf.awy")

	b=compress(None,"/home/andrew/Desktop/asadf/out/asdf.awy")
	image,lengths,nbits=a.compress()
	image2=b.decompress(None,None,nbits)
	#print(data)
	im=Image.fromarray(image2)
	im.save("/home/andrew/Desktop/asadf/out/asdf.png")
	im.save("/home/andrew/Desktop/asadf/out/asdf.jpg")
	
	a=(image1==image2).all()
	solut = (~np.equal(image1, image2)).astype(int)
	indices = np.flatnonzero(solut)
	#print(indices)
	#print(solut)
	print("success: "+str(a))
	#print([image1[0,0,:], image2[0,0,:]])
	#print([image1[0,5,:], image2[0,5,:]])
if __name__ == '__main__':
	main()
