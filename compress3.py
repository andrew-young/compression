from PIL import Image
import numpy as np
from bitstream import bitstream
#from huff0 import huff0
from huffman import huffman
#from lzs import lzs
#from lz77 import lz77
#from lz0 import lz0
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
		image=image.astype(np.uint8)
		
		image=self.transpose(image)

		image=image.transpose((1,0))
		image=image.reshape((w*h*8))
		
		self.huffman(image,lengths)
		
		#for i in range(n):
			#print(self.images[i][:,:,:,4].shape)
			#
			#
			#im=Image.fromarray(self.pyramid[i][:,:,:,5])
			#im.save("/home/andrew/Desktop/asadf/asdfb"+str(i)+".png")


		self.bitstream.close()
		return image,lengths

	
	def decompress(self,image,lengths):
		#print("decompress")
		self.bitstream=bitstream(self.filename,'rb')
		w=self.bitstream.read(32)
		h=self.bitstream.read(32)
		self.file=self.bitstream
		self.w=w
		self.h=h

	

		choice=[0]*self.h
		for j in range(1,h):
			choice[j]=self.bitstream.read(2)
			
		image,lengths=self.dehuffman()
		image=image.reshape((8,w*h))
		image=image.transpose((1,0))
		image=self.detranspose(image)
		image=image.reshape((h,w,3))
		image=self.decompress2(image,choice)
			
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

	def paeth2b(self,A,B,C,D):
		p=(A.astype(np.int16)+B-C).reshape((3,1))
		a=np.stack([A,B,C],axis=1)
		#print(a)
		pa=abs(a.astype(np.int16)-p)
		ind=np.argmin(pa,axis=1)
		c=np.asarray([ a[0,ind[0]],a[1,ind[1]],a[2,ind[2]] ])
		return c

	def paeth2c(self,A,B,C,D):
		p=(A.astype(np.int16)+B-C).reshape((3,1))
		c=np.maximum(0,np.minimum(255,p)).astype(np.uint8).reshape((3))
		return c
				
	def paeth2d(self,A,B,C,D):
		c=((A.astype(np.int16)+B)//2).reshape((3))
		#c=np.maximum(0,np.minimum(255,p)).astype(np.uint8).reshape((3))
		return c
		
	def paeth2e(self,A,B,C,D):
		p=((A.astype(np.int16)+B)//2).reshape((3,1))
		a=np.stack([A,B,C,D],axis=1)
		pa=abs(a.astype(np.int16)-p)
		ind=np.argmin(pa,axis=1)
		c=np.asarray([ a[0,ind[0]],a[1,ind[1]],a[2,ind[2]] ])
		a=np.stack([A,B,C],axis=1)
		return c
			
	def paeth3(self,A,B,C,D):
		c=((A.astype(np.int16)+B-C)).reshape((3))
		c=np.maximum(0,np.minimum(255,c)).astype(np.uint8)
		return c
		
	def paeth3b(self,A,B,C,D):
		c=((A.astype(np.int16)+D-B)).reshape((3))
		c=np.maximum(0,np.minimum(255,c)).astype(np.uint8)
		return c

	def paeth3c(self,A,B,C,D):
		return A
		
	def paeth3d(self,A,B,C,D):
		return B

	
	#first prefiltering step
	#predicts value of next pixel and stores the difference in output image							
	def createpyramid2(self,image):
		
		w=self.w
		h=self.h
		m=4
		func=[self.paeth2c,self.paeth2b,self.paeth3c,self.paeth3d]
		#func=[self.paeth2c,self.paeth2b,self.paeth3c,self.paeth3d]
		image2=np.zeros((h,w,3),np.int16)
		#print(image[:,0])
		image2[0,0,:]=image[0,0,:]
		for i in range(1,w):
			image2[0,i,:]=image[0,i,:].astype(np.int16)-image[0,i-1,:]
			
		for j in range(1,h):
			image2[j,0,:]=image[j,0,:].astype(np.int16)-image[j-1,0,:]	
		choicej=[0]*4
		for j in range(1,h):	
			errsum=[0]*m
			
			for i in range(1,w-1):
				err=[99999]*4
				for k in range(m):
			
					D=func[k](image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:],image[j-1,i+1,:])
					#print(image[j,i,:])
					#print(D)
					image2[j,i,:]=image[j,i,:].astype(np.int16)-D
					#print(self.t1a(image2[j,i,:]))
					#print(self.transposebits2(self.t1a(image2[j,i,:].astype(np.uint8)),8))
					err[k]=np.sum(self.transposebits2(self.t1a(image2[j,i,:].astype(np.uint8)),8)==0)
					errsum[k]=errsum[k]+err[k]
				#print(err)
				ch=np.argmax(err)
				#print(ch)
			#print(errsum)
			choice=np.argmax(errsum).item()
			#print(choice)
			choicej[choice]=choicej[choice]+1
			#21441
			#21023
			#87726
			#choice=0#np.argmin(errsum)
			self.bitstream.write(choice,2)#
			for i in range(1,w-1):
				D=func[choice](image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:],image[j-1,i+1,:])
				image2[j,i,:]=image[j,i,:].astype(np.int16)-D
			i=w-1	
			D=self.paeth(image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:])
			image2[j,i,:]=image[j,i,:].astype(np.int16)-D
				#print([j,i,image[j,i,:],D,image2[j,i,:]])

				
					
		print(choicej)
		#print(image2[:,0])
		
		return image2
		


	#first prefiltering step
	#predicts value of next pixel and adds the value of the difference
	def decompress2(self,image,choice):
		w=self.w
		h=self.h
		func=[self.paeth2c,self.paeth2b,self.paeth3c,self.paeth3d]
		#func=[self.paeth3,self.paeth2b,self.paeth2c,self.paeth2d]
		for i in range(1,w):
			image[0,i,:]=image[0,i,:]+image[0,i-1,:]
		for j in range(1,h):
			image[j,0,:]=image[j,0,:]+image[j-1,0,:]
			
		for j in range(1,h):
			choicej=choice[j]
			for i in range(1,w-1):
				D=func[choicej](image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:],image[j-1,i+1,:])
				image[j,i,:]=image[j,i,:]+D
			i=w-1	
			D=self.paeth(image[j,i-1,:], image[j-1,i,:],image[j-1,i-1,:])
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


	#nbit= number of bits each symbol is stored as.
	#nbit 2 =  number of bits each symbol is stored as in output array2
	#ruins data in origional "array"
	def	transposebits2(self,array,nbit): #ruins data in origional "array"
	
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

				
						
	def t1a(self,v2d): #turn small negative numbers(large numbers) into small positive numbers while keeping small positive numbers small
		c=(v2d>=128)
		c1=255-v2d
		c1=c1*2+1
		c2=v2d*2
		v2d=(c*c1)+(1-c)*c2
		return v2d		
		
	def t1b(self,v2d): #reverse of t1a
		c=v2d%2
		c1=(v2d-1)//2
		c1=255-c1
		c2=v2d//2
		v2d=(c*c1)+(1-c)*c2
		return v2d
		
	def transpose(self,image): #turn 3 8 bit numbers into 8 3 bit numbers
		#print("transpose")
		w=self.w
		h=self.h

		image1=self.t1a(image)
		im=Image.fromarray(image1.astype(np.uint8))
		im.save("/home/andrew/Desktop/asadf/out/asdfa3"+".png")
		image1=image1.reshape((w*h,3))
		image2=self.transposebits2(image1,8)	

		return image2
						
	def detranspose(self,image):  #turn 8 3 bit numbers into 3 8 bit numbers
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
		n=4 # split 8 significant bits into n groups
		
	
		bits2=6
		size1=(1<<bits2)
		arrays=[None]*n
		lengths=[None]*n
		arrays[0]=array[0:w*h*3]
		arrays[1]=array[w*h*3:w*h*5]
		arrays[2]=array[w*h*5:w*h*7]
		arrays[3]=array[w*h*7:w*h*8]
		
		lengths[0]=w*h*3
		lengths[1]=w*h*2
		lengths[2]=w*h*2
		lengths[3]=w*h*1
		for i in range(n):
		#	arrays[i]=array[w*h*(i)*8//n:w*h*(i+1)*8//n]
		#	lengths[i]=w*h*8//n
			arrays[i],lengths[i]=self.t3_9( arrays[i],lengths[i],3,bits2)

		huf=[None]*n

		for i in range(n):#n
			#print(arrays[i].tolist())
			huf[i]=deflate(bits2)
			huf[i].encode(self.bitstream,arrays[i],lengths[i])
			#print(lengths[i])
				
	

		
	def dehuffman(self):
		#print("huffman2")

		n=4
		dtype=np.uint8
		bits1=6
		w=self.w
		h=self.h
		huf=[None]*n
		arrays=[None]*n
		lengths=[None]*n
	
		lengths[0]=w*h*3
		lengths[1]=w*h*2
		lengths[2]=w*h*2
		lengths[3]=w*h*1
		for i in range(n):#n
			huf[i]=deflate(bits1)
		#	lengths[i]=w*h*8//n
			arrays[i],_=huf[i].decode(self.bitstream)#length[i]
			arrays[i]=self.t9_3( arrays[i] , lengths[i],bits1,3)
			
		array=np.concatenate(arrays,axis=0)
		length=w*h
		#print(array.shape)
		return array,length


	
	
								
								
def main():
	#print("Asf")
	
	image_to_compress = "/home/andrew/Desktop/asadf/text256.png"
	
	im = Image.open(image_to_compress)
	im =im.convert("RGB")
	image1=np.asarray(im).astype(np.uint8)
	
	a=compress(image1,"/home/andrew/Desktop/asadf/out/asdf.awy") #to compress

	b=compress(None,"/home/andrew/Desktop/asadf/out/asdf.awy") # to decompress
	
	image,lengths=a.compress()
	image2=b.decompress(image,None)
	
	
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
