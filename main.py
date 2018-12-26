import math
import pygame
import os
from datetime import datetime
import time


window_x, window_y = 5, 32
width, height = 1600, 900
cellSize = 100
frames_per_second = 10

start_pos = (0, 3)
goal_pos = (15, 0)

HEURISTIC = "manhattan" # "manhattan" or "straight"
SEARCH_ALGO = "a_star" # "hillclimb", "bestfirst", "a_star"
MOVE_MODE = "cross" # "cross" or "star"


WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (63, 63, 63)
DARK_GREY = (31, 31, 31)
YELLOW = (200, 255, 0)

live_color = DARK_GREY

cellWallColor = GREY


gridHeight = int(height / cellSize)
gridWidth = int(width / cellSize)
frame_time = 1000000.0 / frames_per_second


def create_map():
    new_map = []
    empty_row = []
    for i in range(0, gridHeight):
        new_map.append(list(empty_row))
    for j in range(0, gridHeight):
        for i in range(0, gridWidth):
            new_map[j].append({"type": " "})

    return new_map


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
        if source_pos[1] < gridHeight-1:
            move_candidates.append((source_pos[0], source_pos[1]+1))
        if source_pos[0] > 0:
            move_candidates.append((source_pos[0]-1, source_pos[1]))
        if source_pos[0] < gridWidth-1:
            move_candidates.append((source_pos[0]+1, source_pos[1]))
    elif MOVE_MODE == "star":
        #Up Down Left Right
        if source_pos[1] > 0:
            move_candidates.append((source_pos[0], source_pos[1]-1))
        if source_pos[1] < gridHeight-1:
            move_candidates.append((source_pos[0], source_pos[1]+1))
        if source_pos[0] > 0:
            move_candidates.append((source_pos[0]-1, source_pos[1]))
        if source_pos[0] < gridWidth-1:
            move_candidates.append((source_pos[0]+1, source_pos[1]))

        # Up-Left Up-Right Down-Left Down-Right
        if source_pos[1] > 0 and source_pos[0] > 0:
            move_candidates.append((source_pos[0]-1, source_pos[1]-1))
        if source_pos[1] > 0 and source_pos[0] < gridWidth-1:
            move_candidates.append((source_pos[0]+1, source_pos[1]-1))
        if source_pos[1] < gridHeight-1 and source_pos[0] > 0:
            move_candidates.append((source_pos[0]-1, source_pos[1]+1))
        if source_pos[1] < gridHeight-1 and source_pos[0] < gridWidth-1:
            move_candidates.append((source_pos[0]+1, source_pos[1]+1))

    return move_candidates


def check_move_legality(map, move_candidates):
    legal_moves = []
    for move in move_candidates:
        #print("move", move)
        if not map[move[1]][move[0]]["type"] == "X":
            legal_moves.append(move)

    return legal_moves


def a_star(map, current_pos, open_list, closed_list, legal_moves):
    #print("open_list", open_list)
    #print("closed_list", closed_list)
    #print("legal_moves", legal_moves)

    open_list.append(current_pos)

    dead_end = False

    for cell in legal_moves:
        if (cell not in open_list) and (cell not in closed_list):
            open_list.append(cell)

    if current_pos in open_list:
        open_list.remove(current_pos)
        closed_list.append(current_pos)

    minimum_F = -1
    minimum_F_cell = current_pos

    for cell in legal_moves:
        #print("cell", cell)
        if cell in open_list:
            map[cell[1]][cell[0]]["H"] = estimate_dist(cell, goal_pos)
            new_G = map[current_pos[1]][current_pos[0]]["G"] + cellSize
            new_F = map[cell[1]][cell[0]]["H"] + new_G

            if ("G" in map[cell[1]][cell[0]].keys()) and (new_G < map[cell[1]][cell[0]]["G"]):
                map[cell[1]][cell[0]]["G"] = new_G
                map[cell[1]][cell[0]]["F"] = new_F
                map[cell[1]][cell[0]]["parent"] = current_pos
            elif ("G" not in map[cell[1]][cell[0]].keys()) or ("F" not in map[cell[1]][cell[0]].keys()):
                map[cell[1]][cell[0]]["G"] = new_G
                map[cell[1]][cell[0]]["F"] = new_F
                map[cell[1]][cell[0]]["parent"] = current_pos

    for cell in open_list:
        if (map[cell[1]][cell[0]]["F"] < minimum_F) or (minimum_F < 0):
            minimum_F = map[cell[1]][cell[0]]["F"]
            minimum_F_cell = cell

    current_pos = minimum_F_cell
    if len(open_list) > 0:
        open_list.remove(current_pos)
        closed_list.append(current_pos)
    else:
        dead_end = True

    return map, current_pos, open_list, closed_list, dead_end


