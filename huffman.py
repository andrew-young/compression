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
		#print(self.value)
		#print(self.parent.parent)
		#print(self.parent.left.value)
		#print(self.value)
		#print(self)
		#print(self.parent.left)
		if self.parent.parent is not None:
			if self.parent.left is self:
				if self.parent.parent.left==self.parent:
					self.parent.parent.left=self.parent.right
					#print("a")
				else:
					#print("b")
					self.parent.parent.right=self.parent.right
				self.parent.right.parent=self.parent.parent	
			else: #self.parent.right==self:
				if self.parent.parent.left==self.parent:
					#print("c")
					self.parent.parent.left=self.parent.left
				else:
					#print("d")
					self.parent.parent.right=self.parent.left
				self.parent.left.parent=self.parent.parent	
				#self.parent.parent=self.parent.left
		
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
	def __init__(self,nbits=None,freq=None):
	
		
		#
		
		self.codetable={}
		self.codelength={}
		self.root=None
		self.n=0
		self.nbits=nbits
		#print(nbits)
		if nbits is None:
			return
		#self.size=1<<nbits
		
		if freq is None  or len(freq)==0:
			return
			#freq=self.generate()
		self.freq=freq
			


		

		if freq is not None:
			#print(type(freq))
			if isinstance(freq,np.ndarray):
				freq=freq.tolist()
			#print(type(freq))	
			if isinstance(freq,list):
				freq=dict(zip(list(range(len(freq))),freq))#convert list to dic
			#print(type(freq))	
			
			self.nbits=(max(freq.keys())).bit_length()
			#print(max(freq.keys()))
			#print(freq)
			self.fromfreq(freq)
			

	
	def fromfreq(self,freq):
		hlist=[]
		self.size=len(freq)

		#for i2 in range(10):# for ints larger than 64 bits
		#	self.codetable[i2]=np.zeros(self.size,dtype=np.uint64)
		#self.codelength=np.zeros(self.size,dtype=np.uint64)
		for length,fre in freq.items():
			if fre>0:
				#print([k2,freq[k2]])
				self.n=self.n+fre
				#total=total+self.freq[i][j,k,k2]
				#print([length,fre])
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
		print("from bits")
		self.readtree(bitstream)
	
	def fromtree(self,root):
		#print("from tree")
		self.root=root
		self.hufftree(root,0,0)
		
	def readtree(self,bitstream):
		self.root=huffnode()
		stack=[self.root]
		while len(stack)>0:
			node=stack[len(stack)-1]
			
			if node.left is not None and node.right is not None:
				del stack[len(stack)-1]
				
		
			else:
				bit=bitstream.read(1)
				#print(bit)
				if bit==0:
					#print([0,"rt"])
					rightnode=huffnode()
					stack.append(rightnode)
					leftnode=huffnode()
					stack.append(leftnode)
					node.left=leftnode
					node.right=rightnode
				elif bit==1:
					node.value=bitstream.read(self.nbits)
					#print([1,node.value,"rt",self.nbits])
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
		#print([value,v,i])
		return value,v,i
			
	
	def hufftree(self,node,code,n,codelist=[]): #build lookuptable from tree for writing
		#k=8 i =type j =n
		word=n//62

		if (n%62)==0 and n!= 0:

			codelist=codelist[:word]
			codelist.append(code)
			code=0
		
		if node.left is  None and node.right is  None:
			#for k2 in range(len(codelist)):
			#	self.codetable[k2][node.value]=codelist[k2]
			#print(word)
			#print(self.codetable)
			#print([node.value])
			#print(code)
			self.codetable[node.value]=code
			self.codelength[node.value]=n
			#print([node.value,code,n])
		else:

			self.hufftree(node.left,2*code,n+1,codelist)
			self.hufftree(node.right,2*code+1,n+1,codelist)
			
	def writetree(self,bitstream):
		print("write tree")
		a1=bitstream.n
		self.writetree1(bitstream,self.root)
		a2=bitstream.n
		print(a2-a1)
		
	def writetree1(self,bitstream,node,i=0):
	
		if node.left is  None and node.right is  None:
			bitstream.write(1,1)
			#print([1,node.value,"wt",self.nbits])
		
			bitstream.write(node.value,self.nbits)
		else:
			
			bitstream.write(0,1)
			#print(0)
			self.writetree1(bitstream,node.left,i+1)
			self.writetree1(bitstream,node.right,i+1)
		
	def write(self,bitstream,symbol):
		v=symbol
		#print(v)
		le=self.codelength[v]
		#print(le)
		for word in range((le-1)//62+1):
			if word<(le)//62:
				
				code=self.codetable[v]
				
				bitstream.write(code,62)
			else:
				
				code=self.codetable[v]
				#print([v,code,"y",le])
				bitstream.write(code,le%62)
						
	def writeall(self,bitstream,array,n):
		print(["writeall",n,self.nbits])
		bitstream.write(n,32)
		if self.nbits>256:
			raise "nbits > 256"
		bitstream.write(self.nbits,8)
		#print([n,self.nbits])
		if n>0:
			self.writetree(bitstream)
			for i in range(n):
				v=array[i]
				self.write(bitstream,v)

	def readall(self,bitstream,dtype):
		
		n=bitstream.read(32)
		self.nbits=bitstream.read(8)
		#print([n,self.nbits])
		array=np.zeros((n),dtype)
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
					
