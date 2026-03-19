from compresslossless import compresslossless
from PIL import Image
import numpy as np
						
def main():

	
	image_to_compress = "/home/andrew/Desktop/asadf/256.png"#crown128 web.jpg
	#72288
	#77213
	im = Image.open(image_to_compress)
	im =im.convert("RGB")
	im.save("/home/andrew/Desktop/asadf/out/og.png")
	image1=np.asarray(im).astype(np.uint8)
	im=Image.fromarray(image1)
	im.save("/home/andrew/Desktop/asadf/out/og2.png")
	a=compresslossless(image1,"/home/andrew/Desktop/asadf/out/asdf.awy") #to compress

	b=compresslossless(None,"/home/andrew/Desktop/asadf/out/asdf.awy") # to decompress
	
	image=a.compress()
	image2=b.decompress(None)
	

	im=Image.fromarray(image2)
	im.save("/home/andrew/Desktop/asadf/out/asdf.png")
	im.save("/home/andrew/Desktop/asadf/out/asdf.jpg")
	
	test1=image1
	test2=image2
	a=(test1==test2).all()
	solut = (~np.equal(test1, test2)).astype(int)
	indices = np.flatnonzero(solut)

	print("success: "+str(a))

if __name__ == '__main__':
	main()
