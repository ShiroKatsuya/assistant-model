# %load simul.py
from matplotlib import pyplot as plt
from matplotlib import animation
from random import uniform
import timeit
import os
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

os.system('cls' if os.name == 'nt' else 'clear')


class Particle:

    __slots__ = ("x", "y", "ang_speed")

    def __init__(self, x, y, ang_speed):
        self.x = x
        self.y = y
        self.ang_speed = ang_speed


class ParticleSimulator:
    def __init__(self, particles):
        self.particles = particles

    def evolve(self, dt):
        timestep = 0.00001
        nsteps = int(dt / timestep)

        for i in range(nsteps):
            for p in self.particles:

                norm = (p.x ** 2 + p.y ** 2) ** 0.5
                v_x = (-p.y) / norm
                v_y = p.x / norm

                d_x = timestep * p.ang_speed * v_x
                d_y = timestep * p.ang_speed * v_y

                p.x += d_x
                p.y += d_y


def visualize(simulator):
    # Use a modern seaborn style that many people find attractive
    plt.style.use("seaborn-v0_8-whitegrid")
    
    # Get the current positions of particles
    X = [p.x for p in simulator.particles]
    Y = [p.y for p in simulator.particles]

    # Create a figure with a dark background color and set up the axes
    fig = plt.figure(facecolor="#212529")  # gray-900
    ax = plt.subplot(111, aspect="equal", facecolor="#212529")  # gray-900
    
    # Title and other aesthetic adjustments for a cleaner look
    ax.set_title("3 BODY PROBLEM", fontsize=16, fontweight="bold", color="#ffffff" )
    ax.set_xticks([])
    ax.set_yticks([])

    # Load the image for particles
    img = plt.imread('particle.png')  # Make sure to have a particle.png image in your directory
    image_box = OffsetImage(img, zoom=0.02)  # Adjust zoom level as needed
    
    # Create annotation boxes for each particle
    annotation_boxes = []
    for x, y in zip(X, Y):
        ab = AnnotationBbox(image_box, (x, y), frameon=False)
        ax.add_artist(ab)
        annotation_boxes.append(ab)

    # Set fixed axis limits
    plt.xlim(-1, 1)
    plt.ylim(-1, 1)

    # Initialize the animation
    def init():
        for ab in annotation_boxes:
            ab.set_visible(False)
        return annotation_boxes

    # Animation function that evolves the simulation and updates positions
    def animate(i):
        simulator.evolve(0.01)  # advance the simulation
        X = [p.x for p in simulator.particles]
        Y = [p.y for p in simulator.particles]
        
        for ab, x, y in zip(annotation_boxes, X, Y):
            ab.xybox = (x, y)
            ab.set_visible(True)
        
        return annotation_boxes

    # Create the animation with a short interval between frames
    anim = animation.FuncAnimation(fig, animate, init_func=init, blit=True, interval=10)
    plt.show()


def test_visualize():
    particles = [
        Particle(0.3, 0.5, +1),
        Particle(0.0, -0.5, -1),
        Particle(-0.1, -0.4, +3),
    ]

    simulator = ParticleSimulator(particles)
    visualize(simulator)

if __name__ == "__main__":
    test_visualize()