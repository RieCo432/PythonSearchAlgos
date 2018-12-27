import math
import pygame
import os
from datetime import datetime
import time
import json
from sys import argv


window_x, window_y = 5, 32
# width, height = 1600, 900
# cellSize = 100
moves_per_second = 10
fast_speed = 200
real_speed = moves_per_second

# start_pos = (0, 3)
# goal_pos = (15, 0)

HEURISTIC = "manhattan"  # "manhattan" or "straight"
SEARCH_ALGO = "a_star"  # "hillclimb", "bestfirst", "a_star"
MOVE_MODE = "cross"  # "cross" or "star"


WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (63, 63, 63)
DARK_GREY = (31, 31, 31)
YELLOW = (200, 255, 0)
BLACK = (0, 0, 0)

live_color = DARK_GREY

cellWallColor = GREY

frame_time = 1000000.0 / moves_per_second


def create_map(gridWidth, gridHeight):
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
        # Up Down Left Right
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
        # print("move", move)
        if not map[move[1]][move[0]]["type"] == "X":
            legal_moves.append(move)

    return legal_moves


def a_star(map, current_pos, open_list, closed_list, legal_moves):
    # print("open_list", open_list)
    # print("closed_list", closed_list)
    # print("legal_moves", legal_moves)

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
        # print("cell", cell)
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
    # print("best_H (current)", best_H)
    best_H_cell = current_pos
    for cell in legal_moves:
        # print("cell", cell)
        new_H = estimate_dist(cell, goal_pos)
        # print("new_H", new_H)
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

    # print("closed_list", closed_list)
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
        # print("cell", cell)
        if cell not in closed_list:
            map[cell[1]][cell[0]]["parent"] = current_pos
            # print("new_H", map[cell[1]][cell[0]]["H"])
            if map[cell[1]][cell[0]]["H"] < best_H or best_H < 0:
                best_H = map[cell[1]][cell[0]]["H"]
                best_H_cell = cell
                dead_end = False

    if dead_end:
        signal_dead_end = True
        global live_color
        if live_color[0] <= 193 and live_color[1] <= 193 and live_color[2] <= 193:
            live_color = (live_color[0]+31, live_color[1]+31, live_color[2]+31)
        else:
            live_color = DARK_GREY
        # print("open_list", open_list)
        for cell in open_list:
            if cell not in closed_list:
                # print("cell", cell)
                if map[cell[1]][cell[0]]["H"] < best_H or best_H < 0:
                    best_H = map[cell[1]][cell[0]]["H"]
                    best_H_cell = cell
                    # print("best_H", best_H)
                    # print("best_H_cell", best_H_cell)
                    dead_end = False

    closed_list.append(best_H_cell)
    if len(open_list) > 0:
        open_list.remove(best_H_cell)
    else:
        dead_end = True
        signal_dead_end = True

    return map, best_H_cell, open_list, closed_list, dead_end, signal_dead_end, current_pos


def export_map_structure(map):
    current_type = " "
    current_type_number = 0
    number_list = []
    for row in map:
        for cell in row:
            new_type = cell["type"]
            if new_type == "S" or new_type == "F":
                new_type = " "
            if new_type == current_type:
                current_type_number += 1
            else:
                number_list.append(current_type_number)
                current_type = new_type
                current_type_number = 1

    number_list.append(current_type_number)

    map_compressed_dict = {"wall_info": number_list, "gridWidth": gridWidth, "gridHeight": gridHeight,
                           "cellSize": cellSize, "windowHeight": height, "windowWidth": width, "startPos": start_pos,
                           "goalPos": goal_pos}

    if len(argv) > 1:
        with open(argv[1], "w") as fout:
            json.dump(map_compressed_dict, fout)
    else:
        with open("new_map.json", "w") as fout:
            json.dump(map_compressed_dict, fout)


def import_map_structure(map_compressed_dict):
    gridWidth = map_compressed_dict["gridWidth"]
    gridHeight = map_compressed_dict["gridHeight"]
    start_pos_list = map_compressed_dict["startPos"]
    goal_pos_list = map_compressed_dict["goalPos"]
    windowWidth = map_compressed_dict["windowWidth"]
    windowHeight = map_compressed_dict["windowHeight"]
    cellSize = map_compressed_dict["cellSize"]
    wall_info = map_compressed_dict["wall_info"]

    start_pos = (start_pos_list[0], start_pos_list[1])
    goal_pos = (goal_pos_list[0], goal_pos_list[1])

    new_map = create_map(gridWidth, gridHeight)
    new_map[start_pos[1]][start_pos[0]]["type"] = "S"
    new_map[goal_pos[1]][goal_pos[0]]["type"] = "F"

    current_type = False
    wall_info_index = 0
    for row in new_map:
        for cell in row:
            if wall_info[wall_info_index] == 0:
                current_type = not current_type
                wall_info_index += 1
            if current_type:
                cell["type"] = "X"
            wall_info[wall_info_index] -= 1

    # print_map(new_map)

    return gridWidth, gridHeight, start_pos, goal_pos, windowWidth, windowHeight, cellSize, new_map


