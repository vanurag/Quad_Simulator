######### Quad with Back-Stepping control (only attitude control)


import pygame
from pygame.locals import *
import ctypes
import sys, math, numpy, pylab
import matplotlib.pyplot as plt
from images2gif import writeGif

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
    import Image
except:
    print ('The GLCUBE example requires PyOpenGL')
    raise SystemExit


mode = 'Ground View'	# Other option: "Bird's-Eye View"
#mode = "Bird's-Eye View"
resolution = 1000, 500

timer = pygame.time.Clock()

dt = 0.035

switch = 0

phi, phi_ref, phi_dot = 0.0, 0.0, 0.0
theta, theta_ref, theta_dot = 0.0, 0.0, 0.0
psi, psi_ref, psi_dot = 0.0, 0.0, 0.0
x, x_ref, x_dot = 0., 0., 0.0
y, y_ref, y_dot = 0., 0.0, 0.0
z, z_ref, z_dot = 0.0, 0.0, 0.0
sum_z,sum_z_ref = 0.0, 0.0
sum_phi,sum_phi_ref = 0.0, 0.0
sum_theta,sum_theta_ref = 0.0, 0.0
sum_psi,sum_psi_ref = 0.0, 0.0
kpz,kdz,kiz = 35, 10, 0.01
#kpz,kdz,kiz = 18.0, 10.61, 1.03
kp_phi,kd_phi,ki_phi = 0.9, 0.2, 0.2
kp_theta,kd_theta,ki_theta = 1.2, 0.2, 0.1
kp_psi,kd_psi,ki_psi = 0.9, 0.2, 0.1

# Physical Parameters
m = 1.0
g = 9.8
Ixx, Iyy, Izz = 0.0085, 0.0085, 0.0165

plot_x,plot_phi,plot_theta,plot_psi,plot_phi_ref,plot_theta_ref,plot_psi_ref = [],[],[],[],[],[],[]
t = 0

room_height = 5.
room_length = 20.0
room_breadth = 15.0

LEFT_WALL = (
	(-room_length/2,0.0,0.0), (-room_length/2,room_height,0.0), (-room_length/2,room_height,-room_breadth), \
	(-room_length/2,0.0,-room_breadth)
)

RIGHT_WALL = (
	(room_length/2,0.0,0.0), (room_length/2,room_height,0.0), (room_length/2,room_height,-room_breadth), \
	(room_length/2,0.0,-room_breadth)
)

END_WALL = (
	(-room_length/2,0.0,-room_breadth), (-room_length/2,room_height,-room_breadth), \
	(room_length/2,room_height,-room_breadth), (room_length/2,0.0,-room_breadth)
)

CEILING = (
	(-room_length/2,room_height,0.0), (-room_length/2,room_height,-room_breadth), \
	(room_length/2,room_height,-room_breadth), (room_length/2,room_height,0.0)
)

FLOOR = (
	(-room_length/2,0.0,0.0), (-room_length/2,0.0,-room_breadth), (room_length/2,0.0,-room_breadth), (room_length/2,0.0,0.0)
)

END_TEXTURE = (
	(0.0,0.0), (0.0,1.0), (1.0,1.0), (1.0,0.0)
)

RIGHT_TEXTURE = (
	(1.0,0.0), (1.0,1.0), (0.0,1.0), (0.0,0.0)
)

LEFT_TEXTURE = (
	(0.0,0.0), (0.0,1.0), (1.0,1.0), (1.0,0.0)
)

FLOOR_TEXTURE = (
	(0.0,0.0), (0.0,1.0), (1.0,1.0), (1.0,0.0)
)

CEILING_TEXTURE = (
	(0.0,1.0), (0.0,0.0), (1.0,0.0), (1.0,1.0)
)

