import pygame
import random
from math import sqrt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

GREEN = (55, 200, 55)
BLACK = (0, 0, 0)
RED = (255, 55, 0)
DARK_GREEN = (0, 155, 0)
WHITE = (255, 255, 255)
BLUE = (50, 50, 250)

FPS = 2
screen_size = [500, 500]
atom_size = 10

n_veggies = 50
n_rabbits = 10
n_foxes = 4

veggie_deviation_from_nest = 500
rabbit_deviation_from_nest = 100
fox_deviation_from_nest = 50

veggies_nest = [0, 0]
rabbits_nest = [screen_size[0]/2, screen_size[1]/2]
foxes_nest = [0, 0]

fox_speed = 7
rabbit_speed = 5

fox_energy = 700
rabbit_energy = 300

fox_sight_distance = 100
rabbit_sight_distance = 75

rabbit_caloricity = 200
veggies_caloricity = 100

veggies_regrowth_time = 2

fox_reproduction_energy_loss = 400
rabbit_reproduction_energy_loss = 200
moving_energy_loss = 1

veggies = [pygame.Rect(veggies_nest[0] + random.random() * veggie_deviation_from_nest, veggies_nest[1] + random.random() * veggie_deviation_from_nest, atom_size, atom_size) for j in range(n_veggies)]
rabbits = [pygame.Rect(rabbits_nest[0] + random.random() * rabbit_deviation_from_nest, rabbits_nest[1] + random.random() * rabbit_deviation_from_nest, atom_size, atom_size) for j in range(n_rabbits)]
foxes = [pygame.Rect(foxes_nest[0] + random.random() * fox_deviation_from_nest, foxes_nest[1] + random.random() * fox_deviation_from_nest, atom_size, atom_size) for j in range(n_foxes)]

foxes_energies = [fox_energy for i in range(n_foxes)]
rabbits_energies = [rabbit_energy for i in range(n_rabbits)]

foxes_memories = [None for i in range(n_foxes)]
rabbits_predator_memories = [None for i in range(n_rabbits)]
rabbits_prey_memories = [None for i in range(n_rabbits)]


pygame.init()
gameDisplay = pygame.display.set_mode((screen_size[0], screen_size[1]))
pygame.display.set_caption('Sztuczne Życie')
clock = pygame.time.Clock()




def exists(object):
    if not object and object != 0:
        return False
    else:
        return True


def isNearby(agent, i, object, j, agent_sight_distance):
    if object[j][0] >= agent[i][0] - agent_sight_distance and object[j][0] <= agent[i][0] + agent_sight_distance and object[j][1] >= agent[i][1] - agent_sight_distance and object[j][1] <= agent[i][1] + agent_sight_distance:
        return True
    else:
        return False


def move(agent, i, speed, agent_energies):
    agent[i][0] += random.choice([-speed, speed])
    agent[i][1] += random.choice([-speed, speed])
    agent_energies[i] -= moving_energy_loss


def eat(agent, i, object, agent_memories, agent_energies, object_energies, object_memories, object_memories_2, calories):
    if agent[i][0] > object[agent_memories[i]][0] - atom_size and agent[i][0] < object[agent_memories[i]][0] + atom_size and agent[i][1] > object[agent_memories[i]][1] - atom_size and agent[i][1] < object[agent_memories[i]][1] + atom_size :
        agent_energies[i] += calories

        death(object, agent_memories[i], object_energies, object_memories, object_memories_2)


def chase(agent, i, object, agent_memories, speed, agent_energies):
    if object[agent_memories[i]][0] <= agent[i][0]:
        agent[i][0] -= speed
    elif object[agent_memories[i]][0] > agent[i][0]:
        agent[i][0] += speed

    if object[agent_memories[i]][1] <= agent[i][1]:
        agent[i][1] -= speed
    elif object[agent_memories[i]][1] > agent[i][1]:
         agent[i][1] += speed

    agent_energies[i] -= moving_energy_loss


def runAway(agent, i, object, agent_memories, speed, agent_energies):
    if object[agent_memories[i]][0] <= agent[i][0]:
        agent[i][0] += speed
    elif object[agent_memories[i]][0] > agent[i][0]:
        agent[i][0] -= speed

    if object[agent_memories[i]][1] <= agent[i][1]:
        agent[i][1] += speed
    elif object[agent_memories[i]][1] > agent[i][1]:
         agent[i][1] -= speed

    agent_energies[i] -= moving_energy_loss




def rememberSurrounding(agent, i , object, agent_memories, agent_sight_distance):
    nearby_indexes = [j for j in range(len(object)-1) if isNearby(agent, i, object, j, agent_sight_distance)]

    if exists(nearby_indexes):
        distances = []
        for index in nearby_indexes:
            distances.append(sqrt(((object[index][0] - agent[i][0])**2) + ((object[index][1] - agent[i][1])**2)))

        nearest_index = distances.index(min(distances))
        agent_memories[i] = nearby_indexes[nearest_index]


def forget( i, agent_memories):
    agent_memories[i] = None


def death(agent, i, agent_energies, agent_memories, agent_memories_2):
    agent.remove(agent[i])
    if exists(agent_energies):
        agent_energies.remove(agent_energies[i])
    if exists(agent_memories):
        agent_memories.remove(agent_memories[i])
    if exists(agent_memories_2):
        agent_memories_2.remove(agent_memories_2[i])


def reproduce(agent_energies, agent_memories, agent_memories_2, default_energy, reproduction_energy_loss, agent, i):
    if agent_energies[i] > default_energy * 1.5:
        agent.append(pygame.Rect(agent[i][0], agent[i][1], atom_size, atom_size))
        agent_energies.append(default_energy)
        agent_memories.append(None)
        if exists(agent_memories_2):
            agent_memories_2.append(None)

        agent_energies[i] -= reproduction_energy_loss