def hillclimb(map, current_pos, legal_moves):

    dead_end = False
    signal_dead_end = False

    best_H = estimate_dist(current_pos, goal_pos)
    #print("best_H (current)", best_H)
    best_H_cell = current_pos
    for cell in legal_moves:
        #print("cell", cell)
        new_H = estimate_dist(cell, goal_pos)
        #print("new_H", new_H)
        if (new_H < best_H) or (best_H < 0):
            best_H = new_H
            best_H_cell = cell
    if best_H_cell == current_pos:
        dead_end = True
        signal_dead_end = True
    else:
        map[best_H_cell[1]][best_H_cell[0]]["parent"] = current_pos

    return map, best_H_cell, dead_end, signal_dead_end, current_pos


def bestfirst(map, current_pos, open_list, closed_list, legal_moves):

    #print("closed_list", closed_list)
    closed_list.append(current_pos)

    for cell in legal_moves:
        if (cell not in open_list) and (cell not in closed_list):
            open_list.append(cell)

    for cell in open_list:
        map[cell[1]][cell[0]]["H"] = estimate_dist(cell, goal_pos)

    best_H = -1
    best_H_cell = current_pos
    dead_end = True
    signal_dead_end = False

    for cell in legal_moves:
        #print("cell", cell)
        if cell not in closed_list:
            map[cell[1]][cell[0]]["parent"] = current_pos
            #print("new_H", map[cell[1]][cell[0]]["H"])
            if map[cell[1]][cell[0]]["H"] < best_H or best_H < 0:
                best_H = map[cell[1]][cell[0]]["H"]
                best_H_cell = cell
                dead_end = False

    if dead_end:
        signal_dead_end = True
        global live_color
        live_color = (live_color[0]+31, live_color[1]+31, live_color[2]+31)
        #print("open_list", open_list)
        for cell in open_list:
            if cell not in closed_list:
                #print("cell", cell)
                if map[cell[1]][cell[0]]["H"] < best_H or best_H < 0:
                    best_H = map[cell[1]][cell[0]]["H"]
                    best_H_cell = cell
                    #print("best_H", best_H)
                    #print("best_H_cell", best_H_cell)
                    dead_end = False

    closed_list.append(best_H_cell)
    if len(open_list) > 0:
        open_list.remove(best_H_cell)
    else:
        dead_end = True
        signal_dead_end = True

    return map, best_H_cell, open_list, closed_list, dead_end, signal_dead_end, current_pos


game_map = create_map()

# Map feature generation. To be implemented differently
game_map[start_pos[1]][start_pos[0]]["type"] = "S"
game_map[goal_pos[1]][goal_pos[0]]["type"] = "F"
for i in range(2, 15):
    game_map[7][i]["type"] = "X"
for i in range(0, 4):
    game_map[i][1]["type"] = "X"
for i in range(0, 4):
    game_map[i][2]["type"] = "X"
for i in range(5, 7):
    game_map[i][2]["type"] = "X"
for i in range(0, 6):
    game_map[i][4]["type"] = "X"
for i in range(1, 7):
    game_map[i][6]["type"] = "X"
