import math
import pygame

# Initializes the pygame library
pygame.init()

# Color definition
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Hexagon(object):

    radius = 25
    offset = 100

    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.x_pixel=self.offset+1.5*self.radius*self.col
        if self.col%2==1:
            self.y_pixel=self.offset+math.sqrt(3)*self.radius*self.row+math.sqrt(3)/2*self.radius
        else:
            self.y_pixel=self.offset+math.sqrt(3)*self.radius*self.row

    def axial(self):
        self.hex_z=self.row-((self.col-self.col%2))/2
        self.hex_x=self.col

    def cube(self):
        self.cube_z=self.row-((self.col-self.col%2))/2
        self.cube_x=self.col
        self.cube_y=-self.cube_x-self.cube_z


    def vertices(self):
        self.vertices_points = []
        for ind in range(6):
            angle_deg = 60*ind
            angle_rad = math.pi/180*angle_deg
            self.vertex_x = self.x_pixel+self.radius*math.cos(angle_rad)
            self.vertex_y = self.y_pixel+self.radius*math.sin(angle_rad)
            self.vertices_points.append([self.vertex_x, self.vertex_y])

class hexgrid(object):

    def __init__(self):
        self.hexlistname= ["hex"+ str(x) + '_' + str(y) for x in range(15) for y in range(11)]
        self.hexdict={}
        for k in self.hexlistname:
            self.ksplit=k.split("hex")[1]
            self.col=self.ksplit.split('_')[0]
            self.row=self.ksplit.split('_')[1]
            if int(self.row) == 10 and int(self.col)%2==1:
                pass
            else:
                self.hexdict[k]=Hexagon(int(self.col),int(self.row))

    def draw_hexgrid(self):
        for a in self.hexdict:
            self.hexdict[a].vertices()
            self.plist=self.hexdict[a].vertices_points
            pygame.draw.polygon(screen, GREEN, self.plist, 0)
            pygame.draw.aalines(screen, BLACK, True, self.plist, True)
class hexoperations(object):
    size=25
    offset=100

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
        self.x_pixel=x_pixel-self.offset
        self.y_pixel=y_pixel-self.offset

        self.q = (self.x_pixel*2.0/3.0)/self.size
        self.r =( (-self.x_pixel/3.0)+(math.sqrt(3)/3.0)*self.y_pixel)/self.size
        self.hex_frac= [self.q,self.r]
        return self.hex_frac

    def hex_round(self,hex_x,hex_y):
        return self.cube2hex(self.cube_round(self.hex2cube(hex_x,hex_y)))


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
        self.cubes=(self.rx, self.ry, self.rz)
        return self.cubes



def cart2cube(col, row):
    cube = []
    # convert odd-r offset to cube
    x = col - (row - (row % 1)) / 2
    z = row
    y = -x - z
    cube.append([x, y, z])
    return cube


# def cube2hex()




# Set the height and width of the screen
scr_height = 1000
scr_width = 1000
size = [scr_width, scr_height]
screen = pygame.display.set_mode(size)

# Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()
hexgrid1=hexgrid()
hexop=hexoperations()
while not done:
    xpos, ypos = pygame.mouse.get_pos()
    test=hexop.pixel_to_hex(xpos,ypos)
    print hexop.hex_round(test[0],test[1])
    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(10)

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

    # All drawing code happens after the for loop and but
    # inside the main while done==False loop.

    # Clear the screen and set the screen background
    screen.fill(WHITE)
    grid_size = 15
    grid_height = 10
    d = 30  # Hexagon's size
    shift = 100
    start = d + shift
    hex_h = d * 2  # Hexagon's height
    hex_w = hex_h * math.sqrt(3) * 0.5  # Hexagon's width
    hexgrid1.draw_hexgrid()

    # This MUST happen after all the other drawing commands.
    pygame.display.flip()

    # Be IDLE friendly

    # x_mouse,y_mouse=pygame.mouse.get_pos()