def loadOBJ(filename,scale):  
	numVerts = 0  
	verts = []  
	norms = []  
	text = []
	vertsOut = []  
	normsOut = []  
	textOut = []
	for line in open(filename, "r"):  
	    vals = line.split() 
	    if vals != []:
		    #print vals
		    if vals[0] == "v":  
			v = map(float, vals[1:4])  
			verts.append([v[0]*scale, v[1]*scale, v[2]*scale])  
			#verts.append(str(float(v)*scale))  
		    if vals[0] == "vt":
			v = map(float, vals[1:3])
			text.append(v)
		    if vals[0] == "vn":  
			n = map(float, vals[1:4])  
			norms.append(n)  
		    if vals[0] == "f":  
			for f in vals[1:]:  
			    w = f.split("/")  
			    # OBJ Files are 1-indexed so we must subtract 1 below  
			    vertsOut.append(list(verts[int(w[0])-1])) 
			    if w[1] != '':
			    	textOut.append(list(text[int(w[1])-1]))  
			    else:
				textOut.append('NoTexture')
			    normsOut.append(list(norms[int(w[2])-1]))  
			    numVerts += 1  
		    vertsOut.append('*')
		    textOut.append('*')
		    normsOut.append('*')
	#xavg,yavg,zavg = 0., 0., 0.
	#count = 0
	#for vert in vertsOut:
		#count += 1
		#xavg += vert[0]
		#yavg += vert[1]
		#zavg += vert[2]
	#print xavg/count, yavg/count, zavg/count	-0.0490349702456 0.0573673072632 1.16036953723
	return vertsOut, textOut, normsOut


def keyPressed(inputKey):
    #pygame.event.pump()
    keysPressed = pygame.key.get_pressed()
    if keysPressed[inputKey]:
        return True
    else:
        return False


def glInit():
    global resolution
    "run the demo"
    #initialize pygame and setup an opengl display
    pygame.init()
    pygame.display.set_mode((resolution[0],resolution[1]), OPENGL|DOUBLEBUF)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    print 'OpenGl version:', glGetString(GL_VERSION)
    LoadTextures()
    #glEnable(GL_TEXTURE_2D)
    glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
    glShadeModel(GL_SMOOTH)	

    glMatrixMode(GL_PROJECTION)

scene_matrix = []
def Load_Scene_ViewMatrix():
	global phi, phi_ref, phi_dot, theta, theta_ref, theta_dot, psi, psi_ref, psi_dot
	global h_ref, x, x_ref, x_dot, y, y_ref, y_dot, z, z_ref, z_dot
	global sum_z,sum_z_ref, sum_phi,sum_phi_ref, sum_theta,sum_theta_ref, sum_psi,sum_psi_ref
	global kpz,kdz,kiz, kp_phi,kd_phi,ki_phi, kp_theta,kd_theta,ki_theta, kp_psi,kd_psi,ki_psi
	global width, height, m_to_p, f, dt, switch, t
	global theta_x,theta_y,theta_z,x_shift,y_shift,z_shift
	global scene_matrix, mode, resolution

	if mode == "Ground View":
		glLoadIdentity()
		gluPerspective(45.0,resolution[0]/resolution[1],0.1,100.0) #setup lens
		glTranslatef(0.0, -2.5, -3.0) #move back
		glRotatef(0, 1, 0, 0) #orbit higher
		#glPushMatrix()
	else:
		glLoadIdentity()
		gluPerspective(45.0,resolution[0]/resolution[1],0.1,100.0) #setup lens
		glTranslatef(0.0, -0.33, 0.0) #move back
		glRotatef(0, 1, 0, 0) #orbit higher
		
	scene_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
        print scene_matrix
    
quad_matrix = []
def Load_Quad_ViewMatrix():
	global phi, phi_ref, phi_dot, theta, theta_ref, theta_dot, psi, psi_ref, psi_dot
	global h_ref, x, x_ref, x_dot, y, y_ref, y_dot, z, z_ref, z_dot
	global sum_z,sum_z_ref, sum_phi,sum_phi_ref, sum_theta,sum_theta_ref, sum_psi,sum_psi_ref
	global kpz,kdz,kiz, kp_phi,kd_phi,ki_phi, kp_theta,kd_theta,ki_theta, kp_psi,kd_psi,ki_psi
	global width, height, m_to_p, f, dt, switch, t
	global theta_x,theta_y,theta_z,x_shift,y_shift,z_shift
	global quad_matrix, mode

	if mode == 'Ground View':
		#print glGetFloatv(GL_PROJECTION_MATRIX)
		glLoadIdentity()
		#setup the camera
		gluPerspective(45.0,resolution[0]/resolution[1],0.1,100.0) #setup lens
		glRotatef(-90, 1, 0, 0) #orbit higher
		#glRotatef(-45, 0, 0, 1) #orbit higher
		glTranslatef(0.0, -6., 1.45) #move back

		glTranslatef(0.0, 13.0, -4.0) #move back

		#glTranslatef(0.0, 1.0, -1.7) #move back
	else:
		glLoadIdentity()
		gluPerspective(45.0,resolution[0]/resolution[1],0.1,100.0) #setup lens
		glRotatef(-90, 1, 0, 0) #orbit higher
		glRotatef(-45, 0, 0, 1) #orbit higher
		glTranslatef(-0.09, 0.09, -0.18) #move back

	quad_matrix = glGetFloatv(GL_PROJECTION_MATRIX)


