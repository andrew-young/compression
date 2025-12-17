class bitstream():
	def __init__(self,file_path,mode='rb'):
		self.i=0
		self.byte=0
		self.mode=mode
		self.f=open(file_path, mode)
		self.n=0

	def write(self,bits,n=1):#n = number of bits
		#print([n, self.i, bits, self.byte])
		bits=bits
		#print("bits "+str(bits))
		#print("n "+str(n))
		if n==1:
			#print(self)
			#print(self.byte)
			
			self.byte=self.byte<<1 
			#print(self.byte)
			#print(type(self.byte))
			
			bit=bits&1
			#print(bit)
			#print(type(bit))
			self.byte=self.byte + bit 
			#print(self.byte)
			self.i=self.i+1
			#print("asdf")
			#print(bits)
			
			#print(self.byte)
			#print(self.i)
			if self.i==8:
				#print(self.byte)
				#print(type(self.byte))
				
				byte=self.byte.to_bytes(1,'big')
				#print(bits)
				#print(self.byte)
				#print(byte)
				self.f.write(byte)
				self.byte=0
				self.i=self.i-8
				self.n=self.n+1
		else:	
			bitmask=(1<<n)-1
			#print(bitmask)
			#print(bits)
			#print(bitmask&bits)
			b=(self.i+7)//8
			#print([self.i, n,b, self.byte])
			#print(self.byte.to_bytes(b,'big'))
			self.byte=self.byte<<n 
			#print(type(bitmask))
			#print(type(bits))
			bit=bitmask&bits
			
			
			self.byte=self.byte+ bit
			
			#print(self.i)
			self.i=self.i+n
			b=(self.i+7)//8
			#print(self.byte.to_bytes(b,'big'))
			#print(n)
			#print(self.i)
			#print(self.byte)
			if self.i>=8:
				byte=self.byte
				a=self.i%8
				b=self.i//8
				byte=byte>>a
				#print(a)
				#print(byte)
				#print(b)
				
				byte=byte.to_bytes(b,'big')#to be written
				#print(bits)
				#print(self.byte)
				#print(byte)
				self.f.write(byte)
				bitmask=(1<<a)-1
				self.byte=self.byte&bitmask
				#print(self.byte.to_bytes(1,'big'))
				self.i=a
				self.n=self.n+b
		#print("i "+str(self.i))
		#print("byte "+str(self.byte))
	
	def read(self,n): #read n bits
		#print([n, self.i, self.byte])
		while self.i < n:
			d=(n-self.i+7)//8
			d=min(d,8)#read atmost 8 bytes at a time
			byte=self.f.read(d)
			#print(byte)
			byte=int.from_bytes(byte,'big')
			
			#print(byte)
			self.byte=self.byte<<(8*d)
			#print(self.byte)
			self.byte=self.byte+ byte
			#print(self.byte)
			self.i=self.i+(8*d)
		
		#print(type(self.byte))	
		byte=self.byte>>(self.i-n)
		
		self.i=self.i-n
		self.n=self.n+n
		mask=(1<<self.i)-1
		#print(self.byte)
		self.byte=self.byte&mask
		#print(mask)
		#print(self.byte)
		#print(byte)
		#print(type(byte))
		return byte
		
	def close(self):
		#write unwritten bits. padded with zeros to make a full byte.
		#print("close")
		if self.mode=='wb' and self.i>0:
			byte=self.byte
			#print(self.i)
			#print(self.byte.to_bytes(1,'big'))
			byte=byte<<(8-self.i)
			byte=byte.to_bytes(1,'big')
			#print(byte)
			self.f.write(byte)
			self.n=self.n+1
		if self.mode=='rb':
			print("bytes written: "+str((self.n-1)//8+1))#bytes  read
		else:
			print("bytes read: "+str(self.n))#bytes written
		self.f.close()
		
	
	