def keysInput():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        exit()
    pygame.event.pump()


def draw(foxes, rabbits, veggies):
    gameDisplay.fill(GREEN)

    for veggie in veggies:
        pygame.draw.rect(gameDisplay, DARK_GREEN, veggie)

    for rabbit in rabbits:
        pygame.draw.rect(gameDisplay, WHITE, rabbit)

    for fox in foxes:
        pygame.draw.rect(gameDisplay, RED, fox)


def rabbitAction(foxes, rabbits, veggies, rabbits_predator_memories, rabbits_prey_memories, rabbits_energies):
    i = 0
    while i <= len(rabbits)-1:
        if not exists(rabbits_predator_memories[i]) and not exists(rabbits_prey_memories[i]):
            move(rabbits, i, rabbit_speed, rabbits_energies)
            rememberSurrounding(rabbits, i , veggies, rabbits_prey_memories, rabbit_sight_distance)
            rememberSurrounding(rabbits, i , foxes, rabbits_predator_memories, rabbit_sight_distance)

        if exists(rabbits_predator_memories[i]):
            if rabbits_predator_memories[i] >= len(foxes) or not exists(foxes[rabbits_predator_memories[i]]) or not isNearby(rabbits, i, foxes, rabbits_predator_memories[i], rabbit_sight_distance):
                forget(i, rabbits_predator_memories)
            else:
                runAway(rabbits, i, foxes, rabbits_predator_memories, rabbit_speed, rabbits_energies)

        if exists(rabbits_prey_memories[i]):
            if rabbits_prey_memories[i] >= len(veggies) or not exists(veggies[rabbits_prey_memories[i]]) or not isNearby(rabbits, i, veggies, rabbits_prey_memories[i], rabbit_sight_distance):
                forget(i, rabbits_prey_memories)
            else:
                chase(rabbits, i, veggies, rabbits_prey_memories, rabbit_speed, rabbits_energies)
                eat(rabbits, i, veggies, rabbits_prey_memories, rabbits_energies, None, None, None, veggies_caloricity)

        print(i, "Krolik", len(rabbits), rabbits_predator_memories[i], rabbits_energies[i])
        i += 1

    i = 0
    while i <= len(rabbits)-1:
        reproduce(rabbits_energies,rabbits_predator_memories, rabbits_prey_memories, rabbit_energy, rabbit_reproduction_energy_loss, rabbits, i)
        if rabbits_energies[i] <= 0:
            death(rabbits, i, rabbits_energies, rabbits_predator_memories, rabbits_prey_memories)
        i += 1



def foxAction(foxes, rabbits, foxes_memories, foxes_energies ):
    i = 0
    while i <= len(foxes)-1:
        if not exists(foxes_memories[i]):
            rememberSurrounding(foxes, i , rabbits, foxes_memories, fox_sight_distance)
            move(foxes, i, fox_speed, foxes_energies)

        if exists(foxes_memories[i]):
            if foxes_memories[i] >= len(rabbits) or not exists(rabbits[foxes_memories[i]]) or not isNearby(foxes, i, rabbits, foxes_memories[i], fox_sight_distance):
                forget(i, foxes_memories)
            else:
                chase(foxes, i, rabbits, foxes_memories, fox_speed, foxes_energies)
                eat(foxes, i, rabbits, foxes_memories, foxes_energies, rabbits_energies, rabbits_predator_memories, rabbits_prey_memories, rabbit_caloricity)


        print(i, "Lis", len(foxes), foxes_memories[i], foxes_energies[i])
        i += 1

    i = 0
    while i <= len(foxes)-1:
        reproduce(foxes_energies, foxes_memories, None, fox_energy, fox_reproduction_energy_loss, foxes, i)
        if foxes_energies[i] <= 0:
            death(foxes, i, foxes_energies, foxes_memories, None)
        i += 1


def veggieAction(veggies, time):
    if len(veggies) != n_veggies and time % veggies_regrowth_time == 0:
        veggies.append(pygame.Rect(veggies_nest[0] + random.random() * veggie_deviation_from_nest, veggies_nest[1] + random.random() * veggie_deviation_from_nest, atom_size, atom_size))


def animatePlot(len_rabbits, len_veggies, len_foxes, len_time):
    plt.cla()
    plt.plot(len_time, len_veggies, color="g", label="Veggies")
    plt.plot(len_time, len_rabbits, color="y", label="Rabbits")
    plt.plot(len_time, len_foxes, color="r", label="Foxes")
    plt.xlabel("Time")
    plt.ylabel("Number")
    plt.legend(loc = 'upper left')
    plt.pause(1/FPS)




def game():
    time = 0

    fig = plt.figure()

    len_rabbits = []
    len_veggies = []
    len_foxes = []
    len_time = []
    plt.ion()
    plt.show()

    while True:
        len_rabbits.append(len(rabbits))
        len_veggies.append(len(veggies))
        len_foxes.append(len(foxes))
        len_time.append(time)

        keysInput()

        draw(foxes, rabbits, veggies)

        rabbitAction(foxes, rabbits, veggies, rabbits_predator_memories, rabbits_prey_memories, rabbits_energies)
        foxAction(foxes, rabbits, foxes_memories, foxes_energies )
        veggieAction(veggies, time)

        animatePlot(len_rabbits, len_veggies, len_foxes, len_time)

        time += 1
        pygame.display.update()
        clock.tick(FPS)


game()
