import numpy as np
import math

class huffnode():
	def __init__(self,freq=0,value=None,repeat=None,minlength=0,maxlength=0,left=None,right=None):
		if value is None:
			self.minlength=minlength
			self.maxlength=maxlength
		else:
			self.minlength=1
			self.maxlength=1
		
		self.freq=freq
		self.value=value
		self.left=left
		self.right=right
		self.parent=None
		self.repeat=None
		
	def join(self,left,right):
		self.left=left
		self.right=right
		self.freq=left.freq+right.freq
		self.maxlength=max(left.maxlength,right.maxlength)+1
		left.parent=self
		right.parent=self
		
	def read(self,bit):
		if bit ==0:
			return self.left
		else:
			return self.right
	
	def remove(self):

		if self.parent.parent is not None:
			if self.parent.left is self:
				if self.parent.parent.left==self.parent:
					self.parent.parent.left=self.parent.right
				else:
					self.parent.parent.right=self.parent.right
				self.parent.right.parent=self.parent.parent	
			else: #self.parent.right==self:
				if self.parent.parent.left==self.parent:
					self.parent.parent.left=self.parent.left
				else:
					self.parent.parent.right=self.parent.left
				self.parent.left.parent=self.parent.parent	
		
		if False:
			if self.parent.left==self:
				leftnode=self.parent.right.left
				rightnode=self.parent.right.right
			else: #self.parent.right==self:
				leftnode=self.parent.left.left
				rightnode=self.parent.left.right
			self.parent.left=leftnode
			self.parent.right=rightnode
			
	def clone(self):
		cloneroot=huffnode()
		self.clonerecurse(cloneroot)
		return cloneroot
		
	def clonerecurse(self,clonenode):
		
		if self.left is not None:
			clonenodeleft=huffnode(value=self.left.value,maxlength=self.maxlength)
			clonenode.left=clonenodeleft
			clonenode.left.parent=clonenode
			self.left.clonerecurse(clonenode.left)
		if self.right is not None:
			clonenoderight=huffnode(value=self.right.value,maxlength=self.maxlength)
			clonenode.right=clonenoderight
			clonenode.right.parent=clonenode
			self.right.clonerecurse(clonenode.right)
			

			
	def print(self):
		if self.value is not None:
			print(self.value)
		if self.left is not None:
			print("left")
			self.left.print()
		if self.right is not None:
			print("right")
			self.right.print()
			
