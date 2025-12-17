import numpy as np
from huffman import huffman

class deflate2 ():
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
		#print(total)
		#print(sum(self.lengths[0].values()))
		#print(sum(self.freq))
		#print(len(self.lengths[0]))
		#print(self.freq)
		sorted_dict = dict(sorted(self.lengths[0].items()))
		#print(sorted_dict)
		return
		 

		
	def getfreq(self):
		keys=list(self.lengths[0].keys())
		keys.sort()#sorted by length

		maxzerolength=keys[len(keys)-1]
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
		#print("removehufzeros")
		#print([node.value,threshold1,threshold2,node.maxlength,node.parent])

			
		
		if node.left is not None:
			#print(["left",node.left.parent])
			self.removehufzeros(node.left,threshold1,threshold2)
			
		if node.right is not None:
			self.removehufzeros(node.right,threshold1,threshold2)
			
		if node.value is not None and node.value >= threshold1 and node.value < threshold2:
			#print(["removed",node.value,threshold1,threshold2,node.maxlength,node.parent.value,node.parent.left])
			node.remove()
			#self.nonzeroroot.print()
			return True
		else:
			return False
			
	def createhuff2(self):
		
		nonzeroroot=self.huff.root.clone()
		self.nonzeroroot=nonzeroroot
		#self.nonzeroroot.print()
		self.removehufzeros(nonzeroroot,threshold1=(1<<self.nbit),threshold2=9999999999999999)
		#nonzeroroot.print()
		self.huff2=huffman(self.nbit)
		self.huff2.fromtree(nonzeroroot)
		return self.huff2
				
	def encode(self,bitstream,array,n):
		#print("encode")
		self.array=array
		self.n=n
		bitstream.write(n,32)
		#print(n)
		if n==0:
			return
			

		self.size=(1<<self.nbit)
		self.freq=np.zeros((self.size))
		self.lengths=[{}]*1#self.size
		self.firstpass()

		self.getfreq()
		nbit=(len(self.freq)).bit_length()
		
		self.huff=huffman(nbit,self.freq)
		#print(self.huff.codelength)
		#self.huff.root.print()
		self.huff2=self.createhuff2()
		#print(self.huff2.codelength)
		#print("huff2")
		#self.huff2.root.print()
		
		bitstream.write(self.maxzero,32)
		#print(self.maxzero)
		a=bitstream.n
		self.huff.writetree(bitstream)

		
		self.secondpass(bitstream)
		b=bitstream.n
		#print("encode size: "+str(b-a))
		
	def secondpass(self,bitstream):

		input=self.array
		inputlength=self.n
			

		a=(1<<self.nbit)
		i=0
		iszero=False
		while i < inputlength:
			symbol=input[i].item()
			#print([symbol,i,iszero,inputlength])
			if iszero ==False:
				if input[i]==0:
					length=1
					iszero=True
					length=1
					while length < self.n-i:
						if input[i+length]!=0:
							#print(input[i+length])
							break
						length=length+1
					#print([symbol,i,length])
					#print([a+length-1,a,i,i+length])
					self.huff.write(bitstream,a+length-1)
					i=i+length
				else:
					#print([symbol,i])
					self.huff.write(bitstream,symbol)
					i=i+1
			else:
				#print([symbol,i])	
				self.huff2.write(bitstream,symbol)
				i=i+1
				iszero=False
		return
	
		
	def decode(self,bitstream):
		#print("decode")
		outlength=bitstream.read(32)
		#print(outlength)
		if outlength==0:
			return np.zeros((0)),outlength
		self.maxzero=bitstream.read(32)
	
		a=((1<<self.nbit)+self.maxzero-1).bit_length()
		#print([a,self.maxzero,1,"a"])
		self.huff=huffman(a)
		
	#	print(outlength)
		#print(self.maxzero)
		
		self.huff.frombitstream(bitstream)
		#self.huff.root.print()
		#self.nbit=self.huff.nbits
		self.huff2=self.createhuff2()
		#self.huff.tostring()
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
		
