import numpy as np
from huffman import huffman

class sparsehuffman ():
	def __init__(self,nbit):
		self.nbit=nbit




	def firstpass(self):
		n=self.n

		input=self.array

		i=0
		total=0
		while i < n:

			symbol=self.array[i]
			#print([i,symbol])
			if input[i]==0:
				length=1
				while length < self.n-i:
					if input[i+length]!=0:
						break
					length=length+1
				total=total+length
				#print([i,length,n])
				if length in self.lengths[0]:
					self.lengths[0][length]=self.lengths[0][length]+1
				else:
					self.lengths[0][length]=1

				i=i+length

			else:
				#print("A")
				self.freq[symbol]=self.freq[symbol]+1
				i=i+1
		#print(self.lengths[0])
		#self.maxv=max(self.freq)
		#self.maxz=len(self.lengths[0])
		#self.nbits=(self.maxv+self.maxz).item().bit_length()
		self.total=total
		#self.printstats()
		return

	def printstats(self):
		total=self.total
		print("total zeros",total)
		print(total/(total+sum(self.freq)))
		print(sum(self.lengths[0].values()))
		print(sum(self.freq))
		print(len(self.lengths[0]))
		
		sorted_dict = dict(sorted(self.lengths[0].items()))
		self.total=sum(self.freq)+sum(self.lengths[0].values())
		print(self.freq)
		print(sorted_dict)
		
	def getfreq(self):
		keys=list(self.lengths[0].keys())
		keys.sort()#sorted by length
		#print(len(keys))
		if len(keys)>0:
			maxzerolength=keys[len(keys)-1]
		else:
			maxzerolength=0
		symbollength=(1<<self.nbit)#number of regular symbols
		freq2=np.zeros((symbollength+maxzerolength))	
		for item in self.lengths[0].items():
			f=item[1]
			length=item[0]
			freq2[symbollength+length-1]=f
				
		freq2[1:symbollength]=self.freq[1:symbollength]
		self.freq=freq2
		self.maxzero=maxzerolength
	
	def removehufzeros(self,node,threshold1,threshold2):
	
		if node.left is not None:
			self.removehufzeros(node.left,threshold1,threshold2)
			
		if node.right is not None:
			self.removehufzeros(node.right,threshold1,threshold2)
			
		if node.value is not None and node.value >= threshold1 and node.value < threshold2:
			node.remove()
			return True
		else:
			return False
			
	def createhuff2(self): #create huffman encoding without zero repeats
		
		nonzeroroot=self.huff.root.clone()
		self.nonzeroroot=nonzeroroot

		self.removehufzeros(nonzeroroot,threshold1=(1<<self.nbit),threshold2=9999999999999999)

		self.huff2=huffman()
		self.huff2.fromtree(nonzeroroot)
		return self.huff2
				
	def encode(self,bitstream,array,n=None):
		#print("encode")
		
		
		
		#print(n)
		if array is None:
			return
			
			
		if n is None:
			n=array.shape[0]
		f=np.sum(array==0)/array.shape[0]
		print(f)
		if f<0.54:
			bitstream.write(1,1)
			self.huff=huffman()
			
			return self.huff.encode(bitstream,array)
			
		bitstream.write(0,1)
		
		self.n=n
		self.array=array
		bitstream.write(n,32)
		if n==0:
			return
		self.size=(1<<self.nbit)
		self.freq=np.zeros((self.size),np.uint64)
		self.lengths=[{}]*1#self.size
		self.firstpass()

		self.getfreq()
		nbit=(len(self.freq)).bit_length()
		
		self.huff=huffman(self.freq)
		self.huff2=self.createhuff2()

		bitstream.write(self.maxzero,32)

		self.startstream=bitstream.n
		self.huff.writetree(bitstream)

		
		self.secondpass(bitstream)
		self.endstream=bitstream.n
		self.printencodesize()
	
	def printencodesize(self):
		print("encode size: "+str(self.endstream-self.startstream))
		
	def secondpass(self,bitstream):

		input=self.array
		inputlength=self.n
			

		a=(1<<self.nbit)
		i=0
		iszero=False
		while i < inputlength:
			symbol=input[i].item()
			if iszero ==False:
				if input[i]==0:
					length=1
					iszero=True
					length=1
					while length < self.n-i:
						if input[i+length]!=0:
							break
						length=length+1
					self.huff.write(bitstream,a+length-1)
					i=i+length
				else:
					self.huff.write(bitstream,symbol)
					i=i+1
			else:
				self.huff2.write(bitstream,symbol)
				i=i+1
				iszero=False
		return
	
		
	def decode(self,bitstream):
		#print("decode")
		mode=bitstream.read(1)
		if mode:
			self.huff=huffman()
			return self.huff.decode(bitstream)
		outlength=bitstream.read(32)
		if outlength==0:
			return np.zeros((0)),outlength
		self.maxzero=bitstream.read(32)
		a=((1<<self.nbit)+self.maxzero-1).bit_length()
		self.huff=huffman()

		self.huff.frombitstream(bitstream)

		self.huff2=self.createhuff2()

		if self.nbit<=8: 
			outarray=np.zeros((outlength),np.uint8)
		else:
			outarray=np.zeros((outlength),np.uint16)
		a=(1<<self.nbit)
		i=0
		iszero=False
		while i<outlength:
			#print(i,a)
			if iszero ==False:
				symbol,code,cl=self.huff.read(bitstream)
				if symbol>=a:
					length=symbol-a+1
					outarray[i:i+length]=np.zeros((length))
					i=i+length
					iszero=True
					
				else:
					outarray[i]=symbol
					i=i+1
			
			else:
				symbol,code,cl=self.huff2.read(bitstream)
				outarray[i]=symbol
				i=i+1
				iszero=False
			
	
		return outarray,outlength
		