def reset_map_vars(map):
    for row in map:
        for cell in row:
            cell.pop("parent", None)
            cell.pop("G", None)
            cell.pop("H", None)
            cell.pop("F", None)

    return map

# game_map = create_map(gridWidth, gridHeight)
#
# #Map feature generation. To be implemented differently
# game_map[start_pos[1]][start_pos[0]]["type"] = "S"
# game_map[goal_pos[1]][goal_pos[0]]["type"] = "F"
# for i in range(2, 15):
#     game_map[7][i]["type"] = "X"
# for i in range(0, 4):
#     game_map[i][1]["type"] = "X"
# for i in range(0, 4):
#     game_map[i][2]["type"] = "X"
# for i in range(5, 7):
#     game_map[i][2]["type"] = "X"
# for i in range(0, 6):
#     game_map[i][4]["type"] = "X"
# for i in range(1, 7):
#     game_map[i][6]["type"] = "X"
# for i in range(0, 6):
#     game_map[i][8]["type"] = "X"
# for i in range(1, 7):
#     game_map[i][10]["type"] = "X"
# for i in range(0, 6):
#     game_map[i][12]["type"] = "X"
# for i in range(1, 7):
#     game_map[i][14]["type"] = "X"
#
# # End of map feature generation
#
# print_map(game_map)


# final_map_dict = export_map_structure(game_map)
# import_map_structure(final_map_dict)

# Default values
height = 900
width = 1600
gridWidth = 16
gridHeight = 9
cellSize = 100
start_pos = (0, 0)
goal_pos = (gridWidth - 1, gridHeight - 1)
current_pos = start_pos
game_map = create_map(gridWidth, gridHeight)

if len(argv) > 1:
    filename = argv[1]
    if filename != "":
        try:
            fin = open(filename, "r")
            map_dict = json.load(fin)
            gridWidth, gridHeight, start_pos, goal_pos, width, height, cellSize, game_map = import_map_structure(
                map_dict)
        except FileNotFoundError:
            gridWidth = int(input("Enter number of horizontal cells: "))
            gridHeight = int(input("Enter number of vertical cells: "))
            cellSize = int(input("Enter cell size in pixels: "))
            width = gridWidth * cellSize
            height = gridHeight * cellSize
            game_map = create_map(gridWidth, gridHeight)
            start_pos = (0, 0)
            goal_pos = (gridWidth-1, gridHeight-1)

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (window_x, window_y)
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Search algo: %s        Moves/Second: %s" %(SEARCH_ALGO, moves_per_second))
screen.fill(0)


def draw_map(map, gridWidth, gridHeight, cellSize, width, height):
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


search_path = False
arrived_at_goal = False
dead_end = False
signal_dead_end = False
path_traced = False
set_new_start = False
set_new_goal = False
trace_new_wall = False
open_list = []
closed_list = []
new_wall_blocks_list = []
dead_end_pos = (0, 0)

# print_map(game_map)

draw_map(game_map, gridWidth, gridHeight, cellSize, width, height)