textures = []
def LoadTextures():
    global textures
    image = Image.open("wall2.jpg")	# wall
    image2 = Image.open("wall3.jpg")	# floor
    image3 = Image.open("ceiling3.jpg")	# ceiling
	
    ix = image.size[0]
    iy = image.size[1]
    size = 256,256
    size2 = size#256,256/2
    box = (0,0,size[0],size[1])
    #image = image.crop(box)
    #image2 = image2.crop(box)
    image = image.resize((size2[0], size2[1]), Image.ANTIALIAS)
    image2 = image2.resize((size[0], size[1]), Image.ANTIALIAS)
    image3 = image3.resize((size[0], size[1]), Image.ANTIALIAS)
    #image.thumbnail(size)
    image = image.tostring("raw", "RGBX", 0, -1)
    image2 = image2.tostring("raw", "RGBX", 0, -1)
    image3 = image3.tostring("raw", "RGBX", 0, -1)
	
    # Create Texture	
    # There does not seem to be support for this call or the version of PyOGL I have is broken.
    textures = glGenTextures(3)

    glBindTexture(GL_TEXTURE_2D, textures[0])   # 2d texture (x and y size)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, size2[0], size2[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

    glBindTexture(GL_TEXTURE_2D, textures[1])   # 2d texture (x and y size)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, size[0], size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, image2)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

    glBindTexture(GL_TEXTURE_2D, textures[2])   # 2d texture (x and y size)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, size[0], size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, image3)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)


def drawroom():
    "draw the cube"
    global textures
    left_quad = zip(LEFT_WALL, END_TEXTURE)
    right_quad = zip(RIGHT_WALL, RIGHT_TEXTURE)
    end_quad = zip(END_WALL, END_TEXTURE)
    floor_quad = zip(FLOOR, END_TEXTURE)
    ceiling_quad = zip(CEILING, CEILING_TEXTURE)
    bag1 = [left_quad,end_quad,right_quad]
    bag2 = [floor_quad]
    bag3 = [ceiling_quad]

    glBindTexture(GL_TEXTURE_2D, textures[0])
    glBegin(GL_QUADS)
    for quad in bag1:
	    for vert in quad:
		    pos, texture = vert
		    #glColor3fv(color)
	  	    glTexCoord2fv(texture)
		    glVertex3fv(pos)
    glEnd()

    glBindTexture(GL_TEXTURE_2D, textures[1])
    glBegin(GL_QUADS)
    for quad in bag2:
	    for vert in quad:
		    pos, texture = vert
		    #glColor3fv(color)
	  	    glTexCoord2fv(texture)
		    glVertex3fv(pos)
    glEnd()

    glBindTexture(GL_TEXTURE_2D, textures[2])
    glBegin(GL_QUADS)
    for quad in bag3:
	    for vert in quad:
		    pos, texture = vert
		    #glColor3fv(color)
	  	    glTexCoord2fv(texture)
		    glVertex3fv(pos)
    glEnd()

def drawquad(verts,text,norms):
    "draw the cube"

    global textures
    #glBindTexture(GL_TEXTURE_2D, textures)
    #glBegin(GL_TRIANGLES)

    glMaterialfv(GL_FRONT_AND_BACK,GL_DIFFUSE,[0.,0.,0.,1.])
    #glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT,[1.,1.,1.,1.])
    glMaterialfv(GL_FRONT_AND_BACK,GL_SPECULAR,[0/255.,51/255.,102/255.,1.])		#204*3
    glLightfv(GL_LIGHT0, GL_POSITION, [1., 1., 1., 0.])
    #glLightfv(GL_LIGHT1, GL_POSITION, [-1., -1., 1., 0.])
    #glLightfv(GL_LIGHT2, GL_POSITION, [-1., 1., 1., 0.])
    #glLightfv(GL_LIGHT3, GL_POSITION, [1., -1.,   -1., 0.])

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    #glEnable(GL_LIGHT1)
    #glEnable(GL_LIGHT2)
    #glEnable(GL_LIGHT3)

    glBegin(GL_POLYGON)
    for tri,texture,normal in zip(verts,text,norms):
	    if tri == '*':
		glEnd()
		glBegin(GL_POLYGON)
	    else:
		#for vert in tri:
		#glColor3f(1.,0.,0.)
	  	#glTexCoord2fv(texture)
		glVertex3fv(tri)
		glNormal3fv(normal)
		#print texture
		#glTexCoord2fv(texture)
		#glTexCoord2f(texture[0],texture[1])
    glEnd()

