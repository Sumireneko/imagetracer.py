import math,random,os,copy,time,sys
from math import floor,ceil,sqrt
from random import randint
from PIL import Image
from io import BytesIO
from addict import Dict
from functools import lru_cache

'''
    imagetracer.py version 0.0 Work in Progress
    The script modified for Python3
    Porting by L.Sumireneko.M
    Original author and library is a following.

    imagetracer.js version 1.2.6
    Simple raster image tracer and vectorizer written in JavaScript.
    andras@jankovics.net

The Unlicense / PUBLIC DOMAIN

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to http://unlicense.org/
'''

args = sys.argv
load_fname = 'i.png'
save_fname = 'image.svg'
option_name = 'default'

if len(args)>0:
    if len(args[1])>0:
        print(args)
        load_fname = args[1]
    if len(args)>2 and len(args[2])>0:
        option_name = args[2]

class ImageToSVGConverter():

    def __init__(self):
        self.versionnumber = '1.2.6'
        self.optionpresets = Dict({
            'default':{
                'corsenabled': False,
                'ltres': 0.05,
                'qtres': 0.98,
                'pathomit':1,
                'rightangleenhance': True,
                'colorsampling': 0,
                'numberofcolors':14,
                'mincolorratio': 0,
                'colorquantcycles':1,
                'layering': 1,
                'strokewidth':0.0,
                'linefilter': True,
                'lineart': False,
                'scale': 1,
                'roundcoords':8,
                'viewbox': True,
                'desc': False,
                'lcpr': 0,
                'qcpr': 0,
                'blurradius': 0,
                'blurdelta': 2
                },
            'default2':{
                'corsenabled': False,
                'ltres': 1,
                'qtres': 1,
                'pathomit': 8,
                'rightangleenhance': True,
                'colorsampling': 5,
                'numberofcolors': 16,
                'mincolorratio': 0,
                'colorquantcycles': 3,
                'layering': 0,
                'strokewidth': 1,
                'linefilter': False,
                'scale': 1,
                'roundcoords': 1,
                'viewbox': False,
                'desc': False,
                'lcpr': 0,
                'qcpr': 0,
                'blurradius': 0,
                'blurdelta': 20
                },
            'posterized1':{
                'colorsampling': 0,
                'numberofcolors': 2
                },
            'posterized2':{
                'numberofcolors': 4,
                'blurradius': 5
                },
            'curvy':{
                'ltres': 0.01,
                'linefilter': True,
                'rightangleenhance': False
                },
            'sharp':{
                'qtres': 0.01,
                'linefilter': False
                },
            'detailed':{
                'pathomit': 0,
                'roundcoords': 2,
                'ltres': 0.5,
                'qtres': 0.5,
                'numberofcolors': 64
                },
            'smoothed':{
                'blurradius': 5,
                'blurdelta': 64
                },
            'grayscale':{
                'colorsampling': 0,
                'colorquantcycles': 1,
                'numberofcolors': 7
                },
            'fixedpalette':{
                'colorsampling': 0,
                'colorquantcycles': 1,
                'numberofcolors': 27
                },
            'randomsampling1':{
                'colorsampling': 1,
                'numberofcolors': 8
                },
            'randomsampling2':{
                'colorsampling': 1,
                'numberofcolors': 64
                },
            'artistic1':{
                'colorsampling': 0,
                'colorquantcycles': 1,
                'pathomit': 0,
                'blurradius': 5,
                'blurdelta': 64,
                'ltres': 0.01,
                'linefilter': True,
                'numberofcolors': 16,
                'strokewidth': 2
                },
            'artistic2':{
                'qtres': 0.01,
                'colorsampling': 0,
                'colorquantcycles': 1,
                'numberofcolors': 4,
                'strokewidth': 0
                },
            'artistic3':{
                'qtres': 10,
                'ltres': 10,
                'numberofcolors': 8
                },
            'artistic4':{
                'qtres': 10,
                'ltres': 10,
                'numberofcolors': 64,
                'blurradius': 5,
                'blurdelta': 256,
                'strokewidth': 2
                },
            'posterized3':{
                'ltres': 1,
                'qtres': 1,
                'pathomit': 20,
                'rightangleenhance': True,
                'colorsampling': 0,
                'numberofcolors': 3,
                'mincolorratio': 0,
                'colorquantcycles': 3,
                'blurradius': 3,
                'blurdelta': 20,
                'strokewidth': 0,
                'linefilter': False,
                'roundcoords': 1,
                'pal': Dict(
                    {
                    'r': 0,
                    'g': 0,
                    'b': 100,
                    'a': 255
                    },
                    {
                    'r': 255,
                    'g': 255,
                    'b': 255,
                    'a': 255
                    }
                    )
                    # palette end
                }
        })
        # end of option preset

        # Lookup tables for pathscan
        # pathscan_combined_lookup[ arr[py][px] ][ dir ] = [nextarrpypx, nextdir, deltapx, deltapy];

        self.pathscan_combined_lookup = [
            [[-1,-1,-1,-1], [-1,-1,-1,-1], [-1,-1,-1,-1], [-1,-1,-1,-1]],#arr[py][px]===0 is invalid
            [[ 0, 1, 0,-1], [-1,-1,-1,-1], [-1,-1,-1,-1], [ 0, 2,-1, 0]],
            [[-1,-1,-1,-1], [-1,-1,-1,-1], [ 0, 1, 0,-1], [ 0, 0, 1, 0]],
            [[ 0, 0, 1, 0], [-1,-1,-1,-1], [ 0, 2,-1, 0], [-1,-1,-1,-1]],
            
            [[-1,-1,-1,-1], [ 0, 0, 1, 0], [ 0, 3, 0, 1], [-1,-1,-1,-1]],
            [[13, 3, 0, 1], [13, 2,-1, 0], [ 7, 1, 0,-1], [ 7, 0, 1, 0]],
            [[-1,-1,-1,-1], [ 0, 1, 0,-1], [-1,-1,-1,-1], [ 0, 3, 0, 1]],
            [[ 0, 3, 0, 1], [ 0, 2,-1, 0], [-1,-1,-1,-1], [-1,-1,-1,-1]],
            
            [[ 0, 3, 0, 1], [ 0, 2,-1, 0], [-1,-1,-1,-1], [-1,-1,-1,-1]],
            [[-1,-1,-1,-1], [ 0, 1, 0,-1], [-1,-1,-1,-1], [ 0, 3, 0, 1]],
            [[11, 1, 0,-1], [14, 0, 1, 0], [14, 3, 0, 1], [11, 2,-1, 0]],
            [[-1,-1,-1,-1], [ 0, 0, 1, 0], [ 0, 3, 0, 1], [-1,-1,-1,-1]],
            
            [[ 0, 0, 1, 0], [-1,-1,-1,-1], [ 0, 2,-1, 0], [-1,-1,-1,-1]],
            [[-1,-1,-1,-1], [-1,-1,-1,-1], [ 0, 1, 0,-1], [ 0, 0, 1, 0]],
            [[ 0, 1, 0,-1], [-1,-1,-1,-1], [-1,-1,-1,-1], [ 0, 2,-1, 0]],
            [[-1,-1,-1,-1], [-1,-1,-1,-1], [-1,-1,-1,-1], [-1,-1,-1,-1]] #arr[py][px]===15 is invalid
        ]

        # Gaussian kernel table
        self.gks = [ 
            [0.27901,0.44198,0.27901],
            [0.135336,0.228569,0.272192,0.228569,0.135336],
            [0.086776,0.136394,0.178908,0.195843,0.178908,0.136394,0.086776],
            [0.063327,0.093095,0.122589,0.144599,0.152781,0.144599,0.122589,0.093095,0.063327],
            [0.049692,0.069304,0.089767,0.107988,0.120651,0.125194,0.120651,0.107988,0.089767,0.069304,0.049692]
        ]
        
        
        # workaround for fitseq() chain bug 
        self.split_point_ex = {'is':False,'p':Dict(),'l':0,'q':0,'sp':0,'en':0}
        self.sep = os.sep
        self.debug_all_layer=''

    def load_file(self,path):
        path = '.'+self.sep+str(path)
        print(f"load file: {path}")
        with open(path, 'rb') as f:
            binary = f.read()
        img = Image.open(BytesIO(binary))
        rgba = img.convert('RGBA')
        return rgba

    def save_file(self,path,sdata):
        path = '.'+self.sep+str(path)
        print(f"Save file: {path}")
        with open(path, mode='w', encoding='UTF-8') as f:
            f.write(sdata)


    def debug_e(self,dat):
        
        o='<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>title</title></head><body>'
        oo=''
        for c in dat:
            a=self.torgbastr(dat[c])
            oo += f'<span style="font-size:2em;color:{a};" title="palette No.{c}_{a}">No.{c}■</span>'
        o+=oo
        o+='</body></html>'
        self.save_file('./export.html',o)

    def debug_e2(self,layer,ii,cnum):
        o='<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>title</title></head><body>'
        oo=''
        cnt=0
        self.debug_all_layer+='<hr><table>'
        for h in layer:
            self.debug_all_layer+=f'<tr><td>Layer:{cnt}</td>'
            for w in h:
                col = w
                a=self.torgbastr(ii.palette[col])
                self.debug_all_layer += f'<td style="width:20px;height:20px;background-color:{a};">{col}</td>'
            self.debug_all_layer+='</tr>'
            cnt+=1
        self.debug_all_layer+='</table>'
        
        #if cnum < len(ii.palette)-1:return
        o+=self.debug_all_layer
        o+='</body></html>'
        self.save_file('./export2.html',o)

    def debug_e3(self,layer,ii,cnum):
        o='<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>title</title></head><body>'
        oo=''
        cnt=0
        self.debug_all_layer+='<hr><table>'
        for h in layer:
            self.debug_all_layer+=f'<tr><td>Layer:{cnt}</td>'
            for w in h:
                #print(w)
                col = w
                a=self.torgbastr(ii.palette[col])
                self.debug_all_layer += f'<td style="width:20px;height:20px;background-color:{a};">{col}</td>'
            self.debug_all_layer+='</tr>'
            cnt+=1
        self.debug_all_layer+='</table>'
        
        #if cnum < len(ii.palette)-1:return
        if cnum != 2:return
        o+=self.debug_all_layer
        o+='</body></html>'
        self.save_file('./export2.html',o)


    def imageToSVG(self,load_f,save_f,set_option):
       # load th file
       bin_data = self.load_file(load_f)
       
       # set image data
       imgd = Dict()
       imgd.width,imgd.height = list(bin_data.size)
       
       #list(image.getdata())  RGBA tuple -> list
       '''
       nb = np.array(bin_data)# make to numpy array
       imgd.data = list(np.ravel(nb)) # flatten it 
       print(list(np.ravel(nb)))
       '''
       raw = list(bin_data.getdata())
       raw = [list(i) for i in raw] # tuple -> list
       raw=sum(raw, []) # list -> flat array
       imgd.data = raw
       
       # set options and make svg data
       options = self.checkoptions(set_option)
       td = self.imagedataToTracedata(imgd, options )
       svgdata = self.getsvgstring(td, options,True)
       
       # save the file
       self.save_file(save_f,svgdata)

    def imagedataToTracedata(self,imgd,options):
        options = self.checkoptions(options)
        # 1. Color quantization
        # ii = -1,1,0 sheet map
        ii = self.colorquantization(imgd, options)
        mode = ['Sequential layering mode(Layering:0)', 'Pallalel layering mode(Layering:1)']
        print(mode[options.layering])
        if options.layering == 0:
            # Sequential layering
            # create tracedata object
            tracedata = Dict({
                'layers' : [],
                'palette' : ii.palette,
                'width' : len(ii.array[0]) - 2,
                'height': len(ii.array) - 2
                })
            # Loop to trace each color layer
            print('Points data crete: ',time.time() - st)
            colornum = 0
            #self.debug_e(ii.palette)
            for colornum in range(0,len(ii.palette)):
                # layeringstep -> pathscan -> internodes -> batchtracepaths
                s_lay = self.layeringstep(ii, colornum)
                #print(s_lay)
                #self.debug_e2(p_lay,ii,colornum)
                p_lay = self.pathscan(s_lay, options.pathomit)
                #print(p_lay)
                i_lay = self.internodes(p_lay, options)
                #print(i_lay)

                tracedlayer = self.batchtracepaths(i_lay, options.ltres, options.qtres)
                #tracedlayer = self.batchtracepaths(self.internodes(self.pathscan(self.layeringstep(ii, colornum), options.pathomit), options), options.ltres, options.qtres)
                # adding traced layer
                #print(tracedlayer)
                tracedata.layers.append(tracedlayer)
            # End of color loop
        else:
            # Parallel layering
            # 2. Layer separation and edge detection
            ls = self.layering(ii)
            # Optional edge node visualization
            if options.layercontainerid:
                self.drawLayers(ls, self.specpalette, options.scale, options.layercontainerid)
            # 3. Batch pathscan(Dict)
            bps = self.batchpathscan(ls, options.pathomit)
            # 4. Batch interpollation(Dict)
            bis = self.batchinternodes(bps, options)
            # 5. Batch tracing and creating tracedata object
            # batchtracelayers return []
            tracedata = Dict({
                'layers': self.batchtracelayers(bis, options.ltres, options.qtres),
                'palette': ii.palette,
                'width': imgd.width,
                'height': imgd.height
                })
        # End of parallel layering
        return tracedata

    def checkoptions(self,options):
        options = options if options == None else Dict()
        # Option preset
        if (type(options) is str):
            options = options.lower()
            if self.optionpresets[options]:
                options = self.optionpresets[options]
            else:
                options = Dict()
            # Defaults
        # print(self.optionpresets['default'].keys())
        ok = list(self.optionpresets['default'].keys())
        # print(str(type(options)))
        k = 0
        for k in ok:
            # print(f'{k}')
            if options.get(k, None) == None:
                options[k] = self.optionpresets['default'][k]
        return options

    #////////////////////////////////////////////////////////////
    #//
    #//  Vectorizing functions
    #//
    #////////////////////////////////////////////////////////////
    
    # 1. Color quantization
    # Using a form of k-means clustering repeatead options.colorquantcycles times. http://en.wikipedia.org/wiki/Color_quantization

    def colorquantization(self,imgd, options):
        arr = []
        idx = 0
        paletteacc = Dict()
        w = imgd.width
        h = imgd.height
        pixelnum = w * h
        palette = Dict()
        copy_deepcopy = copy.deepcopy
        
        # imgd.data must be RGBA, not just RGB
        if len(imgd.data) < pixelnum * 4:
            alloc = pixelnum * 4
            newimgddata = [0] * alloc
            #newimgddata = np.array(([0] * alloc),dtype='uint8') # Uint8,  ClampedArray?
            for pxcnt in range(0,pixelnum):
                imgq = imgd.data[pxcnt*3:pxcnt*3+3]
                p4 = pxcnt*4
                newimgddata[p4] = imgq[0]
                newimgddata[p4 + 1] = imgq[1]
                newimgddata[p4 + 2] = imgq[2]
                newimgddata[p4 + 3] = 255
            imgd.data = newimgddata
        # End of RGBA imgd.data check
        # Filling arr (color index array) with -1
        print(f'Image size = height:{imgd.height}px * width:{imgd.width}px')
        arr = [[-1] * (w+2) for _ in range(h+2)]
        #arr = np.full((h + 2,w + 2), -1)
        
        # Use custom palette if pal is defined or sample / generate custom length palette
        # parette is Dict() object
        if options.pal:palette = options.pal
        elif options.colorsampling == 0:palette = self.generatepalette(options.numberofcolors)
        elif options.colorsampling == 1:palette = self.samplepalette(options.numberofcolors, imgd)
        else:palette = self.samplepalette2(options.numberofcolors, imgd)
        
        # Selective Gaussian blur preprocessing
        if options.blurradius > 0:
            imgd = self.blur( imgd, options.blurradius, options.blurdelta )
        # Repeat clustering step options.colorquantcycles times
        print('createPalette: ',time.time() - st)
        idt_palette = Dict()
        for i in range(0,len(palette)):
            idt_palette[i] = Dict({'r': 0,'g': 0,'b': 0,'a': 0,'n': 0 })
        print('Pixel Analysis: ',time.time() - st)
        
        cycle_limit = options.colorquantcycles - 1
        min_col_ratio = options.mincolorratio
        plen = len(palette)
        for cnt in range(0,options.colorquantcycles):
            # Average colors from the second iteration
            if cnt > 0:
                # This indent fixed
                # Reseting palette accumulator for averaging
                paletteacc = copy_deepcopy(idt_palette)
                # averaging paletteacc for palette
                for k in range(0, len(palette)):
                    # averaging
                    #print( paletteacc )
                    kpal = paletteacc[k]
                    n = kpal.n
                    if n > 0:
                        palette[k] = self.ret_pal(kpal.r,kpal.g,kpal.b,kpal.a,n)

                    # Randomizing a color, if there are too few pixels and there will be a new cycle len(paletteacc[k])>0 and 
                    if (n / pixelnum < min_col_ratio) and (cnt < cycle_limit):
                        palette[k] =Dict({
                            'r': floor(randint(0, 255)),
                            'g': floor(randint(0, 255)),
                            'b': floor(randint(0, 255)),
                            'a': floor(randint(0, 255))
                            })
            # End of palette loop
            # End of Average colors from the second iteration
            # Reseting palette accumulator for averaging
            print('Quantize Cycle',cnt,"_",time.time() - st)
            
            paletteacc=copy_deepcopy(idt_palette)

            for ｊ in range(0,h):
                for i in range(0,w):
                    # pixel index
                    idx = (j * w + i) * 4
                    # find closest color from palette by measuring (rectilinear) color distance between this pixel and all palette colors
                    ci = cd = 0;cdl = 1024;# 4 * 256 is the maximum RGBA distance 
                    q0,q1,q2,q3 = imgd.data[idx:idx+4]# get a list of imgd.data[idx] to imgd.data[idx + 3]

                    for k in range(0,plen):
                        # In my experience, https://en.wikipedia.org/wiki/Rectilinear_distance works better than https://en.wikipedia.org/wiki/Euclidean_distance
                        kpal = palette[k]

                        cd = self.min_max(kpal.r,kpal.g,kpal.b,kpal.a,q0,q1,q2,q3)

                        # Remember this color if this is the closest yet
                        if cd < cdl:cdl = cd;ci = k;
                    # End of palette loop
                    # add to palettacc
                    paletteacc[ci].r += q0
                    paletteacc[ci].g += q1
                    paletteacc[ci].b += q2
                    paletteacc[ci].a += q3
                    paletteacc[ci].n += 1
                    # update the indexed color array
                    arr[j + 1][i + 1] = ci
                    # End of i loop
                # End of j loop
        # End of cnt loop
        return Dict({ 'array':arr, 'palette':palette })

    @lru_cache(maxsize=1000)
    def ret_pal(self,r,g,b,a,n):
        return Dict({
            'r': floor(r / n),
            'g': floor(g / n),
            'b': floor(b / n),
            'a': floor(a / n)
            })


    @lru_cache(maxsize=1024)
    def min_max(self,r,g,b,a,q0,q1,q2,q3):
        c1 = (max([r, q0]) - min([r, q0]))+(max([g, q1]) - min([g, q1]))+(max([b, q2]) - min([b, q2]))+(max([a, q3]) - min([a, q3]))
        return int(c1)

    # Sampling a palette from imagedata
    def samplepalette(self,numberofcolors,imgd):
        idx,palette = 0,Dict()
        imgseed = len(imgd.data)/4
        for i in range(0,numberofcolors):
            idx = floor(randint(0, imgseed)) * 4
            imgq = imgd.data[idx:idx+4]# get a list of imgd.data[idx] to imgd.data[idx + 3]
            palette[i]=Dict({
                'r': imgq[0],
                'g': imgq[1],
                'b': imgq[2],
                'a': imgq[3]
            })
        return palette

    # Deterministic sampling a palette from imagedata: rectangular grid
    def samplepalette2(self,numberofcolors,imgd):
        idx = 0
        pdx = 0
        palette = Dict()
        ni = ceil(sqrt(numberofcolors))
        nj = ceil(numberofcolors / ni)
        vx = imgd.width / (ni + 1)
        vy = imgd.height / (nj + 1)
        w = imgd.width
        l = len(palette)
        for j in range(0,nj):
            for i in range(0,nj):
                if l == numberofcolors:
                    break
                else:
                    idx = floor((j + 1) * vy * w + (i + 1) * vx) * 4
                    imgq = imgd.data[idx:idx+4]# get a list of imgd.data[idx] to imgd.data[idx + 3]
                    palette[pdx]=Dict({
                        'r': imgq[0],
                        'g': imgq[1],
                        'b': imgq[2],
                        'a': imgq[3]
                        })
                    pdx+=1
        return palette

    #Generating a palette with numberofcolors
    def generatepalette(self,numberofcolors):
        palette = Dict()
        rcnt = 0;gcnt = 0;bcnt = 0;
        if numberofcolors < 8:
            # Grayscale
            graystep = floor(255 / (numberofcolors - 1))
            i = 0
            for i in range(0,numberofcolors):
                palette[i]=Dict({
                    'r': i * graystep,
                    'g': i * graystep,
                    'b': i * graystep,
                    'a': 255
                    })
        else:
            # RGB color cube
            colorqnum = floor(numberofcolors ** (1 / 3))
            gstep = colorqnum - 1
            if gstep == 0:gstep = 1
            colorstep = floor(255 / gstep)
            rndnum = numberofcolors - colorqnum * colorqnum * colorqnum
            # number of random colors
            pdx = 0;
            for rcnt in range(0,colorqnum):
                for gcnt in range(0,colorqnum):
                    for bcnt in range(0,colorqnum):
                        palette[pdx]=Dict({
                            'r': rcnt * colorstep,
                            'g': gcnt * colorstep,
                            'b': bcnt * colorstep,
                            'a': 255
                            })
                        pdx+=1
                    # End of blue loop
                # End of green loop
            # End of red loop
            # Rest is random
            for rcnt in range(0,rndnum):
                palette[pdx]=Dict({
                    'r': floor(randint(0, 255)),
                    'g': floor(randint(0, 255)),
                    'b': floor(randint(0, 255)),
                    'a': floor(randint(0, 255))
                })
                pdx+=1
        # End of numberofcolors check
        return palette

    # 2. Layer separation and edge detection
    # Edge node types ( ▓: this layer or 1; ░: not this layer or 0 )
    # 12  ░░  ▓░  ░▓  ▓▓  ░░  ▓░  ░▓  ▓▓  ░░  ▓░  ░▓  ▓▓  ░░  ▓░  ░▓  ▓▓
    # 48  ░░  ░░  ░░  ░░  ░▓  ░▓  ░▓  ░▓  ▓░  ▓░  ▓░  ▓░  ▓▓  ▓▓  ▓▓  ▓▓
    #     0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15

    def layering(self,ii):
        # Creating layers for each indexed color in arr
        # This function use when layer = 1 (Old way)
        layers = []
        val = 0
        ah = len(ii.array)
        aw = len(ii.array[0])
        ak = len(ii.palette)

        n1=n2=n3=n4=n5=n6=n7=n8=0
        # Create layers
        k = 0
        
        # 3 Dimension array
        layers = [[[0] * aw for _ in range(0, ah)]for _ in range(0, ak)]

        # Looping through all pixels and calculating edge node type
        for j in range(1,ah-1):
            for i in range(1,aw-1):
                # This pixel's indexed color
                val = ii.array[j][i]
                
                # Are neighbor pixel colors the same?
                n1 = 1 if ii.array[j - 1][i - 1] == val else 0
                n2 = 1 if ii.array[j - 1][i    ] == val else 0
                n3 = 1 if ii.array[j - 1][i + 1] == val else 0
                n4 = 1 if ii.array[j    ][i - 1] == val else 0
                n5 = 1 if ii.array[j    ][i + 1] == val else 0
                n6 = 1 if ii.array[j + 1][i - 1] == val else 0
                n7 = 1 if ii.array[j + 1][i    ] == val else 0
                n8 = 1 if ii.array[j + 1][i + 1] == val else 0
                # this pixel's type and looking back on previous pixels
                layers[val][j + 1][i + 1] = 1 + n5 * 2 + n8 * 4 + n7 * 8
                if not n4:layers[val][j + 1][i    ] = 0 + 2 + n7 * 4 + n6 * 8
                if not n2:layers[val][j    ][i + 1] = 0 + n3 * 2 + n5 * 4 + 8
                if not n1:layers[val][j    ][i    ] = 0 + n2 * 2 + 4 + n4 * 8
            # End of i loop
        # End of j loop
        return layers

    # 2. Layer separation and edge detection
    # Edge node types ( ▓: this layer or 1; ░: not this layer or 0 )
    # 12  ░░  ▓░  ░▓  ▓▓  ░░  ▓░  ░▓  ▓▓  ░░  ▓░  ░▓  ▓▓  ░░  ▓░  ░▓  ▓▓
    # 48  ░░  ░░  ░░  ░░  ░▓  ░▓  ░▓  ░▓  ▓░  ▓░  ▓░  ▓░  ▓▓  ▓▓  ▓▓  ▓▓
    #     0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15

    def layeringstep(self,ii, cnum):
        # Creating layers for each indexed color in arr
        layer = []
        val = 0
        ah = len(ii.array)
        aw = len(ii.array[0])

        # Create layer
        layer = [[0] * aw for _ in range(ah)]
        #layer = np.full((ah, aw), 0)

        # Looping through all pixels and calculating edge node type
        c0=c1=c2=c3=0
        for j in range(1,ah):
            for i in range(1,aw):
                c0 = 1 if ii.array[j - 1][i - 1] == cnum else 0
                c1 = 2 if ii.array[j - 1][i] == cnum else 0
                c2 = 8 if ii.array[j][i - 1] == cnum else 0
                c3 = 4 if ii.array[j][i] == cnum else 0
                layer[j][i] = c0+c1+c2+c3
            # End of i loop
        # End of j loop
        # return single layer
        return layer
    
    # Point in polygon test
    def pointinpoly(self,p, pa):
        isin = False
        max_pa = len(pa)-1
        for i in range(0,max_pa):
            if i==0:
                j = max_pa - 1
            else:
                j = i - 1
            pajx = pa[j].x;pajy = pa[j].y;paix = pa[i].x;paiy = pa[i].y;
            
            # zero divide check
            m1 = (pajx - paix) * (p.y - paiy)
            m2 = (pajy - paiy)
            
            if m1 == 0:m1 = 0.1#print('zerodiv', f'{pajx} - {paix} * {p.y} - {paiy}')
            if m2 == 0:m2 = 0.1#print('zerodiv2', f'{pajy} - {paiy}') 
            #if pa[i].y > p.y != pa[j].y > p.y and p.x < (pa[j].x - (pa[i].x)) * (p.y - (pa[i].y)) / (pa[j].y - (pa[i].y)) + pa[i].x:
            if ((paiy > p.y) != (pajy > p.y)) and (p.x < (m1 / m2 + paix)):
                isin = not isin
            else:
                isin = isin
        return isin

    # 3. Walking through an edge node array, discarding edge node types 0 and 15 and creating paths from the rest.
    # Walk directions (dir): 0 > ; 1 ^ ; 2 < ; 3 v 

    def pathscan(self,arr, pathomit ):
        
        paths = Dict()
        pacnt = 0;pcnt = 0;px = 0;py = 0;
        w = len(arr[0]);h = len(arr);
        dir = 0;pathfinished = True;holepath = False;lookuprow = None;
        for j in range(0,h):
            for i in range(0,w):
                # This is original arr[py(j)][px(i)]
                arr_in = arr[j][i]
                if (arr_in == 4) or (arr_in == 11):# Other values are not valid
                    # Init
                    py = j;px = i;
                    paths[pacnt] = Dict({'points' : Dict(), 'boundingbox' : [px,py,px,py],'holechildren':list() })
                    pathfinished = False
                    pcnt = 0
                    holepath = True if arr_in == 11 else False
                    dir = 1
                    # Path points loop
                    while not pathfinished:
                        # New path point
                        #if len(paths[pacnt].points) - 1 < pcnt: pathfinished = False
                        paths[pacnt].points[pcnt] = Dict({ 'x' : px - 1, 'y' : py - 1, 't': arr[py][px] })
                        # Bounding box
                        if (px - 1) < paths[pacnt].boundingbox[0]: paths[pacnt].boundingbox[0] = px - 1
                        if (px - 1) > paths[pacnt].boundingbox[2]: paths[pacnt].boundingbox[2] = px - 1
                        if (py - 1) < paths[pacnt].boundingbox[1]: paths[pacnt].boundingbox[1] = py - 1
                        if (py - 1) > paths[pacnt].boundingbox[3]: paths[pacnt].boundingbox[3] = py - 1
                        # Next: look up the replacement, direction and coordinate changes = clear this cell, turn if required, walk forward
                        lookuprow = self.pathscan_combined_lookup[arr[py][px]][dir]
                        # This is updated arr[py(j)][px(i)]
                        arr[py][px] = lookuprow[0];dir = lookuprow[1];px += lookuprow[2];py += lookuprow[3];
                        
                        # Close path
                        if ((px - 1) == paths[pacnt].points[0].x) and ((py - 1) == paths[pacnt].points[0].y):
                            pathfinished = True
                            # Discarding paths shorter than pathomit
                            if len(paths[pacnt].points) < pathomit:
                                paths.popitem()
                            else:
                                if holepath==True:paths[pacnt].isholepath = True
                                else:paths[pacnt].isholepath = False
                                
                                # Finding the parent shape for this hole
                                if holepath == True:
                                    parentidx = 0
                                    parentbbox = [-1,-1,w+1,h+1]
                                    parentcnt = 0
                                    for parentcnt in range(0,pacnt):
                                        prc = list(paths[parentcnt].boundingbox)
                                        pc = list(paths[pacnt].boundingbox)
                                        pts0 = paths[pacnt].points[0] # Dict()
                                        pts = paths[parentcnt].points # Dict()
                                        if (not paths[parentcnt].isholepath) and self.boundingboxincludes(prc, pc) and self.boundingboxincludes(parentbbox, prc) and self.pointinpoly(pts0, pts):
                                            parentidx = parentcnt
                                            parentbbox = prc
                                    paths[parentidx].holechildren.append(pacnt)
                                # End of holepath parent finding
                                pacnt+=1
                        # End of Close path
                        pcnt+=1
                    # End of Path points loop
                # End of Follow path
            # End of i loop
        # End of j loop
        return paths

    def boundingboxincludes(self,parentbbox, childbbox ):
        if len(parentbbox) == 0:return False
        if len(childbbox) == 0:return False
        #print(parentbbox,childbbox)
        return ( ( parentbbox[0] < childbbox[0] ) and ( parentbbox[1] < childbbox[1] ) and ( parentbbox[2] > childbbox[2] ) and ( parentbbox[3] > childbbox[3] ) )

    # 3. Batch pathscan
    def batchpathscan(self,layers, pathomit):
        bpaths=Dict()
        for k in range(0,len(layers)):
            bpaths[k]=self.pathscan(layers[k], pathomit)
        return bpaths


    # 4. interpollating between path points for nodes with 8 directions ( East, SouthEast, S, SW, W, NW, N, NE )
    def internodes(self,paths, options):
        ins = Dict()
        palen = 0;nextidx = 0;nextidx2 = 0;previdx = 0;previdx2 = 0;
        opt_r_angle_ehnc = options.rightangleenhance
        # paths loop
        for pacnt in range(0,len(paths)):
            ins[pacnt] = Dict({
                'points': [] ,
                'boundingbox' : list(paths[pacnt].boundingbox),
                'holechildren' : list(paths[pacnt].holechildren),
                'isholepath' : paths[pacnt].isholepath
                })
            palen = len(paths[pacnt].points)
            # pathpoints loop
            for pcnt in range(0,palen):
                # next and previous point indexes
                nextidx = (pcnt + 1) % palen;nextidx2 = (pcnt + 2) % palen;
                previdx = (pcnt - 1 + palen) % palen;previdx2 = (pcnt - 2 + palen) % palen;
                # right angle enhance
                if (opt_r_angle_ehnc and self.testrightangle(paths[pacnt], previdx2, previdx, pcnt, nextidx, nextidx2)):
                    # Fix previous direction
                    ipcp_last = len(ins[pacnt].points) - 1
                    if ipcp_last > 0:
                        ins[pacnt].points[ipcp_last].linesegment = self.getdirection(ins[pacnt].points[ipcp_last].x, ins[pacnt].points[ipcp_last].y, paths[pacnt].points[pcnt].x, paths[pacnt].points[pcnt].y)
                    # This corner point
                    ins[pacnt].points.append(Dict({
                        'x': paths[pacnt].points[pcnt].x,
                        'y': paths[pacnt].points[pcnt].y,
                        'linesegment': self.getdirection(paths[pacnt].points[pcnt].x, paths[pacnt].points[pcnt].y, (paths[pacnt].points[pcnt].x + paths[pacnt].points[nextidx].x) / 2, (paths[pacnt].points[pcnt].y + paths[pacnt].points[nextidx].y) / 2)
                        }))
                # End of right angle enhance
                # interpolate between two path points
                ins[pacnt].points.append(Dict({
                    'x': (paths[pacnt].points[pcnt].x + paths[pacnt].points[nextidx].x) / 2,
                    'y': (paths[pacnt].points[pcnt].y + paths[pacnt].points[nextidx].y) / 2,
                    'linesegment': self.getdirection((paths[pacnt].points[pcnt].x + paths[pacnt].points[nextidx].x) / 2, (paths[pacnt].points[pcnt].y + paths[pacnt].points[nextidx].y) / 2, (paths[pacnt].points[nextidx].x + paths[pacnt].points[nextidx2].x) / 2, (paths[pacnt].points[nextidx].y + paths[pacnt].points[nextidx2].y) / 2)
                    }))
            # End of pathpoints loop
        # End of paths loop
        return ins

    def testrightangle(self,path, idx1, idx2, idx3, idx4, idx5):
        ppts = path.points
        return ((ppts[idx3].x == ppts[idx1].x) and (ppts[idx3].x == ppts[idx2].x) and (ppts[idx3].y == ppts[idx4].y) and (ppts[idx3].y == ppts[idx5].y)) or ((ppts[idx3].y == ppts[idx1].y) and (ppts[idx3].y == ppts[idx2].y) and (ppts[idx3].x == ppts[idx4].x) and (ppts[idx3].x == ppts[idx5].x))

    def getdirection(self, x1, y1, x2, y2):
        val = 8
        if x1 < x2:
            if y1 < y2: val = 1 # SE
            elif y1 > y2:val = 7 # NE
            else:val = 0 # E
        elif x1 > x2:
            if y1 < y2:val = 3 # SW
            elif y1 > y2:val = 5 # NW
            else:val = 4 # W
        else:
            if y1 < y2:val = 2 # S
            elif y1 > y2:val = 6 # N
            else:val = 8 # center, this should not happen
        return val

    # 4. Batch interpollation
    
    def batchinternodes(self,bpaths, options):
        binternodes = Dict()
        for k in bpaths:
            binternodes[k]=self.internodes(bpaths[k], options)
        return binternodes

    # 5. tracepath() : recursively trying to fit straight and quadratic spline segments on the 8 direction internode path
    
    # 5.1. Find sequences of points with only 2 segment types
    # 5.2. Fit a straight line on the sequence
    # 5.3. If the straight line fails (distance error > ltres), find the point with the biggest error
    # 5.4. Fit a quadratic spline through errorpoint (project this to get controlpoint), then measure errors on every point in the sequence
    # 5.5. If the spline fails (distance error > qtres), find the point with the biggest error, set splitpoint = fitting point
    # 5.6. Split sequence and recursively apply 5.2. - 5.6. to startpoint-splitpoint and splitpoint-endpoint sequences

    def tracepath(self,path, ltres, qtres):
        pcnt = 0;segtype1 = '';segtype2 = '';seqend = 0;smp = Dict();
        smp.segments = []
        smp.boundingbox = list(path.boundingbox)
        smp.holechildren = list(path.holechildren)
        smp.isholepath = bool(path.isholepath)
        pcnt_max = len(path.points)
        while pcnt < pcnt_max:
            # 5.1. Find sequences of points with only 2 segment types
            segtype1 = path.points[pcnt].linesegment
            segtype2 = -1
            seqend = pcnt + 1
            
            while ((path.points[seqend].linesegment == segtype1) or (path.points[seqend].linesegment == segtype2) or (segtype2 == -1)) and (seqend < len(path.points) - 1):
                if (path.points[seqend].linesegment != segtype1) and (segtype2 == -1):
                    segtype2 = path.points[seqend].linesegment
                seqend+=1
            if seqend == len(path.points) - 1:seqend = 0
            # 5.2. - 5.6. Split sequence and recursively apply 5.2. - 5.6. to startpoint-splitpoint and splitpoint-endpoint sequences
            # smp.segments = smp.segments.extend(self.fitseq(path, ltres, qtres, pcnt, seqend))
            
            # fitseq chain
            self.split_point_ex['is'] = False
            smp.segments.append(self.fitseq(path, ltres, qtres, pcnt, seqend))
            
            if self.split_point_ex['is'] == True:
                self.split_point_ex['is'] = False
                spx = self.split_point_ex
                smp.segments.append(self.fitseq(spx['p'],spx['l'],spx['q'],spx['sp'],spx['en']))
                # stupid failsafe
                if self.split_point_ex['is'] == True:
                    self.split_point_ex['is'] = False
                    spx = self.split_point_ex
                    smp.segments.append(self.fitseq(spx['p'],spx['l'],spx['q'],spx['sp'],spx['en']))
                    if self.split_point_ex['is'] == True:
                        self.split_point_ex['is'] = False
                        spx = self.split_point_ex
                        smp.segments.append(self.fitseq(spx['p'],spx['l'],spx['q'],spx['sp'],spx['en']))
            # forward pcnt;
            if seqend > 0:
                pcnt = seqend
            else:
                pcnt = len(path.points)
        # End of pcnt loop
        return smp

    # 5.2. - 5.6. recursively fitting a straight or quadratic line segment on this sequence of path nodes,
    # called from tracepath()

    def fitseq(self, path, ltres, qtres, seqstart, seqend ):
        # return if invalid seqend
        # print("Seq St", seqstart,"Seq En",seqend)
        if ((seqend > len(path.points)) or (seqend < 0)):return Dict()
        # variables
        errorpoint = seqstart;errorval = 0;
        curvepass = True
        px = 0;py = 0;dist2 = None;
        tl = seqend - seqstart
        if tl < 0:tl += len(path.points)
        en = path.points[seqend]
        st = path.points[seqstart]
        vx = (en.x - st.x) / tl
        vy = (en.y - st.y) / tl
        # 5.2. Fit a straight line on the sequence
        pcnt = (seqstart + 1) % len(path.points);pl = 0;
        while pcnt != seqend:
            pl = pcnt - seqstart
            if pl < 0:pl += len(path.points)
            px = path.points[seqstart].x + vx * pl;py = path.points[seqstart].y + vy * pl;
            dist2 = (path.points[pcnt].x - px) * (path.points[pcnt].x - px) + (path.points[pcnt].y - py) * (path.points[pcnt].y - py)
            if dist2 > ltres:curvepass = False
            if dist2 > errorval:errorpoint = pcnt;errorval = dist2;
            pcnt = (pcnt + 1) % len(path.points)
        # return straight line if fits
        if curvepass:
            return Dict({
            'type': 'L',
            'x1': path.points[seqstart].x,
            'y1': path.points[seqstart].y,
            'x2': path.points[seqend].x,
            'y2': path.points[seqend].y
            })
        # 5.3. If the straight line fails (distance error>ltres), find the point with the biggest error
        fitpoint = errorpoint
        curvepass = True
        errorval = 0
        # 5.4. Fit a quadratic spline through this point, measure errors on every point in the sequence
        # helpers and projecting to get control point
        t = (fitpoint - seqstart) / tl
        t1 = (1 - t) * (1 - t)
        t2 = 2 * (1 - t) * t
        t3 = t * t
        cpx = (t1 * path.points[seqstart].x + t3 * path.points[seqend].x - path.points[fitpoint].x) / -t2
        cpy = (t1 * path.points[seqstart].y + t3 * path.points[seqend].y - path.points[fitpoint].y) / -t2
        # Check every point
        pcnt = seqstart + 1
        while pcnt != seqend:
            t = (pcnt - seqstart) / tl
            t1 = (1 - t) * (1 - t)
            t2 = 2 * (1 - t) * t
            t3 = t * t
            px = t1 * path.points[seqstart].x + t2 * cpx + t3 * path.points[seqend].x
            py = t1 * path.points[seqstart].y + t2 * cpy + t3 * path.points[seqend].y
            dist2 = (path.points[pcnt].x - px) * (path.points[pcnt].x - px) + (path.points[pcnt].y - py) * (path.points[pcnt].y - py)
            if dist2 > qtres:curvepass = False
            if dist2 > errorval:errorpoint = pcnt;errorval = dist2;
            pcnt = (pcnt + 1) % len(path.points)
        # return spline if fits
        if curvepass == True:
            return Dict({
            'type': 'Q',
            'x1': path.points[seqstart].x,'y1': path.points[seqstart].y,
            'x2': cpx,'y2': cpy,
            'x3': path.points[seqend].x,'y3': path.points[seqend].y
            })
        # 5.5. If the spline fails (distance error>qtres), find the point with the biggest error
        splitpoint = fitpoint
        # Earlier: math.floor((fitpoint + errorpoint)/2);
        
        # 5.6. Split sequence and recursively apply 5.2. - 5.6. to startpoint-splitpoint and splitpoint-endpoint sequences
        self.split_point_ex = {'p':path, 'l': ltres, 'q': qtres, 'sp': splitpoint, 'en': seqend, 'is': True}
        return self.fitseq(path, ltres, qtres, seqstart, splitpoint)
        #return self.fitseq(path, ltres, qtres, seqstart, splitpoint).update( self.fitseq(path, ltres, qtres, splitpoint, seqend))



    # 5. Batch tracing paths
    def batchtracepaths(self,internodepaths, ltres, qtres):
        btracedpaths = []
        for k in internodepaths:
            if internodepaths.get(k, None) == None:continue
            btracedpaths.append(self.tracepath(internodepaths[k], ltres, qtres))
        return btracedpaths

    # 5. Batch tracing layers
    def batchtracelayers(self,binternodes, ltres, qtres):
        btbis = []
        for k in range(0,len(binternodes)):
            try:
                btbis.append( self.batchtracepaths(binternodes[k], ltres, qtres));
            except IndexError:
                print('Layer idx error was skipped!');continue
        return btbis

    #////////////////////////////////////////////////////////////
    #//
    #//  SVG Drawing functions
    #//
    #////////////////////////////////////////////////////////////

    def get_xy(self,d,num,ops,roundc):
        # options_roundcoords == -1: not use  roundtodec 0
        if roundc == -1:
            return d[f'x{num}'] * ops , d[f'y{num}'] * ops
        else:
            return self.roundtodec(d[f'x{num}'] * ops,1) , self.roundtodec(d[f'y{num}'] * ops,1)

    # Rounding to given decimals https://stackoverflow.com/questions/11832914/round-to-at-most-2-decimal-places-in-javascript
    def roundtodec(self,val, places):
        if val < 0: val = val * -1
        fmt = '{:.'+str(places)+'f}'
        return str(fmt.format(val))
    
    def cond_(self,obj,tr,el):
        if obj:return tr
        return el
    
    def svgpathstring(self,tracedata, lnum, pathnum, options):
        hcnt = 0;hsmp = 0;
        layer = tracedata.layers[lnum]
        smp = layer[pathnum]
        smp_seg_max = len(smp.segments)
        ops = options.scale
        # Line filter
        if (options.linefilter and (smp_seg_max < 3)):return ''
        # print('Segment_Length',smp_seg_max)
        
        # Starting path element, desc contains layer and path number
        #str = '<path ' + self.cond_(options.desc,f'desc="l {lnum} p {pathnum}" ', '') + self.tosvgcolorstr(tracedata.palette[lnum], options) + 'd="'

        str = ''.join(['<path ',
                self.cond_(options.desc,f'desc="l {lnum} p {pathnum}" ', ''),
                self.tosvgcolorstr(tracedata.palette[lnum], options),
                'd="'
                ])

        # Creating non-hole path string
        # options_roundcoords == -1 is not use self.roundtodec()
        roundc = options.roundcoords
        xx1,yy1 = self.get_xy(smp.segments[0],1,ops,roundc)
        str += f'M {xx1} {yy1} '
        
        for pcnt in range(0,smp_seg_max):
            tp = smp.segments[pcnt].type
            xx2,yy2 = self.get_xy(smp.segments[pcnt],2,ops,roundc)
            str += f'{tp} {xx2} {yy2} '
            if smp.segments[pcnt].get('x3', None) != None:
                xx3,yy3 = self.get_xy(smp.segments[pcnt],3,ops,roundc)
                str += f'{xx3} {yy3} '
        str += 'Z '

        # End of creating non-hole path string
        # Hole children
        #print("Sample:",layer[0])
        hcnt_max=len(smp.holechildren)
        for hcnt in range(0,hcnt_max):
            #print("Check:",hcnt, "layer_length",len(layer))
            hsmp = layer[ smp.holechildren[hcnt] ]
            hsmp_seg_total = len(hsmp.segments) - 1
            seglast = hsmp.segments[hsmp_seg_total]
            # workaround
            # print("Segment_length at hole", hsmp_seg_total)
            # options_roundcoords == -1 is not use self.roundtodec()
            roundc = options.roundcoords
            if seglast.get('x3', None) != None:
                xx3,yy3 = self.get_xy(seglast,3,ops,roundc)
                str += f'M {xx3} {yy3} '
            else:
                xx2,yy2 = self.get_xy(seglast,2,ops,roundc)
                str += f'M {xx2} {yy2} '
            pcnt = hsmp_seg_total
            while pcnt >= 0:
                str += hsmp.segments[pcnt].type + ' '
                if hsmp.segments[pcnt].get('x3', None) != None:
                    xx2,yy2 = self.get_xy(hsmp.segments[pcnt],2,ops,roundc)
                    str += f'{xx2} {yy2} '
                xx1,yy1 = self.get_xy(hsmp.segments[pcnt],1,ops,roundc)
                str += f'{xx1} {yy1} '
                pcnt-=1
            # End of creating hole path string
            str += 'Z '# Close path
        # End of holepath check
        # Closing path element
        str += '" />'
        # Rendering control points
        opt_l = options.lcpr;opt_q = options.qcpr;
        
        if (opt_l or opt_q):
            qc = opt_q * 0.2
            lc = opt_l * 0.2
            pcnt_max = len(smp.segments)
            for pcnt in range(0,pcnt_max):
                if smp.segments[pcnt].get('x3', None) != None and opt_q:
                    xx2 = smp.segments[pcnt].x2 * ops;yy2 = smp.segments[pcnt].y2 * ops;
                    str += f'<circle cx="{xx2}" cy="{yy2}" r="{opt_q}" fill="cyan" stroke-width="{qc}" stroke="black" />'
                    
                    xx3 = smp.segments[pcnt].x3 * ops;yy3 = smp.segments[pcnt].y3 * ops;

                    str += f'<circle cx="{xx3}" cy="{yy3}" r="{opt_q}" fill="white" stroke-width="{qc}" stroke="black" />'
                    
                    xx1 = smp.segments[pcnt].x1 * ops;yy1 = smp.segments[pcnt].y1 * ops;
                    xx2 = smp.segments[pcnt].x2 * ops;yy2 = smp.segments[pcnt].y2 * ops;
                    
                    str += f'<line x1="{xx1}" y1="{yy1}" x2="{xx2}" y2="{yy2}" stroke-width="{qc}" stroke="cyan" />'
                    
                    xx2 = smp.segments[pcnt].x2 * ops;yy2 = smp.segments[pcnt].y2 * ops;
                    xx3 = smp.segments[pcnt].x3 * ops;yy3 = smp.segments[pcnt].y3 * ops;

                    str += f'<line x1="{xx2}" y1="{yy2}" x2="{xx3}" y2="{yy3}" stroke-width="{qc}" stroke="cyan" />'
                
                if smp.segments[pcnt].get('x3', None) == None and opt_l:
                    xx2 = smp.segments[pcnt].x2 * ops;yy2 = smp.segments[pcnt].y2 * ops;
                    str += f'<circle cx="{xx2}" cy="{yy2}" r="{opt_l}" fill="white" stroke-width="{lc}" stroke="black" />'
            # Hole children control points
            hcnt_max = len(smp.holechildren)
            for hcnt in range(0,hcnt_max):
                hsmp = layer[smp.holechildren[hcnt]]
                pcnt = 0;pcnt_max=len(hsmp.segments)
                for pcnt in range(0,pcnt_max):
                    hsp = hsmp.segments[pcnt]
                    if ((hsp.get('x3', None) != None) and opt_q):
                        xx2 = hsp.x2 * ops;yy2 = hsp.y2 * ops;
                        str += f'<circle cx="{xx2}" cy="{yy2}" r="{opt_q}" fill="cyan" stroke-width="{qc}" stroke="black" />'
                        
                        xx3 = hsp.x3 * ops;yy3 = hsp.y3 * ops;
                        str += f'<circle cx="{xx3}" cy="{yy3}" r="{opt_q}" fill="white" stroke-width="{qc}" stroke="black" />'
                        
                        xx1 = hsp.x1 * ops;yy1 = hsp.y1 * ops;
                        xx2 = hsp.x2 * ops;yy2 = hsp.y2 * ops;
                        str += f'<line x1="{xx1}" y1="{yy1}" x2="{xx2}" y2="{yy2}" stroke-width="{qc}" stroke="cyan" />'
                        
                        xx2 = hsp.x2 * ops;yy2 = hsp.y2 * ops;
                        xx3 = hsp.x3 * ops;yy3 = hsp.y3 * ops;
                        str += f'<line x1="{xx2}" y1="{yy2}" x2="{xx3}" y2="{yy3}" stroke-width="{qc}" stroke="cyan" />'
                        
                    if (hsp.get('x3', None) == None) and opt_l:
                        xx2 = hsp.x2 * ops;yy2 = hsp.y2 * ops;
                        str += f'<circle cx="{xx2}" cy="{yy2}" r="{opt_l}" fill="white" stroke-width="{lc}" stroke="black" />'
                    # End of  pcnt loop
                # End of hcnt loop
        # End of Rendering control points
        return str

    def getsvgstring (self,tracedata, options,flag):
        options = self.checkoptions(options)
        w = tracedata.width * options.scale
        h = tracedata.height * options.scale
        # SVG start
        if options.viewbox:
            vb = f'viewBox="0 0 {w} {h}" '
        else:
            vb = f'width="{w}" height="{h}" '

        # Drawing: Layers and Paths loops
        svghead = '<svg ' + vb + 'version="1.1" xmlns="http://www.w3.org/2000/svg" desc="Created with imagetracer.js version ' + self.versionnumber + '" >'
        svgstr=''
        tls = tracedata.layers
        lcnt =len(tls) - 1
        while lcnt >= 0 :
            pcnt =len(tls[lcnt])-1
            while pcnt >= 0:
                # Adding SVG <path> string
                if not tls[lcnt][pcnt].isholepath:
                    svgstr+=self.svgpathstring(tracedata, lcnt, pcnt, options)
                pcnt-=1
            # End of paths loop
            lcnt-=1
        # End of layers loop
        # SVG End
        if flag==False:return svgstr
        return ''.join([svghead , svgstr , '</svg>'])

    # Comparator for numeric Array.sort
    def compareNumbers(self,a, b):
        return a - b

    # Convert color object to rgba string
    def torgbastr(self,c):
        return f'rgba({c.r},{c.g},{c.b},{c.a})'

    # Convert color object to SVG color string
    def tosvgcolorstr(self,c, options):
        sw = options.strokewidth
        ld = options.lineart
        op = c.a / 255.0
        
        if ld == True:
            if sw <= 0:sw = 1
            return f'fill="none" stroke="rgb({c.r},{c.g},{c.b})" stroke-width="{sw}"  paint-order="stroke" stroke-linejoin="round" opacity="{op}" '
        return f'fill="rgb({c.r},{c.g},{c.b})" stroke="rgb({c.r},{c.g},{c.b})" stroke-width="{sw}"  paint-order="stroke" stroke-linejoin="round" opacity="{op}" '

    # HTML Helper function: Appending an <svg> element to a container from an svgstring
    def appendSVGString(svgstr, parentid):
        return

    #////////////////////////////////////////////////////////////
    #//
    #//  Canvas functions
    #//
    #////////////////////////////////////////////////////////////

    def blur(self,imgd, radius, delta):
        i,j,k,d,idx = 0,0,0,0,0
        racc,gacc,bacc,aacc,wacc = 0,0,0,0,0
        w = imgd.width
        h = imgd.height
        empdata = [0] * len(imgd.data)
        # new ImageData
        imgd2 = Dict({
            'width': w,
            'height': h,
            'data': empdata.copy()
            })
        
        # radius and delta limits, this kernel
        radius = math.floor(radius)
        if radius < 1:return imgd
        if radius > 5:radius = 5
        delta = abs(delta)
        if delta > 1024:delta = 1024
        # Gaussian Table
        thisgk = self.gks[radius - 1]
        # loop through all pixels, horizontal blur
        for j in range(0,h):
            for i in range(0,w):
                # gauss kernel loop
                for k in range(-radius,radius + 1):
                    # add weighted color values
                    if (i + k > 0) and (i + k < w):
                        idx = (j * w + i + k) * 4
                        tgk = thisgk[k + radius];
                        # print(imgd.data[idx] , tgk)
                        imgq = imgd.data[idx:idx+4]# get a list of imgd.data[idx] to imgd.data[idx + 3]
                        racc += imgq[0] * tgk
                        gacc += imgq[1] * tgk
                        bacc += imgq[2] * tgk
                        aacc += imgq[3] * tgk
                        wacc += tgk
                # The new pixel
                idx = (j * w + i) * 4
                imgd2.data[idx] = math.floor(racc / wacc)
                imgd2.data[idx + 1] = math.floor(gacc / wacc)
                imgd2.data[idx + 2] = math.floor(bacc / wacc)
                imgd2.data[idx + 3] = math.floor(aacc / wacc)
            # End of width loop
        # End of horizontal blur
        # copying the half blurred imgd2 # Uint8,  ClampedArray?
        # himgd = new Uint8ClampedArray(imgd2.data)
        himgd = imgd2.data # empdata.copy()
        
        # loop through all pixels, vertical blur
        for j in range(0,h):
            for i in range(0,w):
                # gauss kernel loop
                for k in range(-radius,radius + 1):
                    # add weighted color values
                    if j + k > 0 and j + k < h:
                        idx = ((j + k) * w + i) * 4
                        tgk = thisgk[k + radius]
                        himgq = himgd[idx:idx+4]# get a list of himgd[idx] to himgd[idx + 3]
                        racc += himgq[0] * tgk
                        gacc += himgq[1] * tgk
                        bacc += himgq[2] * tgk
                        aacc += himgq[3] * tgk
                        wacc += tgk
                # The new pixel
                idx = (j * w + i) * 4
                imgd2.data[idx] = math.floor(racc / wacc)
                imgd2.data[idx + 1] = math.floor(gacc / wacc)
                imgd2.data[idx + 2] = math.floor(bacc / wacc)
                imgd2.data[idx + 3] = math.floor(aacc / wacc)
                # End of width loop
        # End of vertical blur
        # Selective blur: loop through all pixels
        for j in range(0,h):
            for i in range(0,w):
                idx = (j * w + i) * 4
                # d is the difference between the blurred and the original pixel
                imgq = imgd.data[idx:idx+4]# get a list of imgd.data[idx] to imgd.data[idx + 3]
                img2q = imgd2.data[idx:idx+4]
                d = abs(img2q[0] - imgq[0]) + abs(img2q[1] - imgq[1]) + abs(img2q[2] - imgq[2]) + abs(img2q[3] - imgq[3])
                # selective blur: if d>delta, put the original pixel back
                if d > delta:
                    imgd2.data[idx] = imgq[0]
                    imgd2.data[idx + 1] = imgq[1]
                    imgd2.data[idx + 2] = imgq[2]
                    imgd2.data[idx + 3] = imgq[3]
                # End of i loop
            # End of j loop
        # End of Selective blur
        return imgd2


st = time.time()
gen = ImageToSVGConverter()
gen.imageToSVG(load_fname,save_fname,option_name)
print('Elapse: ',time.time() - st)
print('Done!')