import math
import pygame
import os
from datetime import datetime
import time
from pygame.locals import *


window_x, window_y = 5, 32
width, height = 1600, 900
cellSize = 100
frames_per_second = 25.0

start_pos = (7, 0)
goal_pos = (14, 4)

HEURISTIC = "manhattan" # "manhattan" or "straight"
SEARCH_ALGO = "hillclimb" # "hillclimb", "bestfirst", "a_star"
MOVE_MODE = "cross" # "cross" or "star"


WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (63, 63, 63)

cellWallColor = GREY


gridHeight = int(height / cellSize)
gridWidth = int(width / cellSize)
frame_time = 1000000.0 / frames_per_second


def create_map():
    map = []
    empty_row = []
    for i in range(0, gridHeight):
        map.append(list(empty_row))
    for j in range(0, gridHeight):
        for i in range(0, gridWidth):
            map[j].append({"type": " "})

    return map


def estimate_dist(start_pos, goal_pos):
    if HEURISTIC == "manhattan":
        return abs(goal_pos[0] - start_pos[0]) + abs(goal_pos[1] - start_pos[1])
    elif HEURISTIC == "straight":
        return math.sqrt((goal_pos[0] - start_pos[0])**2 + (goal_pos[1] - start_pos[1])**2)


def print_map(map):
    for row in map:
        print(row)


def get_moves(source_pos):
    move_candidates = []
    if MOVE_MODE == "cross":
        if source_pos[1] > 0:
            move_candidates.append((source_pos[0], source_pos[1]-1))
        if source_pos[1] < gridHeight:
            move_candidates.append((source_pos[0], source_pos[1]+1))
        if source_pos[0] > 0:
            move_candidates.append((source_pos[0]-1, source_pos[1]))
        if source_pos[0] < gridWidth:
            move_candidates.append((source_pos[0]+1, source_pos[1]))
    elif MOVE_MODE == "star":
        move_candidates = []

    return move_candidates


def check_move_legality(map, move_candidates):
    legal_moves = []
    for move in move_candidates:
        if not map[move[1]][move[0]]["type"] == "X":
            legal_moves.append(move)

    return legal_moves


map = create_map()


map[start_pos[1]][start_pos[0]]["type"] = "S"
map[goal_pos[1]][goal_pos[0]]["type"] = "F"

for i in range(0, 6):
    map[1+i][7]["type"] = "X"

print_map(map)

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (window_x, window_y)
pygame.init()
screen = pygame.display.set_mode((width, height))
screen.fill(0)


for i in range(0, gridWidth):
    pygame.draw.line(screen, cellWallColor, (i*cellSize, 0), (i*cellSize, height-1), 1)
    pygame.draw.line(screen, cellWallColor, ((i+1)*cellSize-1, 0), ((i+1)*cellSize-1, height-1), 1)

for i in range(0, gridHeight):
    pygame.draw.line(screen, cellWallColor, (0, i*cellSize), (width-1, i*cellSize), 1)
    pygame.draw.line(screen, cellWallColor, (0, (i+1)*cellSize-1), (width-1, (i+1)*cellSize-1), 1)

for row in range(0, gridHeight):
    for cell in range(0, gridWidth):
        if map[row][cell]["type"] == "S":
            pygame.draw.rect(screen, GREEN, (cell*cellSize+1, row*cellSize+1, cellSize-2, cellSize-2), 0)
        elif map[row][cell]["type"] == "F":
            pygame.draw.rect(screen, RED, (cell*cellSize+1, row*cellSize+1, cellSize-2, cellSize-2), 0)
        elif map[row][cell]["type"] == "X":
            pygame.draw.rect(screen, WHITE, (cell*cellSize+1, row*cellSize+1, cellSize-2, cellSize-2), 0)

pygame.display.flip()

current_pos = start_pos

move_candidates = get_moves(current_pos)
print("move_candidates", move_candidates)

legal_moves = check_move_legality(map, move_candidates)
print("legal_moves", legal_moves)


while True:
    timestamp_frame_start = datetime.now()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

    frame_build_time = (datetime.now() - timestamp_frame_start).microseconds
    if frame_build_time < frame_time:
        time.sleep((frame_time - frame_build_time) / 1000000.0)
    pygame.display.flip()

