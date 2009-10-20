#!/usr/bin/env python
# Pandamonkium Productions present
#                ____        __  ___          
#               / __ \__  __/  |/  /___  _____
#              / /_/ / / / / /|_/ / __ \/ ___/
#             / ____/ /_/ / /  / / /_/ (__  ) 
#            /_/    \__, /_/  /_/\____/____/  
#                  /____/ 1.0
#      
#                                                      -- ideamonk and yuvipanda
#                                                                 #hackers-india

# Mosaic Generator using Python ( Diwali Night Hack )

import Image, ImageFilter
import os, sys, math, random
import logging
import glob

try:
	import cPickle as pickle
except ImportError:
	import pickle
	
def build_colormap(files):
	colormap = []
	file_count = 0
	total_files = len(files)
	log = logging.getLogger("PyMos")
	for eachfile in files:
		im = Image.open(eachfile)
		
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
		colormap.append( ( (r,g,b), eachfile, None ))
		# ^^ new format for colormap, None replaced with resized images
		# when processing to optimize
		
		file_count+=1
		log.debug("%.1f %% done" % ( (float(file_count) / total_files) * 100 ))
	return colormap


def build_mosaic(input_path, output_path, collection_path, zoom=20, thumb_size=60, new_colormap=False):
	log = logging.getLogger("PyMos")

	# Build Color Index
	log.info( "Building index...")
	
	files = glob.glob(os.path.join(collection_path, '*.jpg'))
	total_files = len(files)
	file_count = 0
	colormap_file = os.path.join(collection_path, '.colormap')
	if os.path.exists(colormap_file) and not new_colormap:
		colormap = pickle.load(open(colormap_file))
	else:
		colormap = build_colormap(files)
		pickle.dump(colormap, open(colormap_file, 'w'))
	
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
	for x in xrange(0, output_width, thumb_size):
		for y in xrange(0, output_height, thumb_size):
			source_color = sourceData[ (y*source_width + x) / zoom ]
			
			# euclidean distance, color, index in colormap
			match = (555, (555,555,555), 0)# initially something out of range
		
			for index,thumbs in zip (xrange(len(colormap)), colormap):
				thumb_color, thumb_file = thumbs[0], thumbs[1]
				# calculate the euclidian distance between the two colors
				r1,g1,b1 = source_color
				r2,g2,b2 = thumb_color
				r3,g3,b3 = match[1]
			
				ecd_match = match[0]
				ecd_found = math.sqrt ( (r2-r1)**2 + (g2-g1)**2 + (b2-b1)**2)
				
				if (ecd_found < ecd_match):
						match = (ecd_found,thumb_color,index)
				
			try:
				if (colormap[match[2]][2] == None):   # has not been resized yet
					colormap[match[2]] = (colormap[match[2]][0], colormap[match[2]][1],Image.open(colormap[match[2]][1]))
					colormap[match[2]] = (colormap[match[2]][0], colormap[match[2]][1],colormap[match[2]][2].resize ((thumb_size,thumb_size),Image.BICUBIC) )
					
				output.paste (colormap[match[2]][2],(x,y))	
			except:
				''' maybe nothing got matched! '''
				
		log.debug("%.1f %% done" % ((float(x) / output_width)*100))

	log.info("Mosaic Generated")		
	output.save(output_path, "PNG")
	log.info("Output File Written")
