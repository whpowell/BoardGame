import math
import pygame
import time

# Initializes the pygame library
pygame.init()

# Color definition
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WHITEA = (255, 255, 255, 0.3)
BLUE = (0, 0, 255)
BLUEA = (0, 0, 255, 0.3)
BLUEB = (0, 0, 200, 0.3)
BLUEC = (0, 0, 150, 0.3)
GREEN = (0, 255, 0)
GREENA = (0, 255, 0, 0.3)
GREENB = (0, 200, 0, 0.3)
GREENC = (0, 150, 0, 0.3)
RED = (255, 0, 0)
REDA = (255, 0, 0, 0.3)
REDB = (200, 0, 0, 0.3)
REDC = (150, 0, 0, 0.3)
YELLOWA=(255, 255, 0, 0.3)
YELLOWB=(200, 200, 0, 0.3)
YELLOWC=(150, 150, 0, 0.3)
DGREY = (120,120,120,0.4)
LGREY = (200,200,200)

class Hexagon(object):

    def __init__(self, col, row, radius, offset_x,offset_y):
        self.player=-1
        self.tiletype = "normal"
        self.transcolour=WHITEA
        self.radius = radius
    	self.offsetx = offset_x
    	self.offsety = offset_y
        self.col = col
        self.row = row
        self.x_pixel=self.offsetx+1.5*self.radius*self.col
        if self.col%2==1:
            self.y_pixel=self.offsety+math.sqrt(3)*self.radius*self.row+math.sqrt(3)/2*self.radius
        else:
            self.y_pixel=self.offsety+math.sqrt(3)*self.radius*self.row

        self.hex_z=self.row-((self.col-self.col%2))/2
        self.hex_x=self.col
        self.cube_z=self.row-((self.col-self.col%2))/2
        self.cube_x=self.col
        self.cube_y=-self.cube_x-self.cube_z
        self.cube_xyz=[self.cube_x,self.cube_y,self.cube_z]


    def vertices(self):
        self.vertices_points = []
        for ind in range(6):
            angle_deg = 60*ind
            angle_rad = math.pi/180*angle_deg
            self.vertex_x = self.x_pixel+self.radius*math.cos(angle_rad)
            self.vertex_y = self.y_pixel+self.radius*math.sin(angle_rad)
            self.vertices_points.append([self.vertex_x, self.vertex_y])

    def setTileType(self,tile_type):
        self.tiletype = tile_type

    def isstartterr(self):
	if self.tiletype == "terr":
	    return True
        else:
	    return False
	

class Hexgrid(object):

    def __init__(self,size,offset_x,offset_y,screen):
        self.hexlistname= ["hex"+ str(x) + '_' + str(y) for x in range(15) for y in range(11)]
        self.hexdict={}
        self.norm_colour_list=[GREENB, YELLOWB, REDB, BLUEB,LGREY]
        self.terr_colour_list=[GREENA, YELLOWA, REDA, BLUEA,BLACK]
        self.score_colour_list=[GREENC, YELLOWC, REDC, BLUEC,DGREY]
        self.size=size
    	self.offsetx=offset_x
    	self.offsety=offset_y
    	self.screen = screen
        for k in self.hexlistname:
            self.ksplit=k.split("hex")[1]
            self.col=self.ksplit.split('_')[0]
            self.row=self.ksplit.split('_')[1]


            if int(self.row) == 10 and int(self.col)%2==1:
                pass
            else:
                self.hexdict[k]=Hexagon(int(self.col),int(self.row),self.size,self.offsetx,self.offsety)

    def draw_hexgrid(self):
        for a in self.hexdict:
        
        	if self.hexdict[a].tiletype == "normal":
        		colour = self.norm_colour_list[self.hexdict[a].player]
        	elif self.hexdict[a].tiletype == "terr":
        		colour = self.terr_colour_list[self.hexdict[a].player]
        	elif self.hexdict[a].tiletype == "score":
        		colour = self.score_colour_list[self.hexdict[a].player]
        	else:
        		colour = WHITE
            		
        	self.hexdict[a].vertices()
        	self.plist=self.hexdict[a].vertices_points
        	pygame.draw.polygon(self.screen, colour, self.plist, 0)
        	pygame.draw.aalines(self.screen, BLACK, True, self.plist, True)
            
