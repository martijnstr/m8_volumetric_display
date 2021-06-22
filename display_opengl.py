import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import pyrr
import math 
import time
import serial
import numba
#arduino = serial.Serial('COM4', 115200, timeout=.1)

rpm =400
alpha =0
zoom = 1.5
rotation = 0

          
def refresh(f, verticies, colors, R, PHI):
            for r in range(1,R):
                k=r
                for i in range(0,PHI):
                    z=i+k*PHI
                    verticies[z]=(verticies[z][0],verticies[z][1],0,colors[f][z][0],colors[f][z][1],colors[f][z][2])

@numba.jit
def calculateColors(colors2, PHI,R, h, b, zoom):
        for F in range(0,h):
            for i in range(0,round(PHI/2)):
                for r in range(1,R):
                    z=i +r*PHI-round(F*PHI/(2*h))
                    x=round(((len(b)-1)*r*math.cos((i*2*math.pi/(PHI))-F*1*math.pi/h)/(2*R)*zoom +len(b)/2))
                    y=round(((len(b)-1)*r*math.sin((i*2*math.pi/(PHI))-F*1*math.pi/h)/(2*R)*zoom +len(b)/2))
                    Z=round(((len(b)-0.5)*(i)/(PHI/2))*zoom)
                    if (x>=len(b) or y>=len(b) or Z>=len(b)or x<0 or y<0 or z<0):
                        colors2[F][z] = (0,0,0)
                    else:
                        colors2[F][z] = b[x][y][Z]
                    z=i +r*PHI-round(F*PHI/(2*h))-round(PHI/2)
                    x=round(((len(b)-1)*r*math.cos((i*2*math.pi/(PHI))-F*1*math.pi/h+1*math.pi)/(2*R)*zoom +len(b)/2))
                    y=round(((len(b)-1)*r*math.sin((i*2*math.pi/(PHI))-F*1*math.pi/h+1*math.pi)/(2*R)*zoom +len(b)/2))
                    Z=round(((len(b)-0.5)*(i)/(PHI/2))*zoom)
                    if (x>=len(b) or y>=len(b) or Z>=len(b) or x<0 or y<0 or z<0):
                        colors2[F][z] = (0,0,0)
                    else:
                        colors2[F][z] = b[x][y][Z]










def main():
    if not glfw.init():
        return
 
    window = glfw.create_window(500, 500, "Volumetric dislplay", None, None)
 
    if not window:
        glfw.terminate()
        return
 
    glfw.make_context_current(window)

    # convert to 32bit float
    PHI=round(70)
    R=PHI
    scale=R
    h=round(85/(rpm/60))
    colors=[[0,0,0]*(PHI*R)]*h
    colors = np.empty((h, PHI*R,3), dtype = np.float32)
    colors2 = np.empty((h, PHI*R,3), dtype = np.float32)
    verticies=[(0,0,0,0,0,0)]*(PHI*R)
    verticies = np.array(verticies, dtype=np.float32)
    rho = 0.0
    

    with open('test.npy', 'rb', True) as f:
        b = np.load(f)    
        f.close()

    for i in range(0,round(PHI)):
        for r in range(1,R):
            z=i+r*PHI
            verticies[z]=((r*math.cos(i*2*math.pi/PHI)/scale),r*math.sin(i*2*math.pi/PHI)/scale*(1+r*alpha*math.sin(i*2*math.pi/PHI)/scale),0,0,0,0)


        
        
    verticies = np.array(verticies, dtype=np.float32)
 


    
    surfaces=[(0,0,0,0,0,0)]*(PHI*R)   

    for r in range(PHI,len(surfaces)):
        k=r+1
        if (r+1)%PHI==0:
            k=r-PHI+1
        surfaces[r]=(r, r+PHI, k+PHI,k+PHI,k,r)
 
    indices = np.array(surfaces, dtype = np.uint32)
 
    

    
    VERTEX_SHADER = """
 
        #version 330
 
        in vec3 position;
        in vec3 color;
        out vec3 newColor;
        
        uniform mat4 transform; 
 
        void main() {
 
         gl_Position = transform * vec4(position, 1.0f);
         newColor = color;
 
         }
 
 
    """
 
    FRAGMENT_SHADER = """
        #version 330
 
        in vec3 newColor;
        out vec4 outColor;
 
        void main() {
 
          outColor = vec4(newColor, 1.0f);
 
        }
 
    """
 
    # Compile The Program and shaders
    

    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER))

                                              
    # Create Buffer object in gpu
    VBO = glGenBuffers(1)
    # Bind the buffer
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, verticies.nbytes, verticies, GL_STATIC_DRAW)
 
    #Create EBO
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
 
 
 
 
    # get the position from  shader
    position = glGetAttribLocation(shader, 'position')
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position)
 
    # get the color from  shader
    color = glGetAttribLocation(shader, 'color')
    glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    glEnableVertexAttribArray(color)
 
    glUseProgram(shader)
 
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    t=1


    while not glfw.window_should_close(window):
        
        rot_x = pyrr.Matrix44.from_z_rotation(0)
        rot_y = pyrr.Matrix44.from_y_rotation(0)
    
        transformLoc = glGetUniformLocation(shader, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, rot_x * rot_y)
        
        glfw.poll_events()
        # data = arduino.readline()[:-2]

        if round(time.time())%2==1:
            try:
                with open('test.npy', 'rb', True) as f:
                        b = np.load(f)
                        f.close()
            except:
                print("failed fetching new data")
        
        
        try:
    
            calculateColors(colors, R, PHI, h, b, zoom)
            
            colors = colors2
        except:
            print("error") 

                    

        for f in range(0,h):

            # if data:
            #     break
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            refresh(f, verticies, colors, R, PHI)

            
            
            glBufferData(GL_ARRAY_BUFFER, verticies.nbytes, verticies, GL_DYNAMIC_DRAW)
            glDrawElements(GL_TRIANGLES,verticies.nbytes, GL_UNSIGNED_INT,  None)
            glfw.swap_buffers(window)

            x =(time.time()-t)
            if x!=0:
                fps = 1/x
                print(fps)
            t= time.time()
    glfw.terminate()
 
 
if __name__ == "__main__":
    main()