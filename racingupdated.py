
import pygame
import random
import os
import neat
pygame.font.init()  # init font

WIN_WIDTH = 600
WIN_HEIGHT = 800
BOUNDARY = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("RacingAI")

brick_wall_img = pygame.transform.scale2x(pygame.image.load(os.path.join("brick_wall_img.jpg")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("background3.jpg")).convert_alpha(), (600, 900))
car_images = pygame.transform.scale2x(pygame.image.load(os.path.join("main_car.jpg")).convert_alpha())
road_img = pygame.transform.scale2x(pygame.image.load(os.path.join("background3.jpg")).convert_alpha())

gen = 0

class Car:
    """
    Car class representing the  car
    """
    IMGS = car_images

    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.tilt = 0
        self.vel = 0
        self.img_count = 0
        self.img = self.IMGS

    def up(self):
        """
        make the car go up
        :return: None
        """
        self.y -= 25

    def down(self):
        #make the car go down
        self.y += 25


    def draw(self, win):
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        gets the mask for the current image of the car
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Wall():
    """
    represents a wall object
    """
    GAP = 200
    VEL = 15

    def __init__(self, x):
        """
        initialize wall object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0
        # where the top and bottom of the wall is
        self.top = 0
        self.bottom = 0

        self.WALL_TOP = pygame.transform.flip(brick_wall_img, False, True)
        self.WALL_BOTTOM = brick_wall_img

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        set the height of the wall, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.WALL_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move wall based on vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draw both the top and bottom of the wall
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.WALL_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.WALL_BOTTOM, (self.x, self.bottom))


    def collide(self, car, win):
        """
        returns if a point is colliding with the wall
        :param car: Car object
        :return: Bool
        """
        car_mask = car.get_mask()
        top_mask = pygame.mask.from_surface(self.WALL_TOP)
        bottom_mask = pygame.mask.from_surface(self.WALL_BOTTOM)
        top_offset = (self.x - car.x, self.top - round(car.y))
        bottom_offset = (self.x - car.x, self.bottom - round(car.y))

        b_point = car_mask.overlap(bottom_mask, bottom_offset)
        t_point = car_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Road:
    """
    Represnts the moving road of the game
    """
    VEL = 5
    WIDTH = road_img.get_width()
    IMG = road_img

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        move road so it looks like its scrolling
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the road. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, cars, walls, base, score, gen, wall_ind):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param car: a Car object
    :param walls: List of walls
    :param score: score of the game (int)
    :param gen: current generation
    :param wall_ind: index of closest wall
    :return: None
    """
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0))

    for wall in walls:
        wall.draw(win)

    base.draw(win)
    for car in cars:
        # draw lines from car to wall
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (car.x+car.img.get_width()/2, car.y + car.img.get_height()/2), (walls[wall_ind].x + walls[wall_ind].WALL_TOP.get_width()/2, walls[wall_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (car.x+car.img.get_width()/2, car.y + car.img.get_height()/2), (walls[wall_ind].x + walls[wall_ind].WALL_BOTTOM.get_width()/2, walls[wall_ind].bottom), 5)
            except:
                pass
        # draw car
        car.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(cars)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config):
    """
    runs the simulation of the current population of
    cars and sets their fitness based on the distance they
    reach in the game.
    """
    global WIN, gen
    win = WIN
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # car object that uses that network to play
    nets = []
    cars = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        cars.append(Car(230,350))
        ge.append(genome)

    base = Road(BOUNDARY)
    walls = [Wall(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(cars) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        wall_ind = 0
        if len(cars) > 0:
            if len(walls) > 1 and cars[0].x > walls[0].x + walls[0].WALL_TOP.get_width():  # determine whether to use the first or second
                wall_ind = 1                                                                 # wall on the screen for neural network input

        for x, car in enumerate(cars):  # give each car a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            # send car location, top wall location and bottom wall location and determine from network whether to move up or not
            output = nets[cars.index(car)].activate((car.y, abs(car.y - walls[wall_ind].height), abs(car.y - walls[wall_ind].bottom)))

            if output[0] > .5:
                car.up()
            if output[0] < 0:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 up
                car.down()

        rem = []
        add_wall = False
        for wall in walls:
            wall.move()
            # check for collision
            for car in cars:
                if wall.collide(car, win):
                    ge[cars.index(car)].fitness -= 1
                    nets.pop(cars.index(car))
                    ge.pop(cars.index(car))
                    cars.pop(cars.index(car))

            if wall.x + wall.WALL_TOP.get_width() < 0:
                rem.append(wall)

            if not wall.passed and wall.x < car.x:
                wall.passed = True
                add_wall = True

        if add_wall:
            score += 1
            # can add this line to give more reward for passing through a wall (not required)
            for genome in ge:
                genome.fitness += 5 #fitness fucntion being incremented
            walls.append(Wall(WIN_WIDTH))

        for r in rem:
            walls.remove(r)

        for car in cars:
            if car.y + car.img.get_height() - 10 >= BOUNDARY or car.y < -50:
                nets.pop(cars.index(car))
                ge.pop(cars.index(car))
                cars.pop(cars.index(car))

        draw_window(WIN, cars, walls, base, score, gen, wall_ind)

        # break if score gets large enough
        '''if score > 20:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break'''


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play  car.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