#        	pygame.draw.polygon(self.screen, self.hexdict[a].transcolour, self.plist, 0)            

    def sethextypes(self,coords,hextype):
        for i in coords:
	    	self.hexdict["hex%r_%r"%(i[0],i[1])].setTileType(hextype)
	    	
	def sethextypespix(self,mouse_x,mouse_y,hextype):
		self.hex_round(mouse_x,mouse_y)
		self.hex_cube=self.cube_round(self.hex2cube(self.pixel_to_hex(mouse_x,mouse_y)[0],self.pixel_to_hex(mouse_x,mouse_y)[1]))
		for k in self.hexdict:
			if self.hexdict[k].cube_xyz == self.hex_cube:
				self.hexdict[k].setTileType(hextype)

    def cube2hex(self,cube_coord):
        self.hex_x=cube_coord[0]
        self.hex_z=cube_coord[2]
        return self.hex_x,self.hex_z

    def hex2cube(self,hex_x, hex_z):
        self.cube_x = hex_x
        self.cube_y = -hex_x -hex_z
        self.cube_z = hex_z
        self.cube_coords= [self.cube_x,self.cube_y,self.cube_z]
        return self.cube_coords

    def pixel_to_hex(self,x_pixel, y_pixel):
        self.x_pixel=x_pixel-self.offsetx
        self.y_pixel=y_pixel-self.offsety

        self.q = (self.x_pixel*2.0/3.0)/self.size
        self.r =( (-self.x_pixel/3.0)+(math.sqrt(3)/3.0)*self.y_pixel)/self.size
        self.hex_frac= [self.q,self.r]
        return self.hex_frac

    def hex_round(self,x,y):
        return self.cube2hex(self.cube_round(self.hex2cube(self.pixel_to_hex(x,y)[0],self.pixel_to_hex(x,y)[1])))


    def cube_round(self,frac_cube):
        self.h = frac_cube
        self.rx = round(self.h[0])
        self.ry = round(self.h[1])
        self.rz = round(self.h[2])

        self.x_diff = abs(self.rx - self.h[0])
        self.y_diff = abs(self.ry - self.h[1])
        self.z_diff = abs(self.rz - self.h[2])

        if self.x_diff > self.y_diff and self.x_diff > self.z_diff:
            self.rx = -self.ry-self.rz
        elif self.y_diff > self.z_diff:
            self.ry = -self.rx-self.rz
        else:
            self.rz = -self.rx-self.ry
        self.cubes=[self.rx, self.ry, self.rz]
        return self.cubes

    def hex_add(self,hexa, hexb):
        return [hexa.cube_x + hexb.cube_x, hexa.cube_y + hexb.cube_y, hexa.cube_z + hexb.cube_z]

    def hex_subtract(self,hexa, hexb):
        return [hexa.cube_x - hexb.cube_x, hexa.cube_y - hexb.cube_y, hexa.cube_z - hexb.cube_z]

    def  hex_length(self, len_xyz):
        return (abs(len_xyz[0]) + abs(len_xyz[1]) + abs(len_xyz[2]))/ 2

    def hex_distance(self, hexa, hexb):
        return self.hex_length(self.hex_subtract(hexa, hexb))



    def occupied_by(self,mouse_x,mouse_y):
        self.hex_round(mouse_x,mouse_y)
        self.hex_cube=self.cube_round(self.hex2cube(self.pixel_to_hex(mouse_x,mouse_y)[0],self.pixel_to_hex(mouse_x,mouse_y)[1]))
        for k in self.hexdict:
            if self.hexdict[k].cube_xyz == self.hex_cube:
                return self.hexdict[k].player

    def occupied(self,mouse_x,mouse_y):
            self.hex_round(mouse_x,mouse_y)
            self.hex_cube=self.cube_round(self.hex2cube(self.pixel_to_hex(mouse_x,mouse_y)[0],self.pixel_to_hex(mouse_x,mouse_y)[1]))
            for k in self.hexdict:
                if self.hexdict[k].cube_xyz == self.hex_cube:
                    if self.hexdict[k].player == -1:
                        return False
                    else:
                        return True

    def onboard(self,mouse_x,mouse_y):
	    onboard = False
            self.hex_round(mouse_x,mouse_y)
            self.hex_cube=self.cube_round(self.hex2cube(self.pixel_to_hex(mouse_x,mouse_y)[0],self.pixel_to_hex(mouse_x,mouse_y)[1]))
            for k in self.hexdict:
                if self.hexdict[k].cube_xyz == self.hex_cube:
                    onboard = True                 
            return onboard

    def thistype(self,mouse_x,mouse_y):
	ttype = "normal"
        self.hex_round(mouse_x,mouse_y)
        self.hex_cube=self.cube_round(self.hex2cube(self.pixel_to_hex(mouse_x,mouse_y)[0],self.pixel_to_hex(mouse_x,mouse_y)[1]))
        for k in self.hexdict:
            if self.hexdict[k].cube_xyz == self.hex_cube:
                ttype = self.hexdict[k].tiletype           
        return ttype

    def change_owner(self,playernum,mouse_x,mouse_y):
        self.hex_round(mouse_x,mouse_y)
        self.hex_cube=self.cube_round(self.hex2cube(self.pixel_to_hex(mouse_x,mouse_y)[0],self.pixel_to_hex(mouse_x,mouse_y)[1]))
        for k in self.hexdict:
            if self.hexdict[k].cube_xyz == self.hex_cube:
                self.hexdict[k].player=playernum

    def num_terr(self,mouse_x,mouse_y):
        terrnum=0
        self.hex_round(mouse_x,mouse_y)
        self.hex_cube=self.cube_round(self.hex2cube(self.pixel_to_hex(mouse_x,mouse_y)[0],self.pixel_to_hex(mouse_x,mouse_y)[1]))
        for k in self.hexdict:
            if self.hexdict[k].cube_xyz == self.hex_cube:
                for j in self.hexdict:
                    if self.hexdict[j].player == -1:
                        pass
                    elif self.hexdict[j].player == self.hexdict[k].player and self.hex_distance(self.hexdict[k],self.hexdict[j]) < 2:
                        terrnum += 1
        return terrnum-1

    def close_neighbour(self, playernum, mouse_x, mouse_y):
        dist=20
        flag=0
        self.hex_round(mouse_x,mouse_y)
        self.hex_cube=self.cube_round(self.hex2cube(self.pixel_to_hex(mouse_x,mouse_y)[0],self.pixel_to_hex(mouse_x,mouse_y)[1]))
        for k in self.hexdict:
            if self.hexdict[k].cube_xyz == self.hex_cube:
                myname = k
                flag = 1
        if flag == 0:
            return 99
        else:
            for k in self.hexdict:
                if self.hexdict[k].player == playernum:
                    if self.hex_distance(self.hexdict[k],self.hexdict[myname]) < dist:
                        dist=self.hex_distance(self.hexdict[k],self.hexdict[myname])
        return dist
