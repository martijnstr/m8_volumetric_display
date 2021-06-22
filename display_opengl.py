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

rpm =402
alpha =0

          
def refresh(f, verticies, colors, R, PHI):
            for r in range(1,R):
                k=r*PHI
                for i in range(0,PHI):
                
                    z=i+k
                    verticies[z]=(verticies[z][0],verticies[z][1],0,colors[f][z][0],colors[f][z][1],colors[f][z][2])

@numba.jit
def calculateColors(colors2, PHI,R, h, b):
        for F in range(0,h):
            rho = F*1*math.pi/h
            for i in range(0,round(PHI)):
                for r in range(1,R):
                    z=i+r*PHI
                    x=round((len(b)-0.1)*r*math.cos((i*1*math.pi/(PHI))+rho)/(2*R) +len(b)/2)
                    y=round((len(b)-0.1)*r*math.sin((i*1*math.pi/(PHI))+rho)/(2*R) +len(b)/2)
                    Z=round((len(b)-0.1)*(i)/(PHI))
                    colors2[F][z] = b[x][y][Z]
            for i in range(0,round(PHI)):
                for r in range(1,R):
                    z=i+r*PHI
                    x=round((len(b)-0.1)*r*math.cos((i*1*math.pi/(PHI))+rho+math.pi)/(2*R) +len(b)/2)
                    y=round((len(b)-0.1)*r*math.sin((i*1*math.pi/(PHI))+rho+math.pi)/(2*R) +len(b)/2)
                    Z=round((len(b)-0.1)*(i)/(PHI))
                    colors2[F][z] = b[x][y][Z]
                    

@numba.jit
def calculateColors2(colors2, PHI,R, h, b):
    for F in range(0,h):
            rho = F*1*math.pi/h 
            for i in range(round(PHI/2),PHI):
                for r in range(1,R):
                    z=i+r*PHI

                    x=round((len(b)-0.1)*r*math.cos((i*2*math.pi/(PHI/2))+rho)/(2*R) +round(len((b))/2))
                    y=round((len(b)-0.1)*r*math.sin((i*2*math.pi/(PHI/2))+rho)/(2*R) +round((len(b))/2))
                    Z=round((len(b)-0.1)*(i-(PHI/2))/(PHI/2))
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
    PHI=round(80)
    R=80
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

    for F in range(0,h):
        
        rho = F*2*math.pi/h
        for i in range(0,round(PHI)):
            for r in range(1,R):
                z=i+r*PHI
                verticies[z]=((r*math.cos(i*2*math.pi/PHI)/scale),r*math.sin(i*2*math.pi/PHI)/scale*(1+r*alpha*math.sin(i*2*math.pi/PHI)/scale),0,0,0,0)
                x=round((len(b)-1)*r*math.cos((i*2*math.pi/PHI)+rho)/(2*scale) +round(len((b))/2))
                y=round((len(b)-1)*r*math.sin((i*2*math.pi/PHI)+rho)/(2*scale) +round((len(b))/2))
                Z=round((len(b)-1)*(i)/(PHI))
                colors[F][z] = b[x][y][Z]

        
        
    cube = np.array(verticies, dtype=np.float32)
 


    
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
    glBufferData(GL_ARRAY_BUFFER, cube.nbytes, cube, GL_STATIC_DRAW)
 
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

    rot_x = pyrr.Matrix44.from_z_rotation(0 )
    rot_y = pyrr.Matrix44.from_y_rotation(0)
 
    transformLoc = glGetUniformLocation(shader, "transform")
    glUniformMatrix4fv(transformLoc, 1, GL_FALSE, rot_x * rot_y)

    while not glfw.window_should_close(window):
        
        glfw.poll_events()
        # data = arduino.readline()[:-2]

        if round(time.time())%2==1:
            with open('test.npy', 'rb', True) as f:
                    b = np.load(f)
                    f.close()
        
        
        try:
            
            calculateColors(colors, R, PHI, h, b)
            #calculateColors2(colors, R, PHI, h, b)
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