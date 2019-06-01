import math
import pygame

class Hex:
	def __init__(self,q,r):
		self.q = q
		self.r = r
		self.s = -q -r
				
class Point:
	def __init__(self,x,y):
		self.x = x
		self.y = y
		
class Orientation:
	def __init__(self,f0,f1,f2,f3,b0,b1,b2,b3,start_angle):
		self.f0 = f0
		self.f1 = f1
		self.f2 = f2
		self.f3 = f3
		self.b0 = b0
		self.b1 = b1
		self.b2 = b2
		self.b3 = b3
		self.start_angle = start_angle
		
layout_pointy = Orientation(math.sqrt(3.0),math.sqrt(3.0)/2.0,0.0,3.0/2.0,math.sqrt(3.0)/3.0,-1.0/3.0,0.0,2.0/3.0,0.5)
#layout_flat = Orientation(3.0/2.0,0.0,math.sqrt(3.0)/2.0,math.sqrt(3.0),2.0/3.0,0.0,-1.0/3.0,math.sqrt(3.0)/3.0,0.0)		

class Layout:
	def __init__(self,orientation,size,origin):
		self.orientation = orientation
		self.size = size
		self.origin = origin
		
def hex_to_pixel(layout,hex):
	orientation = layout.orientation
	x = (orientation.f0 * hex.q + orientation.f1 * hex.r) * layout.size.x
	y = (orientation.f2 * hex.q + orientation.f3 * hex.r) * layout.size.y
	return Point(x + layout.origin.x, y + layout.origin.y)
	
def hex_corner_offset(layout,corner):
	size = layout.size
	angle = 2.0 * math.pi * (corner + layout.orientation.start_angle)/6
	return Point(size.x * math.cos(angle), size.y * math.sin(angle))
	
def polygon_corners(layout,hex):
	corners = []
	center = hex_to_pixel(layout, hex)
	for i in range (6):
		offset = hex_corner_offset(layout, i)
		corners.append([center.x + offset.x, center.y + offset.y])
	return corners
	
pygame.init()
screen = pygame.display.set_mode((500,500))
lout = Layout(layout_pointy,Point(10,10),Point(0,0))
crns = polygon_corners(lout,Hex(1,1))
print crns

while 1:
	screen.fill([255,255,255])
	pygame.draw.aalines(screen,[0,0,0],False,[[0,0],[50,50]],True)