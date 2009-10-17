#!/usr/bin/env python
# author -- ideamonk at gmail.com
# diwali night hack

import Image
import os,sys
import random
import ImageFilter

files = os.listdir('./kids')
colormap = []
mag = 5

for aFile in files:
	
	im = Image.open ('./kids/' + aFile)
	im = im.filter(ImageFilter.BLUR)
	im = im.filter(ImageFilter.BLUR)
	#im = im.filter(ImageFilter.BLUR)
	#im = im.filter(ImageFilter.BLUR)
	#im = im.filter(ImageFilter.BLUR)
	
	r = 0
	g = 0
	b = 0
	imdata = list(im.getdata())
	for i in imdata:
		r += i[0]
		g += i[1]
		b += i[2]

	r /= len(imdata)
	g /= len(imdata)
	b /= len(imdata)

	colormap.append(((r,g,b), aFile))	

# got colormap generated
mainImage = Image.open ('./images/foo.jpg')
mainData = list(mainImage.getdata())
output = Image.new (mainImage.mode,(mainImage.size[0]*mag,mainImage.size[1]*mag),(255,255,255))

for x in range(0,mainImage.size[0],10):
	for y in range(0,mainImage.size[1],10):
		color = mainData[y*mainImage.size[0]+x]
		# match color
		match = ( (555,555,555), "")
		
		for images in colormap:
			dc = images[0]
			if ( abs( dc[0] - color[0] ) < abs(match[0][0] - color[0]) and
					abs( dc[1] - color[1] ) < abs(match[0][1] - color[1]) and
					abs( dc[2] - color[2] ) < abs(match [0][2] - color[2])
					):
						#if (random.randint(1,10)!=3):
						match = (dc,images[1])
		#print dc,color
		try:
			pim = Image.open('./kids/' + match[1])
			pim = pim.resize ((50,50),Image.BICUBIC)
			output.paste (pim,(x*5,y*5))	
		except:
			''' '''
	print (float(x) / mainImage.size[0])*100, "% done"
	#output.show()
	#raw_input()
	#output.save ("/tmp/state.png","PNG")
output.show()
output.save("/home/ideamonk/mosaic/output.png", "PNG")