while True:
    timestamp_frame_start = datetime.now()

    if not search_path:
        current_pos = start_pos
        # A-Star init
        open_list = []
        closed_list = []
        game_map[start_pos[1]][start_pos[0]]["G"] = 0

    if not arrived_at_goal and not dead_end:

        if search_path:
            # print("current_pos", current_pos)

            move_candidates = get_moves(current_pos)
            # print("move_candidates", move_candidates)

            legal_moves = check_move_legality(game_map, move_candidates)
            # print("legal_moves", legal_moves)

            if SEARCH_ALGO == "a_star":
                game_map, current_pos, open_list, closed_list, dead_end = a_star(game_map, current_pos, open_list,
                                                                                 closed_list,
                                                                                 legal_moves)
            elif SEARCH_ALGO == "hillclimb":
                game_map, current_pos, dead_end, signal_dead_end, dead_end_pos = hillclimb(game_map, current_pos,
                                                                                           legal_moves)
            elif SEARCH_ALGO == "bestfirst":
                game_map, current_pos, open_list, closed_list, dead_end, signal_dead_end, dead_end_pos = bestfirst(
                    game_map,
                    current_pos,
                    open_list,
                    closed_list,
                    legal_moves)

            # print("current_pos", current_pos, "goal_pos", goal_pos)

            if current_pos == goal_pos:
                arrived_at_goal = True
                # print("arrived")
            else:
                pygame.draw.rect(screen, live_color,
                                 (current_pos[0] * cellSize + 1, current_pos[1] * cellSize + 1, cellSize - 2,
                                  cellSize - 2), 0)
                if signal_dead_end:
                    pygame.draw.aaline(screen, RED, (dead_end_pos[0] * cellSize + 1, dead_end_pos[1] * cellSize + 1),
                                       (dead_end_pos[0] * cellSize + cellSize - 1,
                                        dead_end_pos[1] * cellSize + cellSize - 1), 2)
                    pygame.draw.aaline(screen, RED,
                                       (dead_end_pos[0] * cellSize + 1, dead_end_pos[1] * cellSize + cellSize - 1),
                                       (dead_end_pos[0] * cellSize + cellSize - 1, dead_end_pos[1] * cellSize + 1), 2)
                    signal_dead_end = False

    if arrived_at_goal or dead_end:
        # print("tracing path")
        # print_map(game_map)
        search_path = False
        if not dead_end:
            parent = goal_pos
            total_path = []
        else:
            parent = current_pos
            total_path = [current_pos]

        while True:
            # print(parent, " <-- ", game_map[parent[1]][parent[0]]["parent"])
            parent = game_map[parent[1]][parent[0]]["parent"]
            if parent == start_pos:
                break
            else:
                total_path.append(parent)

        # print("total_path", total_path)

        for path_cell in total_path:
            pygame.draw.rect(screen, BLUE,
                             (path_cell[0] * cellSize + 1, path_cell[1] * cellSize + 1, cellSize - 2, cellSize - 2), 0)
            pygame.display.flip()
            path_traced = True

        # Reset vars
        open_list = []
        current_pos = start_pos
        closed_list = []
        dead_end = False
        arrived_at_goal = False
        if path_traced:
            game_map = reset_map_vars(game_map)
            path_traced = False
            # print("resetting map")
            # print_map(game_map)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                draw_map(game_map, gridWidth, gridHeight, cellSize, width, height)
                live_color = DARK_GREY
                search_path = True
            elif event.key == pygame.K_RETURN:
                export_map_structure(game_map)
            elif event.key == pygame.K_1:
                SEARCH_ALGO = "hillclimb"
            elif event.key == pygame.K_2:
                SEARCH_ALGO = "bestfirst"
            elif event.key == pygame.K_3:
                SEARCH_ALGO = "a_star"
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_UP:
                if moves_per_second >= 10:
                    moves_per_second += 10
                else:
                    moves_per_second += 1
            elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS or event.key == pygame.K_DOWN:
                if moves_per_second > 10:
                    moves_per_second -= 10
                elif moves_per_second > 1:
                    moves_per_second -= 1
            if event.key == pygame.K_s:
                set_new_start = True
            elif event.key == pygame.K_f:
                set_new_goal = True

            frame_time = 1000000.0 / moves_per_second

            pygame.display.set_caption("Search algo: %s        Moves/Second: %s" % (SEARCH_ALGO, moves_per_second))

        if event.type == pygame.MOUSEBUTTONDOWN:
            pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()

            if pressed1 and set_new_start:
                game_map[start_pos[1]][start_pos[0]]["type"] = " "
                start_pos = pygame.mouse.get_pos()
                start_pos = (start_pos[0] // cellSize, start_pos[1] // cellSize)
                game_map[start_pos[1]][start_pos[0]]["type"] = "S"
                set_new_start = False
            elif pressed1 and set_new_goal:
                game_map[goal_pos[1]][goal_pos[0]]["type"] = " "
                goal_pos = pygame.mouse.get_pos()
                goal_pos = (goal_pos[0] // cellSize, goal_pos[1] // cellSize)
                game_map[goal_pos[1]][goal_pos[0]]["type"] = "F"
                set_new_goal = False
            elif pressed1:
                trace_new_wall = True
                new_wall_blocks_list = []

            draw_map(game_map, gridWidth, gridHeight, cellSize, width, height)

        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

    pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()

    if pressed1 and trace_new_wall:
        # print("tracing mouse")
        wall_toggle_pos = pygame.mouse.get_pos()
        wall_toggle_pos = (wall_toggle_pos[0] // cellSize, wall_toggle_pos[1] // cellSize)
        if wall_toggle_pos not in new_wall_blocks_list:
            new_wall_blocks_list.append(wall_toggle_pos)
        # print("new_wall_blocks_list", new_wall_blocks_list)
        real_speed = moves_per_second
        moves_per_second = fast_speed

    if trace_new_wall and not pressed1:
        trace_new_wall = False
        for block in new_wall_blocks_list:
            if game_map[block[1]][block[0]]["type"] == " ":
                game_map[block[1]][block[0]]["type"] = "X"
            elif game_map[block[1]][block[0]]["type"] == "X":
                game_map[block[1]][block[0]]["type"] = " "

        moves_per_second = real_speed
        frame_time = 1000000.0 / moves_per_second
        draw_map(game_map, gridWidth, gridHeight, cellSize, width, height)

    frame_build_time = (datetime.now() - timestamp_frame_start).microseconds
    if frame_build_time < frame_time:
        time.sleep((frame_time - frame_build_time) / 1000000.0)
    pygame.display.flip()