for i in range(0, 6):
    game_map[i][8]["type"] = "X"
for i in range(1, 7):
    game_map[i][10]["type"] = "X"
for i in range(0, 6):
    game_map[i][12]["type"] = "X"
for i in range(1, 7):
    game_map[i][14]["type"] = "X"

# End of map feature generation

print_map(game_map)

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
        if game_map[row][cell]["type"] == "S":
            pygame.draw.rect(screen, GREEN, (cell*cellSize+1, row*cellSize+1, cellSize-2, cellSize-2), 0)
        elif game_map[row][cell]["type"] == "F":
            pygame.draw.rect(screen, RED, (cell*cellSize+1, row*cellSize+1, cellSize-2, cellSize-2), 0)
        elif game_map[row][cell]["type"] == "X":
            pygame.draw.rect(screen, WHITE, (cell*cellSize+1, row*cellSize+1, cellSize-2, cellSize-2), 0)

pygame.display.flip()

current_pos = start_pos

# A-Star init
open_list = []
closed_list = []
game_map[start_pos[1]][start_pos[0]]["G"] = 0

arrived_at_goal = False
dead_end = False
signal_dead_end = False

while not arrived_at_goal and not dead_end:
    timestamp_frame_start = datetime.now()

    #print("current_pos", current_pos)

    move_candidates = get_moves(current_pos)
    #print("move_candidates", move_candidates)

    legal_moves = check_move_legality(game_map, move_candidates)
    #print("legal_moves", legal_moves)

    if SEARCH_ALGO == "a_star":
        game_map, current_pos, open_list, closed_list, dead_end = a_star(game_map, current_pos, open_list, closed_list,
                                                               legal_moves)
    elif SEARCH_ALGO == "hillclimb":
        game_map, current_pos, dead_end, signal_dead_end, dead_end_pos = hillclimb(game_map, current_pos, legal_moves)
    elif SEARCH_ALGO == "bestfirst":
        game_map, current_pos, open_list, closed_list, dead_end, signal_dead_end, dead_end_pos = bestfirst(game_map,
                                                                                                           current_pos,
                                                                                                           open_list,
                                                                                                           closed_list,
                                                                                                           legal_moves)


    if current_pos == goal_pos:
        arrived_at_goal = True
        #print("arrived")
    else:
        pygame.draw.rect(screen, live_color,
                         (current_pos[0] * cellSize + 1, current_pos[1] * cellSize + 1, cellSize - 2, cellSize - 2), 0)
        if signal_dead_end:
            pygame.draw.aaline(screen, RED, (dead_end_pos[0] * cellSize + 1, dead_end_pos[1] * cellSize + 1),
                               (dead_end_pos[0] * cellSize + cellSize-1, dead_end_pos[1] * cellSize + cellSize-1), 2)
            pygame.draw.aaline(screen, RED, (dead_end_pos[0] * cellSize + 1, dead_end_pos[1] * cellSize + cellSize-1),
                               (dead_end_pos[0] * cellSize + cellSize-1, dead_end_pos[1] * cellSize + 1), 2)
            signal_dead_end = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

    frame_build_time = (datetime.now() - timestamp_frame_start).microseconds
    if frame_build_time < frame_time:
        time.sleep((frame_time - frame_build_time) / 1000000.0)
    pygame.display.flip()

if not dead_end:
    parent = goal_pos
    total_path = []
else:
    parent = current_pos
    total_path = [current_pos]

while True:
    print(parent, " <-- ", game_map[parent[1]][parent[0]]["parent"])
    parent = game_map[parent[1]][parent[0]]["parent"]
    if parent == start_pos:
        break
    else:
        total_path.append(parent)

print("total_path", total_path)

for path_cell in total_path:
    pygame.draw.rect(screen, BLUE, (path_cell[0] * cellSize + 1, path_cell[1] * cellSize + 1, cellSize - 2, cellSize - 2), 0)
    pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