class huffman():
	def __init__(self,freq=None):
	
		
		#
		
		self.codetable={}
		self.codelength={}
		self.root=None
		self.n=0
		self.nbits=None


		#self.size=1<<nbits
		
		if freq is None  or len(freq)==0:
			return

		self.freq=freq
			


		


		self.fromfreq(freq)
			

	
	def estimatesize(self):
		total=0
		for symbol,length in self.codelength:
			symbolfreq=self.freq[key]
			total=total+length*symbolfreq
		return total
		
	def getfreq(self):
		n=self.n

		input=self.array
		
		self.maxv=np.max(self.array)
		self.nbits=self.maxv.item().bit_length()
		self.freq=[0]*(self.maxv.astype(np.uint16)+1)
		i=0
		#print(self.maxv+1)
		while i < n:
			symbol=self.array[i]
			#print(symbol)
			self.freq[symbol]=self.freq[symbol]+1
			i=i+1


		
		#self.printstats()
		return
	def printstats(self):
		print(sum(self.freq))
		print(self.freq)
		
	def encode(self,bitstream,array,n=None):
		self.array=array
		if n is None:
			self.n=array.shape[0]
		else:
			self.n=n
		self.getfreq()
		self.fromfreq(self.freq)
		self.startstream=bitstream.n
		
		self.writeall(bitstream,array,self.n)
		self.endstream=bitstream.n
		self.printencodesize()
	
	def printencodesize(self):
		print("tree size"+str(self.endtree-self.starttree))
		print("encode size: "+str(self.endstream-self.startstream))
		
	def fromfreq(self,freq):
		if freq is not None:
			if isinstance(freq,np.ndarray):
				freq=freq.tolist()

			if isinstance(freq,list):
				freq=dict(zip(list(range(len(freq))),freq))#convert list to dic

			self.nbits=(max(freq.keys())).bit_length()

			
		hlist=[]
		self.size=len(freq)
		self.n=0
		for length,fre in freq.items():
			if fre>0:
				self.n=self.n+fre
				hlist.append(huffnode(value=length,freq=fre))

		if self.n==0:
			return
		le=len(hlist)
		for k2 in range(le-1):
			k3=le-k2-1
			hlist.sort(key=lambda x: x.maxlength+ 20*x.freq, reverse=True)
			node=huffnode()

			node.join(hlist[k3-1],hlist[k3])
			del hlist[k3]
			del hlist[k3-1]
			hlist.append(node)
		self.root=hlist[0]
			
		self.hufftree(self.root,0,0)
		
	def frombitstream(self,bitstream):
		self.readtree(bitstream)
	
	def fromtree(self,root):
		self.root=root
		self.hufftree(root,0,0)
		
	def readtree(self,bitstream):
		self.root=huffnode()
		stack=[self.root]
		self.nbits=bitstream.read(8)+1
		while len(stack)>0:
			node=stack[len(stack)-1]
			
			if node.left is not None and node.right is not None:
				del stack[len(stack)-1]
				
		
			else:
				bit=bitstream.read(1)
				if bit==0:
					rightnode=huffnode()
					stack.append(rightnode)
					leftnode=huffnode()
					stack.append(leftnode)
					node.left=leftnode
					node.right=rightnode
				elif bit==1:
					node.value=bitstream.read(self.nbits)
					del stack[len(stack)-1]
					

	def read(self,bitstream,node=None):#read symbol

		if node is None:
			node=self.root

		v=0
		i=0

		while node is not None and node.left is not None:
			i=i+1
			bit=bitstream.read(1)
			v=v*2+bit

			node=node.read(bit)
			
		value=node.value
		return value,v,i
			
	
	def hufftree(self,node,code,n,codelist=[]): #build lookuptable from tree for writing
		#k=8 i =type j =n
		word=n//62

		if (n%62)==0 and n!= 0:

			codelist=codelist[:word]
			codelist.append(code)
			code=0
		
		if node.left is  None and node.right is  None:
			self.codetable[node.value]=code
			self.codelength[node.value]=n
		else:

			self.hufftree(node.left,2*code,n+1,codelist)
			self.hufftree(node.right,2*code+1,n+1,codelist)
			
	def writetree(self,bitstream):
		self.starttree=bitstream.n
		bitstream.write(self.nbits-1,8)
		self.writetree1(bitstream,self.root)
		self.endtree=bitstream.n
		
		
	def writetree1(self,bitstream,node,i=0):
	
		if node.left is  None and node.right is  None:
			bitstream.write(1,1)

			bitstream.write(node.value,self.nbits)
		else:
			
			bitstream.write(0,1)
			self.writetree1(bitstream,node.left,i+1)
			self.writetree1(bitstream,node.right,i+1)
		
	def write(self,bitstream,symbol):
		v=symbol
		le=self.codelength[v]
		for word in range((le-1)//62+1):
			if word<(le)//62:
				
				code=self.codetable[v]
				
				bitstream.write(code,62)
			else:
				
				code=self.codetable[v]
				bitstream.write(code,le%62)
						
	def writeall(self,bitstream,array,n):
		bitstream.write(n,32)
		if self.nbits>256:
			raise "nbits > 256"
		bitstream.write(self.nbits,8)
		if n>0:
			self.writetree(bitstream)
			for i in range(n):
				v=array[i]
				self.write(bitstream,v)

	def decode(self,bitstream):
		 return self.readall(bitstream)
	
	def readall(self,bitstream):
		
		n=bitstream.read(32)
		self.nbits=bitstream.read(8)
		if self.nbits>32:
			self.dtype=np.uint64
		elif self.nbits>16:
			self.dtype=np.uint32
		elif self.nbits>8:
			self.dtype=np.uint16
		else:
			self.dtype=np.uint8
			

		array=np.zeros((n),self.dtype)
		if n>0:
			self.frombitstream(bitstream)
			for i in range(n):
				array[i],h,cl=self.read(bitstream)
		return array,n

	
	def tostring(self):
		print("huffman to string")
		print(self.nbits)
		if self.root is not None:
			self.tostringtree(self.root,0)
	
	
	def tostringtree(self,node,code,i=0):
		if node.left is  None and node.right is  None:
			print([node.value, code,i])
		else:
			self.tostringtree(node.left,2*code,i+1)
			self.tostringtree(node.right,2*code+1,i+1)
					
