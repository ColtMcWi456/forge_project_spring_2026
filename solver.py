class MazeSolver:
    """
    Handles:
    - Maze solving algorithms (BFS, DFS, A*)
    - Returns a valid path through the maze
    """

    def __init__(self, grid):
        self._grid = grid
        self._start = self._find_start(grid)
        self.end = self._find_end(grid)

    def _find_end(self, grid):
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == 'E':
                    return (x, y)
        return None

    def _find_start(self, grid):
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == 'S':
                    return (x, y)
        return None

    def solve(self):
        return self.bfs(self._grid, self._start, self.end)

    def bfs(self, grid, start, end):
        from collections import deque

        queue = deque([start])
        visited = set()
        visited.add(start)
        parent = {start: None}

        while queue:
            current = queue.popleft()

            if current == end:
                return self.reconstruct_path(parent, start, end)

            for neighbor in self.get_neighbors(grid, current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        return None
    
    def get_neighbors(self, grid, position):
        x, y = position
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < len(grid[0]) and 0 <= new_y < len(grid):
                if grid[new_y][new_x] != 1:
                    neighbors.append((new_x, new_y))

        return neighbors
    
    def reconstruct_path(self, parent, start, goal):
        path = []
        current = goal

        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse()
        return path