#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Pandamonkium Productions present
#                ____        __  ___
#               / __ \__  __/  |/  /___  _____
#              / /_/ / / / / /|_/ / __ \/ ___/
#             / ____/ /_/ / /  / / /_/ (__  )
#            /_/    \__, /_/  /_/\____/____/
#                  /____/
#
#                                                      -- ideamonk and yuvipanda
#                                                                 #hackers-india

''' PyMos - A mosaic generator module '''

import Image
import os, sys, random
import logging
import glob

try:
    import cPickle as pickle
except ImportError:
    import pickle

USING_RTREE = False
NEAREST_CACHE = {}

try:
    import rtree
    USING_RTREE = True
except:
    # we shall fall back to linear time queries in absence of rtree
    pass


def get_average_rgb(image, filename):
    red = green = blue = 0
    try:
        imdata = list(image.getdata())
        imdata_size = len(imdata)
    except:
        log.debug ("Error processing " + filename)
        return None

    try:
        for i in imdata:
            if type(i) == int:
                red += i
                green += i
                blue += i
            else:
                red += i[0]
                green += i[1]
                blue += i[2]

        # average the color of this thumbnail
        red /= imdata_size
        green /= imdata_size
        blue /= imdata_size
    except ValueError:
        log.debug ("Error processing " + filename)
    return (red, green, blue)


def get_linear_colormap(files):
    colormap = []
    file_count = 0
    total_files = len(files)
    log = logging.getLogger("PyMos")
    for eachfile in files:
        try:
            temp = Image.open(eachfile)
        except IOError as error:
            log.debug("Error opening %s" % eachfile)
            log.debug("IOError - %s" % error)
            continue

        rgb = get_average_rgb(temp, eachfile)
        if not rgb:
            continue
        
        colormap.append( ( rgb, eachfile ))
        # caching of resized images done in image_cache now

        file_count += 1
        log.debug("%.1f %% done" % ((float(file_count)/total_files)*100))
    return colormap


def get_rtree_properties():
    p = rtree.index.Property()
    p.dimension = 3
    p.dat_extension = 'data'
    p.idx_extension = 'index'
    return p
    
    
def get_rtree_colormap(files, colormap_file):
    log = logging.getLogger("PyMos")
    
    if os.path.isfile(colormap_file + ".index"):
        os.remove(colormap_file + ".index")
    if os.path.isfile(colormap_file + ".data"):
        os.remove(colormap_file + ".data")
        
    colormap = rtree.index.Index(colormap_file, properties=get_rtree_properties())
    # TODO: confirm if this is in-memory and has nothing to do with the 
    # .colormap.data and .colormap.index files and can be painlessly pickled
    
    file_count = 0
    total_files = len(files)
    
    for eachfile in files:
        try:
            temp = Image.open(eachfile)
        except IOError as error:
            log.debug("Error opening %s" % eachfile)
            log.debug("IOError - %s" % error)
            continue

        rgb = get_average_rgb(temp, eachfile)
        if not rgb:
            continue
            
        r,g,b = rgb
        # append to colormap
        colormap.add( file_count, (r,g,b,r,g,b), eachfile)
        # ^^ new format for colormap, None replaced with resized images
        # when processing to cache already loaded images

        file_count += 1
        log.debug("%.1f %% done" % ((float(file_count)/total_files)*100))
    return colormap
    
    
def build_colormap(files, colormap_file):
    ''' builds out and returns an average color to file location mapping '''
    if not USING_RTREE:
        return get_linear_colormap(files)
    else:
        return get_rtree_colormap(files, colormap_file)


def get_euclidean_match(source_color, colormap):
    # euclidean distance, color, index in colormap
    r_1, g_1, b_1 = source_color[0:3]
    match = (196608, (555, 555, 555), 0) # initially something out of range
    for index, thumbs in zip (xrange(len(colormap)), colormap):
        thumb_color = thumbs[0]
        # calculate the euclidian distance between the two colors
        r_2, g_2, b_2 = thumb_color[0:3]

        ecd_match = match[0]
        ecd_found = ( (r_2 - r_1) ** 2 + (g_2 - g_1) ** 2 +
                        (b_2-b_1) ** 2 )

        if (ecd_found < ecd_match):
            match = (ecd_found, thumb_color, index)
    return colormap[match[2]][1]

def build_mosaic(input_path, output_path, collection_path,
                    zoom = 20, thumb_size = 60, fuzz = 0, new_colormap=False):
    ''' Builds up the ouput using given parameters using colormap
        using input_path, output_path, collection_path, zoom=20,
              thumb_size=60, fuzz=0, new_colormap=False
    '''
    log = logging.getLogger("PyMos")
   
    # Build Color Index
    log.info( "Building index...")

    files = glob.glob(os.path.join(collection_path, '*.jpg'))
    colormap_file = os.path.join(collection_path, '.colormap')
    NEAREST_CACHE = {}
    
    if os.path.exists(colormap_file) and not new_colormap:
        if not USING_RTREE:
            colormap = pickle.load(open(colormap_file))
        else:
            colormap = rtree.index.Index(colormap_file, properties=get_rtree_properties())
    else:
        colormap = build_colormap(files, colormap_file)
        if not USING_RTREE:
            pickle.dump(colormap, open(colormap_file, 'w'))

    log.info("Color Index built")

    # prepare images
    try:
        source = Image.open (input_path)
        source_data = list(source.getdata())
    except IOError:
        log.debug ("Error opening %s" % input_path)
        sys.exit(0)

    source_width, source_height = source.size
    output_width, output_height = source_width*zoom, source_height*zoom

    output = Image.new("RGB", (output_width, output_height),
                            (255,255,255))
    image_cache = {}
    log.info("Generating Mosaic...")
    
    # square mosaics as for now
    for s_x in xrange(0, output_width, thumb_size):
        for s_y in xrange(0, output_height, thumb_size):
            source_color = source_data[ (s_y/zoom) * source_width + s_x/zoom ]
            is_bw = type(source_color) == int
            
            # we randomize source color for added fuziness
            if (fuzz!=0):
                if is_bw:
                    source_color = random.randint(-fuzz, fuzz) + source_color
                else:
                    source_color = tuple(s_x + random.randint(-fuzz, fuzz)
                                        for s_x in source_color)
                                        
            if is_bw:
                source_color = (source_color, source_color, source_color)
                
            if not USING_RTREE:
                match = get_euclidean_match(source_color, colormap)
            else:
                if source_color in NEAREST_CACHE:
                    match = NEAREST_CACHE[source_color]
                else:
                    match = NEAREST_CACHE[source_color] = \
                            colormap.nearest(source_color, 1, objects=True).next().object
            
            if not (match in image_cache):
                image_cache[match] = Image.open(match)
                ### new maxfill method
                tsize = image_cache[match].size
                # taller image -> fille width to complete square
                tsize =  (thumb_size,
                        int( round((float(tsize[1])/tsize[0]) * thumb_size)))

                if ( tsize[0] > tsize[1]):
                    # wider image -> fill height of thumb_sizexthumb_size square
                    tsize =  (int( round((float(tsize[0])/tsize[1]) * thumb_size )),
                        thumb_size)
                image_cache[match] = image_cache[match].resize(tsize)
                
            output.paste (image_cache[match], (s_x, s_y))
        log.debug("%.1f %% done" % ((float(s_x)/output_width) * 100))


    log.info("Mosaic Generated. Saving...")

    if (output_path == None):
        return output

    output.save(output_path, "PNG")
    log.info("Done " + output_path)
