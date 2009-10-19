#!/usr/bin/env python
# PyMos
# Diwali Night Hack - Mosaic Generator using Python
# Abhishek Mishra <ideamonk at gmail.com>

import Image, ImageFilter
import os, sys, math, random
import logging

def build_mosaic(input_path, output_path, collection_path, zoom=20, thumb_size=60):

	log = logging.getLogger("PyMos")

	# Build Color Index
	log.info( "Building index...")
	
	files = os.listdir(collection_path)
	total_files = len(files)
	file_count = 0
	colormap = []
	
	for eachfile in files:
		im = Image.open (os.path.join(collection_path, eachfile))

		# lets blur a little to bring major color's prominance	
		im = im.filter(ImageFilter.BLUR)
		im = im.filter(ImageFilter.BLUR)
		im = im.filter(ImageFilter.BLUR)
	
		r = g = b = 0
		imdata = list(im.getdata())
		imdata_size = len(imdata)
		
		for i in imdata:
			r += i[0]
			g += i[1]
			b += i[2]

		# average the color of this thumbnail
		r /= imdata_size
		g /= imdata_size
		b /= imdata_size
		
		# append to colormap
		colormap.append(((r,g,b), eachfile))	
		
		file_count+=1
		log.debug("%.1f %% done" % ( (float(file_count) / total_files) * 100 ))

	log.info("Color Index built")
	
	# prepare images
	sourceImage = Image.open (input_path)
	sourceData = list(sourceImage.getdata())
	source_width, source_height = sourceImage.size
	output_width = source_width*zoom
	output_height = source_height*zoom
	
	output = Image.new(sourceImage.mode,
			   (output_width,output_height),
			   (255,255,255)
			   )

	log.info("Generating Mosaic...")
	# square mosaics as for now
	for x in range(0, output_width, thumb_size):
		for y in range(0, output_height, thumb_size):
			source_color = sourceData[ (y*source_width + x) / zoom ]
			
			# euclidean distance, color, source
			match = (555, (555,555,555), "")# initially something out of range
		
			for thumbs in colormap:
				thumb_color, thumb_file = thumbs
				# new matching method
				# calculate the euclidian distance between the two colors by taking the 
				# square root of the quantity 
				#		[(r2-r1)*(r2-r1) + (g2-g1)*(g2-g1) + (b2-b1)*(b2-b1)]'
				#
				# :( However, comparisons based on a metric like euclidian distance 
				# assumes that the rgb colorspace is orthogonal, homogenous, and linear 
				# in all three dimensions. These assumptions are subject to the 
				# composition of one's photoreceptors and to the method of translating 
				# these values into electromagnetic radiation.
				#
				# :'(  There are notions of contrast and neutrality that a simple 
				# euclidean metric doesn't capture.
				r1,g1,b1 = source_color
				r2,g2,b2 = thumb_color
				r3,g3,b3 = match[1]
				
				ecd_match = match[0]
				ecd_found = math.sqrt ( (r2-r1)**2 + (g2-g1)**2 + (b2-b1)**2)
				
				if (ecd_found < ecd_match):
						match = (ecd_found,thumb_color,thumb_file)
				
			try:
				small_image = Image.open(collection_path + match[2])
				small_image = small_image.resize ((thumb_size,thumb_size),Image.BICUBIC)
				output.paste (small_image,(x,y))	
			except:
				''' maybe nothing got matched! '''
				
		log.debug("%.1f %% done" % ((float(x) / output_width)*100))

	log.info("Mosaic Generated")		
	output.save(output_path, "PNG")
	log.info("Output File Written")


if __name__ == '__main__':
	logging.basicConfig() #YUCK, WHO wrote standard library's logging module? Some Java guy? GEEZ!
	log = logging.getLogger("PyMos")
	log.setLevel(logging.INFO)
	build_mosaic('input.jpg', 'output.png', 'collection/')