def ReadKeyInputs():
	global phi, phi_ref, phi_dot, theta, theta_ref, theta_dot, psi, psi_ref, psi_dot
	global h_ref, x, x_ref, x_dot, y, y_ref, y_dot, z, z_ref, z_dot
	global sum_z,sum_z_ref, sum_phi,sum_phi_ref, sum_theta,sum_theta_ref, sum_psi,sum_psi_ref
	global kpz,kdz,kiz, kp_phi,kd_phi,ki_phi, kp_theta,kd_theta,ki_theta, kp_psi,kd_psi,ki_psi
	global width, height, m_to_p, f, dt, switch, t
	global theta_x,theta_y,theta_z,x_shift,y_shift,z_shift
	global mode

	if keyPressed(pygame.K_SPACE) == True:
		z_ref = z_ref + 0.05
	if keyPressed(pygame.K_LCTRL) == True:
		z_ref = z_ref - 0.05
	if keyPressed(pygame.K_UP) == True:
		if theta_ref < 0.3:
		    theta_ref = theta_ref + 0.05
	if keyPressed(pygame.K_DOWN) == True:
		if theta_ref > -0.3:
		    theta_ref = theta_ref - 0.05
	if keyPressed(pygame.K_LEFT) == True:
		if phi_ref < 0.3:
		    phi_ref = phi_ref + 0.07
	if keyPressed(pygame.K_RIGHT) == True:
		if phi_ref > -0.3:
		    phi_ref = phi_ref - 0.07
	if keyPressed(pygame.K_a) == True:
		psi_ref = psi_ref + 0.001
	if keyPressed(pygame.K_d) == True:
		psi_ref = psi_ref - 0.001
	if keyPressed(pygame.K_LSHIFT) == True:
		if mode == "Bird's-Eye View":
			mode = 'Ground View'
		elif mode == 'Ground View':
			mode = "Bird's-Eye View"
		Load_Scene_ViewMatrix()
		Load_Quad_ViewMatrix()


	if keyPressed(pygame.K_ESCAPE) == True:
		#plt.plot(plot_x,plot_phi,plot_x,plot_phi_ref)
		#plt.title('Roll')
		#pylab.show()
		#plt.figure
		#plt.plot(plot_x,plot_theta,plot_x,plot_theta_ref)
		#plt.title('Pitch')
		#pylab.show()
		#plt.figure
		#plt.plot(plot_x,plot_psi,plot_x,plot_psi_ref)
		#plt.title('Yaw')
		#pylab.show()
		pygame.quit()
		sys.exit()
	if (keyPressed(pygame.K_UP) or keyPressed(pygame.K_DOWN)) == False:
		theta_ref = 0.0

	if (keyPressed(pygame.K_LEFT) or keyPressed(pygame.K_RIGHT)) == False:
		phi_ref = 0.0


