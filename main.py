import config
from vision import CameraVision
from solver import MazeSolver
from planner import PathPlanner
from robot import ArduinoRobot


def main():
    # -----------------------
    # 1. Capture maze image
    # -----------------------
    vision = CameraVision(config.CAMERA_ID, config.DEBUG_FOLDER)
    vision.connect()

    frame = vision.capture_frame()
    processed = vision.preprocess(frame)
    segmented = vision.segment_maze(processed)

    grid = vision.extract_grid(segmented, config.GRID_WIDTH, config.GRID_HEIGHT)
    vision.release()

    # -----------------------
    # 2. Solve maze
    # -----------------------
    solver = MazeSolver()
    path = solver.solve(grid, config.START, config.GOAL, method="bfs")

    # -----------------------
    # 3. Convert path to commands
    # -----------------------
    planner = PathPlanner(cm_per_cell=config.CM_PER_CELL)
    simplified_path = planner.simplify_path(path)
    commands = planner.path_to_commands(simplified_path)

    # -----------------------
    # 4. Send commands to robot
    # -----------------------
    robot = ArduinoRobot(config.ARDUINO_PORT, config.BAUDRATE)
    robot.connect()
    robot.send_commands(commands)
    robot.close()


if __name__ == "__main__":
    main()