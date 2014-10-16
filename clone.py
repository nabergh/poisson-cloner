from scipy import misc
from scipy import sparse
from scipy.sparse import linalg
from array import *
import math
import matplotlib.pyplot as plt

def getInd(x, y):
	return y*(width) + x

def getCoords(ind):
	return (ind % width, ind / width)

background = misc.imread('background.jpg')
foreground = misc.imread('foreground.jpg')
matte = misc.imread('matte.png')

minX, minY, maxX, maxY = len(matte[0]), len(matte), 0, 0
for y in range(len(matte)):
	for x in range(len(matte[y])):
		if matte[y][x][0] > 0:
			if x < minX:
				minX = x
			if x > maxX:
				maxX = x
			if y < minY:
				minY = y
			if y > maxY:
				maxY = y
width = maxX - minX + 1
height = maxY - minY + 1
print "Found bounding box for matted region."


for c in range(0,3):
	print "Solving color channel " + str(c)
	mat = sparse.dok_matrix((width * height, width * height))
	b = array('l', [0] * (width * height))
	for y in range(minY,maxY + 1):
		for x in range(minX,maxX + 1):
			if matte[y][x][0] > 0:
				i = getInd(x - minX, y - minY)
				mat[i, i] = 4
	
				if matte[y][x - 1][0] > 0:
					mat[i, i - 1] = -1
				else:
					b[i] += background[y][x - 1][c]
	
				if matte[y][x + 1][0] > 0:
					mat[i, i + 1] = -1
				else:
					b[i] += background[y][x + 1][c]
	
				if matte[y - 1][x][0] > 0:
					mat[i, i - width] = -1
				else:
					b[i] += background[y - 1][x][c]
	
				if matte[y + 1][x][0] > 0:
					mat[i, i + width] = -1
				else:
					b[i] += background[y + 1][x][c]
	
				b[i] += foreground[y][x][c] * 4
				b[i] -= foreground[y][x - 1][c]
				b[i] -= foreground[y][x + 1][c]
				b[i] -= foreground[y - 1][x][c]
				b[i] -= foreground[y + 1][x][c]
	mat = mat.tocsr()
	g = linalg.cg(mat, b, tol=1e-50)
	result = g[0]
	iterations = g[1]
	print "Iterations " + str(iterations)
	
	for y in range(minY,maxY + 1):
		for x in range(minX,maxX + 1):
			if matte[y][x][0] > 0:
				i = getInd(x - minX, y - minY)
				if result[i] < 0:
					result[i] = 0
				elif result[i] > 255:
					result[i] = 255    
				background[y][x][c] = result[i]
				# background[y][x][c] = foreground[y][x][c]   #naive
	
plt.imshow(background)
plt.show()