def ReadMouseEvents():
	global phi, phi_ref, phi_dot, theta, theta_ref, theta_dot, psi, psi_ref, psi_dot
	global h_ref, x, x_ref, x_dot, y, y_ref, y_dot, z, z_ref, z_dot
	global sum_z,sum_z_ref, sum_phi,sum_phi_ref, sum_theta,sum_theta_ref, sum_psi,sum_psi_ref
	global kpz,kdz,kiz, kp_phi,kd_phi,ki_phi, kp_theta,kd_theta,ki_theta, kp_psi,kd_psi,ki_psi
	global width, height, m_to_p, f, dt, switch, t
	global theta_x,theta_y,theta_z,x_shift,y_shift,z_shift
	global quad_matrix, scene_matrix, mode

	events = pygame.event.get()
	#print events
	for event in events:
	    #print event
	    if event.type == MOUSEBUTTONDOWN and event.button == 1:
		print 'Left Click'
		#glLoadMatrixf(quad_matrix)
		#glTranslatef(1., 0., 0.)
		#quad_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
		#glLoadMatrixf(scene_matrix)
		#glTranslatef(1., 0., 0.)
		#scene_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
	    elif event.type == MOUSEBUTTONDOWN and event.button == 3:
		print 'Right Click'
		#glLoadMatrixf(quad_matrix)
		#glTranslatef(-1., 0., 0.)
		#quad_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
		#glLoadMatrixf(scene_matrix)
		#glTranslatef(-1., 0., 0.)
		#scene_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
	    elif event.type == MOUSEBUTTONDOWN and event.button == 4:
		#print 'Up Scroll'
		glLoadMatrixf(quad_matrix)
		glTranslatef(0., -1., 0.)
		quad_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
		glLoadMatrixf(scene_matrix)
		glTranslatef(0., 0., 1.)
		scene_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
	    elif event.type == MOUSEBUTTONDOWN and event.button == 5:
		#print 'Down Scroll'
		glLoadMatrixf(quad_matrix)
		glTranslatef(0., 0.5, 0.)
		quad_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
		glLoadMatrixf(scene_matrix)
		glTranslatef(0., 0., -0.5)
		scene_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
	    elif event.type == MOUSEMOTION and event.buttons == (1,0,0):
		glLoadMatrixf(quad_matrix)
		glTranslatef(event.rel[0]/20., 0., -event.rel[1]/20.)
		#glRotatef(event.rel[1]/5.,1,0,0)
		quad_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
		glLoadMatrixf(scene_matrix)
		glTranslatef(event.rel[0]/20., -event.rel[1]/20., 0.)
		#glRotatef(event.rel[1]/5.,1,0,0)
		scene_matrix = glGetFloatv(GL_PROJECTION_MATRIX)


def GetQuadState():
	global phi, phi_ref, phi_dot, theta, theta_ref, theta_dot, psi, psi_ref, psi_dot
	global h_ref, x, x_ref, x_dot, y, y_ref, y_dot, z, z_ref, z_dot
	global sum_z,sum_z_ref, sum_phi,sum_phi_ref, sum_theta,sum_theta_ref, sum_psi,sum_psi_ref
	global kpz,kdz,kiz, kp_phi,kd_phi,ki_phi, kp_theta,kd_theta,ki_theta, kp_psi,kd_psi,ki_psi
	global width, height, m_to_p, f, dt, switch, t
	global theta_x,theta_y,theta_z,x_shift,y_shift,z_shift
	global mode

	t += dt
	plot_x.append(t)
	plot_phi.append(phi)
	plot_phi_ref.append(phi_ref)
	plot_theta.append(theta)
	plot_theta_ref.append(theta_ref)
	plot_psi.append(psi)
	plot_psi_ref.append(psi_ref)
	
	ReadKeyInputs()	

	###### Controller #######
	alpha1,alpha2,alpha3,alpha4,alpha5,alpha6,alpha7,alpha8 = 15,15,15,15,15,15,15,15

	a1 = (Iyy-Izz)/Ixx
	a3 = (Izz-Ixx)/Iyy
	a5 = (Ixx-Iyy)/Izz
	b1 = 1/Ixx
	b2 = 1/Iyy
	b3 = 1/Izz

	z1 = phi_ref - phi
	z3 = theta_ref - theta
	z5 = psi_ref - psi
	z7 = z_ref - z
	z2 = phi_dot - alpha1*z1
	z4 = theta_dot - alpha3*z3
	z6 = psi_dot - alpha5*z5
	z8 = z_dot - alpha7*z7

	U1 = m*(z7 + g - alpha7*(z8+alpha7*z7) - alpha8*z8)/(math.cos(phi)*math.cos(theta))
	U2 = (z1 - a1*theta_dot*psi_dot - alpha1*(z2+alpha1*z1) - alpha2*z2)/b1
	U3 = (z3 - a3*phi_dot*psi_dot - alpha3*(z4+alpha3*z3) - alpha4*z4)/b2
	U4 = (z5 - a5*theta_dot*phi_dot - alpha5*(z6+alpha5*z5) - alpha6*z6)/b3
	#print U1,U2,U3,U4
	#########################

	###### Quadrotor Dynamics ######
	y_dot_dot = (math.cos(phi)*math.sin(theta)*math.cos(psi) + math.sin(psi)*math.sin(phi))*U1/m
	x_dot_dot = (math.cos(phi)*math.sin(theta)*math.sin(psi) - math.sin(phi)*math.cos(psi))*U1/m
	z_dot_dot = math.cos(theta)*math.cos(phi)*U1/m - g
	phi_dot_dot = (Iyy-Izz)*theta_dot*psi_dot/Ixx + U2/Ixx
	theta_dot_dot = (Izz-Ixx)*phi_dot*psi_dot/Iyy + U3/Iyy
	psi_dot_dot = (Ixx-Iyy)*theta_dot*phi_dot/Izz + U4/Izz

	x_dot = x_dot + dt*x_dot_dot
	x = x + dt*x_dot
	y_dot = y_dot + dt*y_dot_dot
	y = y + dt*y_dot
	z_dot = z_dot + dt*z_dot_dot
	z = z + dt*z_dot
	phi_dot = phi_dot + dt*phi_dot_dot
	phi = phi + dt*phi_dot
	theta_dot = theta_dot + dt*theta_dot_dot
	theta = theta + dt*theta_dot
	psi_dot = psi_dot + dt*psi_dot_dot
	psi = psi + dt*psi_dot

	sum_z += z
	sum_z_ref += z_ref
	sum_phi += phi
	sum_phi_ref += phi_ref
	sum_theta += theta
	sum_theta_ref += theta_ref
	sum_psi += psi
	sum_psi_ref += psi_ref

	#print math.sin(phi), math.sin(theta), math.sin(psi)

	theta_x = theta
	theta_y = psi
	theta_z = phi


