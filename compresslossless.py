
import numpy as np
from bitstream import bitstream
from sparsehuffman import sparsehuffman 

import losslessfunctions as lf

test1=None
test2=None
class compresslossless():
	def __init__(self,image,filename):
		self.image=image
		self.filename=filename
		self.compres=False

		self.i2threshold=True # true means compress i2==1
		
		self.size1=[[512,64,64],[64,8,8]]
		#self.size2=[[8,8,8],[2,1,1]]
		self.size2=[[9,9,9],[3,3,3]]
		#self.bits=[[9,6,6],[3,3,3]]
		self.bits=[[8,8,8],[2,1,1]]
		self.drthreshold=31
		
		
	def compress(self):
		image=self.image
		self.bitstream=bitstream(self.filename,'wb')

		w=image.shape[1]
		h=image.shape[0]

	
		self.w=w
		self.h=h
		
		n=max(w,h).bit_length()-1
		self.n=n

		self.bitstream.write(w,32)
		self.bitstream.write(h,32)


		avg=np.mean(image,axis=(0,1))
		self.midcolor=lf.getmidcolor(avg)
		a=[0,1,2]
		del a[self.midcolor]
		
		midc=image[:,:,self.midcolor]
		image[:,:,1:3]=image[:,:,a]
		image[:,:,0]=midc

		
		self.bitstream.write(self.midcolor,2)

		image=self.encodedif(image)
		self.huffman(image)
		


		self.bitstream.close()
		return image

	
	def decompress(self,image):

		self.bitstream=bitstream(self.filename,'rb')
		w=self.bitstream.read(32)
		h=self.bitstream.read(32)
		self.file=self.bitstream
		self.w=w
		self.h=h

		self.midcolor2=self.bitstream.read(2)
		self.midcolor=0


		huf=sparsehuffman(2)
		choice,_=huf.decode(self.bitstream)
	
		
		image=self.dehuffman()
		image=self.decodedif(image,choice)
			
		self.midcolor=self.midcolor2
		a=[0,1,2]
		del a[self.midcolor]	
		midc=image[:,:,0]
		image[:,:,a]=image[:,:,1:3]
		image[:,:,self.midcolor]=midc
			
		self.file.close()
		
		return image
	



	
	#first prefiltering step
	#predicts value of next pixel and stores the difference in output image							
	def encodedif(self,image):
		
		w=self.w
		h=self.h
		m=3
		func=[lf.paeth1,lf.paeth1left,lf.paeth1up]
		func2=[lf.paeth2,lf.paeth2left,lf.paeth2up]
		dif=np.zeros((h,w,3),np.uint8)

		#top left pixel
		dif[0,0,:]=image[0,0,:]
		
		#top pixels
		p=image[0,:-1,:]
		dif[0,1:,:]=lf.encodepixeldif(p,image[0,1:,:])

		#left pixels		
		p=image[:-1,0,:]	
		dif[1:,0,:]=lf.encodepixeldif(p,image[1:,0,:])
	
			
		choicej=[0]*3
		choice3=np.zeros(h-1,np.uint8)
		errsum2=0

		for j in range(1,h):	
			errsum=[0]*m
			pj=np.zeros((m,w,3))
			
			for i in range(1,w):
				err=[99999]*m
				A=image[j,i-1,:]
				B=image[j-1,i,:]
				C=image[j-1,i-1,:]
				for k in range(m):
					if i==w-1:
						pj[k,i]=func2[k](A, B,C)
					else:
						D=image[j-1,i+1,:]
						pj[k,i,:]=func[k](A, B,C,D)
			
			for k in range(m):
				dif[j,1:,:]=lf.t1a(lf.encodepixeldif(pj[k,1:],image[j,1:,:]))
				errsum[k]=np.sum(lf.transposebits2(dif[j,:,:].astype(np.uint8),8)==0)

			
			choice=np.argmax(errsum).item()
			
			
			#choicej[choice]=choicej[choice]+1
			
			choice3[j-1]=choice
			
			A=image[j,0:-2,:]
			B=image[j-1,1:-1,:]
			C=image[j-1,0:-2,:]
			D=image[j-1,2:,:]
			p=func[choice](A, B,C,D)
			dif[j,1:-1,:]=lf.encodepixeldif(p,image[j,1:-1,:])

			#right pixels
			i=w-1	
			A=image[j,i-1,:]
			B=image[j-1,i,:]
			C=image[j-1,i-1,:]
			p=func2[choice](A, B,C)
			dif[j,i,:]=lf.encodepixeldif(p,image[j,i,:])

		#print(choicej)

		huf=sparsehuffman(2)
		huf.encode(self.bitstream,choice3)
		dif=lf.t1a(dif.reshape((-1,3))[:,:])
			
		#im=Image.fromarray(dif)
		#im.save("/home/andrew/Desktop/asadf/out/d1234.png")
		
		return dif

				
	def decodedif(self,dif,choice):
		w=self.w
		h=self.h

	
		func=[lf.paeth1,lf.paeth1left,lf.paeth1up]
		func2=[lf.paeth2,lf.paeth2left,lf.paeth2up]
		image=np.zeros((h,w,3),dtype=np.uint8)
		
		
		dif=lf.t1b(dif.reshape((h,w,3)))
		

		image[0,0,:]=dif[0,0,:]
		
	
		for i in range(1,w):
			p=image[0,i-1,:]
			image[0,i,:]=lf.decodepixeldif(p,dif[0,i,:])

		for j in range(1,h):
			p=image[j-1,0,:]
			image[j,0,:]=lf.decodepixeldif(p,dif[j,0,:])

		
		for j in range(1,h):
			choicej=choice[j-1]
			for i in range(1,w-1):
				A=image[j,i-1,:]
				B=image[j-1,i,:]
				C=image[j-1,i-1,:]
				D=image[j-1,i+1,:]
				p=func[choicej](A, B,C,D)
				image[j,i,:]=lf.decodepixeldif(p,dif[j,i,:])
				
			i=w-1
			A=image[j,i-1,:]
			B=image[j-1,i,:]
			C=image[j-1,i-1,:]
			p=func2[choicej](A, B,C)

			image[j,i,:]=lf.decodepixeldif(p,dif[j,i,:])
		

		return image


	

	
	def huffman(self,array):

		w=self.w
		h=self.h

		n=4 # split 8 significant bits into n groups


		arrays2=[None]*n



		array=np.unpackbits(array[...,np.newaxis],axis=-1)

		size1=8//n#number of significant bits per group
		size2=n//2 # groups are grouped into size2 groups of 2
		f=np.zeros((2,8//size1))
		for k in range(8):
			section0=array[:,1:3,k*size1:(k+1)*size1]
			section1=array[:,self.midcolor,k*size1:(k+1)*size1]
			if section0.size!=0:
				f[0,k]=np.sum(section0==0)/section0.size
			if section1.size!=0:
				f[1,k]=np.sum(section1==0)/section1.size
		
		
		f=f.reshape((2,size2,2)).transpose((1,0,2))
		s1=np.sum(f,axis=(1))
		s2=np.sum(f,axis=(2))
		
		mode=[0]*(size2)
		d1=[0]*(size2)
		d2=[0]*(size2)
		bits=[0]*(size2)

		for i in range(size2):
			d1[i]=np.abs(s1[i,1]-s1[i,0])
			d2[i]=np.abs(s2[i,1]-s2[i,0])
			if d1[i]>d2[i]:
				mode[i]=0
			else:
				mode[i]=1
				
		for i in range(size2):
			if mode[i]==0:
				arrays2[0+2*i]=array[:,:,2*i*size1:(2*i+1)*size1].reshape((-1))
				arrays2[1+2*i]=array[:,:,(2*i+1)*size1:(2*i+2)*size1].reshape((-1))
				bits[i]=6
				
			else:
				arrays2[0+2*i]=array[:,1:3,2*i*size1:2*(i+1)*size1].reshape((-1))
				arrays2[1+2*i]=array[:,self.midcolor,2*i*size1:2*(i+1)*size1].reshape((-1))
				bits[i]=8
			self.bitstream.write(bits=mode[i],n=1)
	

			
		huf=[None]*n
		for i in range(n):
			arrays2[i],length3=lf.t3_9(arrays2[i],1,bits[i//2])
			huf[i]=sparsehuffman(bits[i//2])
		

				
		
		
		for i in range(n):#n

			if arrays2[i] is not None:
				huf[i].encode(self.bitstream,arrays2[i],arrays2[i].shape[0])#lengths[i])



		
	def dehuffman(self): 

		n=4

		w=self.w
		h=self.h
		huf=[None]*n
		arrays=[None]*n
		huf=[None]*n


		size1=8//n
		size2=n//2
		size3=w*h
		mode=[0]*(size2)

		bits=[0]*(size2)
		for i in range(size2):
			mode[i]=self.bitstream.read(1)
			if mode[i]==0:
				bits[i]=6
			else:
				bits[i]=8
				
		huf=[None]*n
		for i in range(n):
			huf[i]=sparsehuffman(bits[i//2])
			
		for i in range(n):#n
			arrays[i],_=huf[i].decode(self.bitstream)#length[i]
			
		array=np.zeros((size3,3,8),np.uint8)			
		for i in range(size2):
			if mode[i]==0:

				arrays[0+2*i]=lf.t9_3(arrays[0+2*i],size3*bits[i]*size1//2,bits[i],1) 
				arrays[1+2*i]=lf.t9_3(arrays[1+2*i],size3*bits[i]*size1//2,bits[i],1) 
				arrays[0+2*i]=arrays[0+2*i].reshape((-1,3,size1))
				arrays[1+2*i]=arrays[1+2*i].reshape((-1,3,size1))
				array[:,:,2*i*size1:(2*i+1)*size1]=arrays[0+2*i]
				array[:,:,(2*i+1)*size1:(2*i+2)*size1]=arrays[1+2*i]

			else:

				arrays[0+2*i]=lf.t9_3(arrays[0+2*i],size3*bits[i]*size1//2,bits[i],1) 
				arrays[1+2*i]=lf.t9_3(arrays[1+2*i],size3*bits[i]*size1//4,bits[i],1) 

				
				arrays[0+2*i]=arrays[0+2*i].reshape((-1,2,2*size1))
				arrays[1+2*i]=arrays[1+2*i].reshape((-1,2*size1))
				array[:,1:3,2*i*size1:2*(i+1)*size1]=arrays[0+2*i]
				array[:,self.midcolor,2*i*size1:2*(i+1)*size1]=arrays[1+2*i]

		
		array=np.packbits(array,axis=-1)[...,0]
		
		return array


	

