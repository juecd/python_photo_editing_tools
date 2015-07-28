import math
from struct import *
import copy



# parse the file named fname into a dictionary of the form 
# {'width': int, 'height' : int, 'max' : int, pixels : (int * int * int) list}
def parsePPM(fname):
    dict = {'width':0, 'height':0, 'max':0, 'pixels':[]}
    file = open(fname, "rb")

    file.readline()
    tmp = file.readline()
    widthHeight = tmp.split()
    maxx = file.readline()

    dict['width'] = int(widthHeight[0])
    dict['height'] = int(widthHeight[1])
    dict['max'] = int(maxx)
    
    tmp2 = file.read()
    sz = len(tmp2)
    strng = "%iB" % sz

    tple = unpack(strng, tmp2)
    start = 0
    stop = 3

    tmpArr = []

    while (len(tple)+1 >= stop):
        tmpTple = tple[start:stop]
        tmpArr.append(tmpTple)
        start = start + 3
        stop = stop + 3

    dict['pixels'] = tmpArr
    file.close()

    return dict

# write the given ppm dictionary as a PPM image file named fname
# the function should not return anything
def unparsePPM(ppm, fname):
    file = open(fname, 'wb')
    file.write ('P6\n')
    file.write('%i %i\n' % (ppm['width'], ppm['height']))
    file.write('%i\n' %ppm['max'])

    packed = ""

    for tpl in ppm['pixels']:
        str = pack('3B', tpl[0], tpl[1], tpl[2])
        packed = packed + str

    file.write(packed)

    file.close()


def negate(ppm):
    cpy = copy.deepcopy(ppm)
    maxx = cpy['max']
    for i in range(len(cpy['pixels'])):
        ls = list(cpy['pixels'][i])
        for j in range(len(ls)):
            ls[j] = maxx - ls[j]
        cpy['pixels'][i] = tuple(ls)

    return cpy


def mirrorImage(ppm):
    cpy = copy.deepcopy(ppm)
    wdth = cpy['width']

    newLs = []
    origLs = cpy['pixels']
    #split the list by wdth (aka by picture's row)
    for i in range(0, len(origLs), wdth):
        rw = origLs[i:i + wdth]
        rw.reverse()
        newLs.extend(rw)

    cpy['pixels'] = newLs
    return cpy


# produce a greyscale version of the given ppm dictionary.
# the resulting dictionary should have the same format, 
# except it will only have a single value for each pixel, 
# rather than an RGB triple.
def greyscale(ppm):
    cpy = copy.deepcopy(ppm)
    ls = [round(.299 * x[0] + .587 * x[1] + .114 * x[2]) for x in cpy['pixels']]
    cpy['pixels'] = ls
    return cpy

# take a dictionary produced by the greyscale function and write it as a PGM image file named fname
# the function should not return anything
def unparsePGM(pgm, fname):
    file = open(fname, 'wb')
    file.write ('P5\n')
    file.write('%i %i\n' % (pgm['width'], pgm['height']))
    file.write('%i\n' %pgm['max'])

    packed = ""

    for x in pgm['pixels']:
        str = pack('B', x)
        packed = packed + str

    file.write(packed)

    file.close()    



# gaussian blur code adapted from:
# http://stackoverflow.com/questions/8204645/implementing-gaussian-blur-how-to-calculate-convolution-matrix-kernel
def gaussian(x, mu, sigma):
  return math.exp( -(((x-mu)/(sigma))**2)/2.0 )

def gaussianFilter(radius, sigma):
    # compute the actual kernel elements
    hkernel = [gaussian(x, radius, sigma) for x in range(2*radius+1)]
    vkernel = [x for x in hkernel]
    kernel2d = [[xh*xv for xh in hkernel] for xv in vkernel]

    # normalize the kernel elements
    kernelsum = sum([sum(row) for row in kernel2d])
    kernel2d = [[x/kernelsum for x in row] for row in kernel2d]
    return kernel2d

def calcNewVal(gfilter, mtrx, radius, RGBindex, row, col):
    #make a matrix of given radius with specified pixel in center
    newM = [[0 for k in range(radius*2+1)] for kk in range(radius*2+1)]

    ctrR = row - radius
    ctrC = col - radius

    for x, lss in enumerate(newM):
        for y, val in enumerate(lss):
            newM[x][y] = mtrx[ctrR][ctrC][RGBindex]
            ctrC = ctrC + 1
        ctrC = col - radius
        ctrR = ctrR + 1

    sm = 0

    #multiple matrices together
    for it, ls in enumerate(newM):
        temp = [i*j for i, j in zip(ls, gfilter[it])]
        sm = sm + sum(temp)

    return round(sm)

# blur a given ppm dictionary, returning a new dictionary  
# the blurring uses a gaussian filter produced by the above function
def gaussianBlur(ppm, radius, sigma):
    # obtain the filter
    gfilter = gaussianFilter(radius, sigma)
    #gfilter = [[1,1,1], [1,1,1], [1,1,1]]

    cpy = copy.deepcopy(ppm)
    pxs = cpy['pixels']
    ht = cpy['height']
    wdth = cpy['width']
    newLs = []

    #make a matrix representing the ppm
    mtrx = [[0 for i in range(wdth)] for j in range(ht)]
    #populate the matrix
    i = 0
    j = 0
    for tpl in pxs:
        if j > wdth-1:
            i = i + 1
            j = 0
        mtrx[i][j] = tpl
        j = j + 1

    #enumerate through matrix
    for row, lss in enumerate(mtrx):
        for col, tpl in enumerate(lss):
            #if calculation goes out of bounds of image, return the tuple
            if row-radius < 0 or row+radius > ht-1 or col-radius < 0 or col+radius > wdth-1:
                newLs.append(tpl)
            else:
                newTup = []
                for RGBindex, tVal in enumerate(tpl):
                    newVal = calcNewVal(gfilter, mtrx, radius, RGBindex, row, col)
                    newTup.append(newVal)
                newLs.append(tuple(newTup))
    #newLs now contains edited pixel values
    cpy['pixels'] = newLs

    return cpy