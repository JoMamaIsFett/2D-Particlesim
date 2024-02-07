import pygame
import sys
import random
import math
import colorsys
import time

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
running = True
width = screen.get_width()
height = screen.get_height()

#You can change these values

fps = 60
density = 100
angle_exclude_size = 2 / 3 * math.pi
strength_multiplier = 0.0005
max_vel = 1
particle_number = 1000
noise = 100
reset_time = 20

#don't change these variables

vector_list = []
particle_list = []
reset_timer = reset_time
start_time = time.time()
delta_time = 0
color_multiply = 4
color_divide = 10


class FluidVector:
    def __init__(self, x, y, direction, strength):
        self.x = x
        self.y = y
        self.direction = direction
        self.strength = strength

        angle_max = direction + angle_exclude_size
        angle_min = direction - angle_exclude_size

        if angle_max > 2 * math.pi:
            angle_max -= 2 * math.pi
        if angle_min < -2 * math.pi:
            angle_min += 2 * math.pi

        self.next_max = angle_max
        self.next_min = angle_min

    def render(self):
        pygame.draw.circle(screen, (255, 255, 0), (self.x, self.y), 5)

        end_x = math.cos(self.direction) * self.strength + self.x
        end_y = math.sin(self.direction) * self.strength + self.y
        pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), (end_x, end_y))

        '''

        end_x = math.cos(self.next_max) * self.strength + self.x
        end_y = math.sin(self.next_max) * self.strength + self.y
        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (end_x, end_y))

        end_x = math.cos(self.next_min) * self.strength + self.x
        end_y = math.sin(self.next_min) * self.strength + self.y
        pygame.draw.line(screen, (0, 255, 0), (self.x, self.y), (end_x, end_y))
        
        '''


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x_vel = 0
        self.y_vel = 0

    def vel(self):
        direction, distance = nearest_vector(self.x, self.y)
        strength = distance + random.randint(-noise, noise)

        x_pull = math.cos(direction) * strength
        y_pull = math.sin(direction) * strength

        multiplier = strength_multiplier * delta_time * 100
        delta_x = (x_pull - self.x_vel) * multiplier
        delta_y = (y_pull - self.y_vel) * multiplier

        self.x_vel = max(min(delta_x + self.x_vel, max_vel), -max_vel)
        self.y_vel = max(min(delta_y + self.y_vel, max_vel), -max_vel)

    def move(self):
        self.vel()

        self.x += self.x_vel * delta_time * 100
        if self.x < 0:
            self.x += width
        elif self.x > width:
            self.x -= width

        self.y += self.y_vel * delta_time * 100
        if self.y < 0:
            self.y += height
        elif self.y > height:
            self.y -= height

    def render(self):
        speed = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)

        hue = 1 - min(0.95, max(0.0, (speed * color_multiply) / color_divide))
        saturation = 1.0
        value = 1.0

        rgb = colorsys.hsv_to_rgb(hue, saturation, value)

        scaled_rgb = [int(val * 255) for val in rgb]

        pygame.draw.circle(screen, scaled_rgb, (self.x, self.y), 5)


def render():
    screen.fill((0, 0, 0))

    # for row in vector_list:
    #     for vec in row:
    #         vec.render()

    for par in particle_list:
        par.render()

    pygame.display.flip()


def key_handler(keys):
    global running
    if keys[pygame.K_ESCAPE]:
        running = False


def update():
    global reset_timer, start_time, delta_time
    for par in particle_list:
        par.move()

    if reset_timer <= 0:
        vector_list.clear()
        create_vectors()
        reset_timer = reset_time

    end_time = time.time()
    delta_time = end_time - start_time
    reset_timer -= delta_time
    start_time = time.time()


def calculate_distance(x1, y1, x2, y2):
    delta_x = x2 - x1
    delta_y = y2 - y1
    distance = math.sqrt(delta_x ** 2 + delta_y ** 2)
    return distance


def nearest_vector(x_pos, y_pos):
    x = min(round(x_pos / density), width // density - 1)
    y = min(round(y_pos / density), height // density - 1)

    vec = vector_list[x][y]

    direction = vec.direction
    distance = calculate_distance(x_pos, y_pos, vec.x, vec.y)

    return direction, distance


def new_angle(angle_min, angle_max):
    while True:
        angle = random.uniform(-math.pi, math.pi)

        if angle_min < angle < angle_max:
            return angle


def create_vectors():
    for x in range(width // density + 1):
        vector_list.append([])

        for y in range(height // density + 1):
            if y != 0:
                a_a_min = vector_list[x][y - 1].next_min
                a_a_max = vector_list[x][y - 1].next_max
                if x == 0:
                    angle = new_angle(max(a_a_min, -0.5 * math.pi), min(a_a_max, 0.5 * math.pi))
                else:
                    a_b_min = vector_list[x - 1][y].next_min
                    a_b_max = vector_list[x - 1][y].next_max
                    angle = new_angle(max(a_a_min, a_b_min), min(a_a_max, a_b_max))

            elif x != 0:
                angle = new_angle(max(vector_list[x - 1][y].next_min, 0), min(vector_list[x - 1][y].next_max, math.pi))

            else:
                angle = random.uniform(0, 0.5 * math.pi)

            vector_list[x].append(FluidVector(density * x, density * y, angle, random.randint(density // 2, density)))


create_vectors()

for i in range(particle_number):
    particle_list.append(Particle(random.randint(0, width), random.randint(0, height)))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            color_multiply = random.uniform(1, 10)
            color_divide = random.uniform(5, 15)

    key_handler(pygame.key.get_pressed())
    update()
    render()
    clock.tick()

pygame.quit()
sys.exit()
