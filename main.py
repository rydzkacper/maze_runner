import functools
from pathlib import Path
from queue import PriorityQueue
from typing import List

import numpy as np
from PIL import Image, ImageDraw
import time

from maze_analyser import Node, nodes_from_maze


@functools.total_ordering
class PriorityItem:


    def __init__(self, priority, item):
        self.priority = priority
        self.item = item

    def __eq__(self, other):
        return self.priority == other.priority

    def __lt__(self, other):
        return self.priority < other.priority


def run_dijkstra_algorithm(start_node, nodes) -> None:

    queue = PriorityQueue()

    start_node.distance = 0

    current_node = None
    shortest_path = [start_node]

    queue.put(PriorityItem(0, start_node))

    while not queue.empty():

        current_node = queue.get().item

        for node, weight in current_node.adjacency_list.items():
            if node not in shortest_path:
                if node.distance and current_node.distance + weight >= node.distance:
                    continue
                node.distance = current_node.distance + weight
                node.previous = current_node
                queue.put(PriorityItem(node.distance, node))


def get_path_from_node(node: Node) -> List[Node]:

    path = []
    while node:
        path.append(node)
        node = node.previous
    return path


def colour_path(image, path) -> None:

    start_node = path[-1]
    finish_node = path[0]

    pixels = image.load()

    red_fade = np.linspace(255, 0, finish_node.distance + 1).astype(int)
    blue_fade = np.linspace(0, 255, finish_node.distance + 1).astype(int)
    step = 0

    for node1, node2 in zip(path[:-1], path[1:]):
        x1, y1 = node1.coords
        x2, y2 = node2.coords
        distance = node1.distance - node2.distance
        x_change = np.linspace(x1, x2, distance + 1)[:-1]
        y_change = np.linspace(y1, y2, distance + 1)[:-1]

        for path_x, path_y in zip(x_change, y_change):
            pixels[path_x, path_y] = (red_fade[step], blue_fade[step], 0)
            step += 1

    pixels[start_node.coords] = (red_fade[step], blue_fade[step], 0)


def solve_image(file_path) -> None:

    import os
    image = Image.open(file_path)
    start_node, finish_node, nodes = nodes_from_maze(image)
    run_dijkstra_algorithm(start_node, nodes)
    path = get_path_from_node(finish_node)
    colour_path(image, path)
    image.save(os.path.join(os.path.dirname(file_path), "solved_%s" % os.path.basename(file_path)))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("maze", nargs="?", type=str, default='your image location here')
    args = parser.parse_args()

    start = time.time()
    solve_image(args.maze)
    end = time.time() - start
    print('Time taken:', end)