def main():
    global phi, phi_ref, phi_dot, theta, theta_ref, theta_dot, psi, psi_ref, psi_dot
    global h_ref, x, x_ref, x_dot, y, y_ref, y_dot, z, z_ref, z_dot
    global sum_z,sum_z_ref, sum_phi,sum_phi_ref, sum_theta,sum_theta_ref, sum_psi,sum_psi_ref
    global kpz,kdz,kiz, kp_phi,kd_phi,ki_phi, kp_theta,kd_theta,ki_theta, kp_psi,kd_psi,ki_psi
    global width, height, m_to_p, f, dt, switch, t
    global theta_x,theta_y,theta_z,x_shift,y_shift,z_shift
    global quad_matrix, scene_matrix, mode

    glInit()

    Load_Scene_ViewMatrix()
    Load_Quad_ViewMatrix()

    #glLoadMatrixd(start_matrix)
    verts,text, norms = loadOBJ('quad_0_03.obj',0.0025)
    #print verts
    #print text
    #print norms

    #glScalef(0.5,0.5,0.5)
    while 1:

	#pygame.event.pump()
	#print pygame.mouse.get_pressed()
	#print pygame.event.get()

	ReadMouseEvents()

	glLoadMatrixf(quad_matrix)
	#print 'yea'
	#ReadKeyInputs()
	GetQuadState()
	#print x,y,z

	if mode == 'Ground View':
		glTranslatef(x, y, z)
		glRotatef(-theta*(180/math.pi), 1, 0, 0)
		glRotatef(-psi*(180/math.pi), 0, 0, 1)
		glRotatef(-phi*(180/math.pi), 0, 1, 0)
		#glTranslatef(-x, z, y)
		#glTranslatef(x, y, z)


	#quad_matrix = glGetFloatv(GL_PROJECTION_MATRIX)

	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)


	#glLoadMatrixf(quad_matrix)
	#glRotatef(1, 0, 1, 0)
	drawquad(verts,text,norms)
	#pygame.display.flip()

	glEnable(GL_TEXTURE_2D)
	glLoadMatrixf(scene_matrix)
	if mode == "Bird's-Eye View":
		glRotatef(theta*(180/math.pi), 1, 0, 0)
		glRotatef(-phi*(180/math.pi), 0, 0, 1)
		glRotatef(psi*(180/math.pi), 0, 1, 0)
		glTranslatef(-x, -z, y)
	drawroom()
	pygame.display.flip()
	glDisable(GL_TEXTURE_2D)





if __name__ == '__main__': main()
