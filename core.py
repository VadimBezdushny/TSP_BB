import heapq
import math
import numpy as np
import json

from copy import copy, deepcopy

INF = 10000
BOUND = 1000


class TSPMatrix:
    def __init__(self, input_matrix):
        # TODO throw not square
        self.init_size = input_matrix.shape[0]
        self.matrix = input_matrix.copy()
        self.zero_score = np.zeros(input_matrix.shape)
        self.paths_pool = []
        self.lower_bound = 0
        self.indices = [list(range(0, input_matrix.shape[0])),
                        list(range(0, input_matrix.shape[0]))]
        self.min_cols = []
        self.min_rows = []

    def __enter__(self):
        return self

    def repr_json(self):
        return dict(matrix=self.matrix.tolist(),
                    zero_score=self.zero_scores,
                    paths_pool=self.paths_pool,
                    lower_bound=self.lower_bound,
                    indices=self.indices,
                    min_cols=self.min_cols,
                    min_rows=self.min_rows
                    )

    def reduce_matrix(self):
        min_rows = self.matrix.min(axis=1)
        for i, j in np.ndindex(self.matrix.shape):
            self.matrix[i][j] -= min_rows[i]

        min_cols = self.matrix.min(axis=0)
        for i, j in np.ndindex(self.matrix.shape):
            self.matrix[i][j] -= min_cols[j]

        self.lower_bound += np.sum(min_rows) + np.sum(min_cols)
        self.min_rows = min_rows
        self.min_cols = min_cols

    def calc_zero_score(self):
        self.zero_score = np.zeros(self.matrix.shape)
        for i, j in np.ndindex(self.matrix.shape):
            if self.matrix[i][j] == 0:
                min_in_row = np.min(np.delete(self.matrix[i], j))
                min_in_col = np.min(np.delete(self.matrix[:, j], i))
                self.zero_score[i][j] = min_in_row + min_in_col

    def include_edge(self, ind, jnd):

        self.matrix = np.delete(self.matrix, self.indices[0].index(ind), 0)
        self.matrix = np.delete(self.matrix, self.indices[1].index(jnd), 1)

        self.indices[0].remove(ind)
        self.indices[1].remove(jnd)

        start_of_new_path, end_of_new_path = [ind], [jnd]
        # print(self.paths_pool)
        for path in self.paths_pool:
            if path[-1] == ind:
                start_of_new_path = path[:]

            if path[0] == jnd:
                end_of_new_path = path[:]

        if start_of_new_path in self.paths_pool:
            self.paths_pool.remove(start_of_new_path)

        if end_of_new_path in self.paths_pool:
            self.paths_pool.remove(end_of_new_path)

        start_of_new_path.extend(end_of_new_path)
        self.paths_pool.append(start_of_new_path[:])
        if self.matrix.shape[0] > 2:
            self.matrix[self.indices[0].index(start_of_new_path[-1])][self.indices[1].index(start_of_new_path[0])] = INF

    def exclude_edge(self, ind, jnd):
        self.matrix[self.indices[0].index(ind)][self.indices[1].index(jnd)] = INF


class BBNode:

    def __init__(self, tsp_matrix, index):
        self.tsp_matrix = tsp_matrix
        self.index = index
        self.priority = 0

    def __lt__(self, other):
        return \
            (self.priority < other.priority if not self.priority == other.priority
             else self.index < other.index)


    def is_final(self):
        return len(self.tsp_matrix.paths_pool) == 1 and \
               len(self.tsp_matrix.paths_pool[0]) == self.tsp_matrix.init_size

    def calc_split_edge(self):
        # TODO: remove to TSPMatrix
        self.tsp_matrix.reduce_matrix()
        self.tsp_matrix.calc_zero_score()

        indcs = self.tsp_matrix.indices
        res = max([(self.tsp_matrix.zero_score[i][j], indcs[0][i], indcs[1][j])
                   for i, j in np.ndindex(self.tsp_matrix.matrix.shape)
                   if indcs[0][i] != indcs[1][j] and self.tsp_matrix.matrix[i][j] <= BOUND])
        print("lasdasdasd", res, res[1:])
        return res[1:]

    def get_path(self):
        if self.is_final():
            return self.tsp_matrix.paths_pool[0]

    def include_node(self, split_edge):
        self.tsp_matrix.include_edge(*split_edge)
        self.tsp_matrix.reduce_matrix()
        self.priority = self.tsp_matrix.lower_bound
        if self.priority == math.nan:
            self.priority = INF  # TODO
        return self

    def exclude_node(self, split_edge):
        self.tsp_matrix.exclude_edge(*split_edge)
        self.tsp_matrix.reduce_matrix()
        self.priority = self.tsp_matrix.lower_bound
        return self


class TSPSolver:
    def __init__(self, m):
        self.m = TSPMatrix(deepcopy(m))
        self.nodes_pool = None
        self.start_matrix = deepcopy(m)

    def eval_path(self, path):
        ans = 0
        # print(path)
        for i, _ in enumerate(path):
            # print(self.start_matrix[path[i - 1]][path[i]])
            ans += self.start_matrix[path[i - 1]][path[i]]
        return ans

    def run(self):
        self.nodes_pool = []

        main_node = BBNode(self.m, 1)

        best_len = INF * INF
        best_path = list(range(self.m.matrix.shape[0]))

        counter = 0
        heapq.heappush(self.nodes_pool, main_node)
        while len(self.nodes_pool) > 0 and counter <= 50:

            node = heapq.heappop(self.nodes_pool)
            if node.priority > best_len:
                break

            if node.is_final():
                path = node.get_path()
                best_len = self.eval_path(best_path)
                path_len = self.eval_path(path)
                if best_len > path_len:
                    best_path = path
                    best_len = path_len
            else:

                split_edge = node.calc_split_edge()
                print(split_edge, node.tsp_matrix.matrix, node.tsp_matrix.indices,
                      node.tsp_matrix.paths_pool, node.priority, sep="\n")
                print("#" * 40)

                InNode = deepcopy(node).include_node(split_edge)
                InNode.index = 2 * node.index

                ExNode = deepcopy(node).exclude_node(split_edge)
                ExNode.index = 2 * node.index + 1

                heapq.heappush(self.nodes_pool, InNode)
                heapq.heappush(self.nodes_pool, ExNode)

                counter += 1

        print(best_path, self.eval_path(best_path))


def run():
    a = np.array([[INF, 90, 80, 40, 100],
                  [60, INF, 40, 50, 70],
                  [50, 30, INF, 60, 20],
                  [10, 70, 20, INF, 50],
                  [20, 40, 50, 20, INF]])

    b = np.array([[INF, 1, 1, 1],
                  [1, INF, 1, 1],
                  [1, 1, INF, 1],
                  [1, 1, 1, INF]])

    c = np.array([[10000, 0, 0, 0, 1, 0],
                  [0, 10000, 1, 0, 0, 2],
                  [0, 0, 10000, 1, 0, 0],
                  [1, 0, 0, 10000, 2, 0],
                  [0, 0, 0, 0, 10000, 1],
                  [0, 0, 0, 0, 0, 10000], ])
    TSPSolver(b).run()
