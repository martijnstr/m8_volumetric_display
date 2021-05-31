import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import pyrr
import math 
import time
from PIL import Image

filename = "beeg yosh.jpg"
img = Image.open(filename)
#img.show()

def main():
    if not glfw.init():
        return
 
    window = glfw.create_window(1080, 1080, "Pyopengl Rotating Cube", None, None)
 
    if not window:
        glfw.terminate()
        return
 
    glfw.make_context_current(window)

 
    # convert to 32bit float
    PHI=round(100)
    
    R=100
    scale=R
    colors=[0,0,0]*(PHI*R)
    img = Image.open(filename)
    size =img.size
    verticies=[(0,0,0,0,0,0)]*(PHI*R)
    for r in range(1,R):
        for i in range(0,PHI):
            z=i+r*PHI

            verticies[z]=(r*math.cos(i*2*math.pi/PHI)/scale,r*math.sin(i*2*math.pi/PHI)/scale,0,0,0,0)
            
            colors[z] = img.getpixel((verticies[z][0]*200+350,-verticies[z][1]*200+200))
                
            #print(colors)

 
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
 
    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
                                              OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER))
 
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
    e=1
    size=img.size
    rot_x = pyrr.Matrix44.from_z_rotation(0 * glfw.get_time() )
    rot_y = pyrr.Matrix44.from_y_rotation(0)
 
    transformLoc = glGetUniformLocation(shader, "transform")
    glUniformMatrix4fv(transformLoc, 1, GL_FALSE, rot_x * rot_y)
    while not glfw.window_should_close(window):
        
        glfw.poll_events()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
 

        
        #Draw Cube
        img = Image.open(filename)

        for r in range(1,R):
            for i in range(0,PHI):
                z=i+r*PHI
                #colors = img.getpixel((verticies[z][0]*200+350,-verticies[z][1]*200+200))
                
                #print (colors)
                verticies[z]=(verticies[z][0],verticies[z][1],0,colors[z][0]/255,colors[z][1]/255,colors[z][2]/255)
        
        cube = np.array(verticies, dtype=np.float32)
        
        
        
        
        glBufferData(GL_ARRAY_BUFFER, cube.nbytes, cube, GL_STATIC_DRAW)
        glDrawElements(GL_TRIANGLES,cube.nbytes, GL_UNSIGNED_INT,  None)
        glfw.swap_buffers(window)
        
        

        fps = 1/(time.time()-t)
        print(fps)
        t= time.time()
    glfw.terminate()
 
 
if __name__ == "__main__":
    main()