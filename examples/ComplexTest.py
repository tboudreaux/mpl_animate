import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from matplotlib import cm
from mplEasyAnimate import animation
from tqdm import tqdm

def RK4(diffeq, y0, t, h):
    """ RK4 method for ODEs:
        Given y0 at t, returns y1 at t+h """
    k1 = h*diffeq(y0, t)                    # dy/dt at t
    k2 = h*diffeq(y0+0.5*k1, t + h/2.)      # dy/dt at t+h/2
    k3 = h*diffeq(y0+0.5*k2, t + h/2.)      # dy/dt at t+h/2
    k4 = h*diffeq(y0+k3, t + h)             # dy/dt at t+h
    return y0 + (k1+k4)/6.0 + (k2+k3)/3.0

def wavemotion2d(u0, u1):
    u2 = 2*(1-2*b)*u1 - u0                     # unshifted terms 
    u2[1:-1,1:-1] += b*( u1[1:-1,0:-2] + u1[1:-1,2:] # left, right
                        + u1[0:-2,1:-1] + u1[2:,1:-1] ) #top, bottom
    return u2

def gaussian(x):
    return np.exp(-(x-5)**2)

def force(r, t):       # force of particle pair, with relative pos r
    s = np.sqrt(np.sum(r*r, axis=-1))           # distance 
    s3 = np.dstack((s, s, s))                   # make (m,n,3) array 
    return -spring_k*(1.0 - spring_l/s3)*r      # Hooke's law 

def cloth(Y, t):    # tablecloth
    r, v, f = Y[0], Y[1], np.zeros((N,M,3))

    rtop = r[0:-1, :] - r[1:, :]                # rel pos to top neighbor 
    if t < 1:
        rright = r[:, 0:-1] - r[:, 1:]              # rel pos to right neighbor
    else:
        rright = r[:, 0:] - r[:, 1:]
    ftop, fright = force(rtop, t), force(rright, t)   # forces from top, right
    f[0:-1, :] = ftop                   # force from top 
    if t < 1:
        f[:, 0:-1] += fright                # force from right 
    else:
        f[:, :] += fright
    f[1:, :] -= ftop                    # below, left: use 3rd law 
    f[:, 1:] -= fright
    a = (f - damp*v)/mass + gvec
    if t < 1:
        v[0,0], v[0,-1], v[-1,0], v[-1,-1]=0, 0, 0, 0   # fixed coners 
    else:
        v[0,0], v[0,-1], v[-1,0], v[-1,-1]=0, 0, 0
    return np.array([v,a])

L, M, N = 2.0, 15, 15                   # size, (M,N) particle array
h, mass, damp = 0.01, 0.004, 0.01       # keep damp between [.01,.1]
x, y = np.linspace(0,L,M), np.linspace(0,L,N)
r, v = np.zeros((N,M,3)), np.zeros((N,M,3))
spring_k, spring_l = 50.0, x[1]-x[0]    # spring const., relaxed length
r[:,:, 0], r[:,:, 1] = np.meshgrid(x,y)             # initialize pos
Y, gvec = np.array([r, v]), np.array([0,0,-9.8])    # [v,a], g vector

x, y, z = r[:,:,0], r[:,:,1], r[:,:,2]                      # mesh points
fig = plt.figure(figsize=(20, 17))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(x, y, z)
t=0

anim = animation('FallingCloth.mp4')
for t in tqdm(np.arange(0, 2, h)):
    Y = RK4(cloth, Y, 0, h)
    x, y, z = Y[0,:,:,0], Y[0,:,:,1], Y[0,:,:,2]
    fig = plt.figure(figsize=(20, 17))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_zlim(-1.3, 0)
    ax.plot_surface(x, y, z)
    anim.add_frame(fig)
    plt.close(fig)
anim.close()
