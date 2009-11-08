#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Pandamonkium Productions present
#                ____        __  ___
#               / __ \__  __/  |/  /___  _____
#              / /_/ / / / / /|_/ / __ \/ ___/
#             / ____/ /_/ / /  / / /_/ (__  )
#            /_/    \__, /_/  /_/\____/____/
#                  /____/ 0.5
#
#                                                      -- ideamonk and yuvipanda
#                                                                 #hackers-india

''' PyMos - A mosaic generator module '''

import Image
import os, sys, math, random
import logging
import glob

try:
    import cPickle as pickle
except ImportError:
    import pickle

def build_colormap(files):
    ''' checks for presense of colormap, if not found then builds one and
        caches it for future '''
        
    colormap = []
    file_count = 0
    total_files = len(files)
    log = logging.getLogger("PyMos")
    for eachfile in files:
        temp = Image.open(eachfile)

        red = green = blue = 0
        imdata = list(temp.getdata())
        imdata_size = len(imdata)

        try:
            for i in imdata:
                red += i[0]
                green += i[1]
                blue += i[2]

            # average the color of this thumbnail
            red /= imdata_size
            green /= imdata_size
            blue /= imdata_size
        except ValueError:
            log.debug ("Error processing " + eachfile)

        # append to colormap
        colormap.append( ( (red, green, blue), eachfile, None ))
        # ^^ new format for colormap, None replaced with resized images
        # when processing to optimize

        file_count += 1
        log.debug("%.1f %% done" % ((float(file_count)/total_files)*100))
    return colormap


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

    if os.path.exists(colormap_file) and not new_colormap:
        colormap = pickle.load(open(colormap_file))
    else:
        try:
            colormap = build_colormap(files)
            pickle.dump(colormap, open(colormap_file, 'w'))
        except IOError:
            log.info( "Error: Collection not found.")
            sys.exit(1)

    log.info("Color Index built")

    # prepare images
    source = Image.open (input_path)
    source_data = list(source.getdata())
    source_width, source_height = source.size
    output_width, output_height = source_width*zoom, source_height*zoom

    output = Image.new("RGB", (output_width, output_height),
                            (255,255,255))

    log.info("Generating Mosaic...")
    # square mosaics as for now
    for s_x in xrange(0, output_width, thumb_size):
        for s_y in xrange(0, output_height, thumb_size):
            source_color = source_data[ (s_y/zoom) * source_width + s_x/zoom ]
            
            # we randomize source color for added fuziness
            if (fuzz!=0):
                source_color = tuple(s_x + random.randint(-fuzz, fuzz)
                                        for s_x in source_color)

            # euclidean distance, color, index in colormap
            match = (555, (555, 555, 555), 0)# initially something out of range

            for index, thumbs in zip (xrange(len(colormap)), colormap):
                thumb_color = thumbs[0]
                # calculate the euclidian distance between the two colors
                r_1, g_1, b_1 = source_color
                r_2, g_2, b_2 = thumb_color

                ecd_match = match[0]
                ecd_found = math.sqrt ( (r_2 - r_1) ** 2 +
                                        (g_2 - g_1) ** 2 +
                                        (b_2-b_1) ** 2 )

                if (ecd_found < ecd_match):
                    match = (ecd_found, thumb_color, index)

            try:
                if (colormap[match[2]][2] == None):   # has not been resized yet
                    colormap[match[2]] = (colormap[match[2]][0],
                    colormap[match[2]][1], Image.open(colormap[match[2]][1]))

                ### new maxfill method
                tsize = colormap[match[2]][2].size

                # taller image -> fille width to complete square
                tsize =  (
                        thumb_size,
                        int( round((float(tsize[1])/tsize[0]) * thumb_size))
                 )

                if ( tsize[0] > tsize[1]):
                    # wider image -> fill height of thumb_sizexthumb_size square
                    tsize =  (
                        int( round((float(tsize[0])/tsize[1]) * thumb_size )),
                        thumb_size
                    )

                output.paste (colormap[match[2]][2].resize (tsize), (s_x, s_y))

            except ValueError:
                log.debug ("No match for " + source_color)

        log.debug("%.1f %% done" % ((float(s_x)/output_width) * 100))


    log.info("Mosaic Generated. Saving...")

    if (output_path == None):
        return output

    output.save(output_path, "PNG")
    log.info("Done " + output_path)
