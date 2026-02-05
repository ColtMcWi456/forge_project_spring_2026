class PathPlanner:
    """
    Handles:
    - Path simplification
    - Converting path into movement commands
    """

    def __init__(self, cm_per_cell=1.0):
        self.cm_per_cell = cm_per_cell

    def simplify_path(self, path):
        """
        Reduce path into fewer points.
        (example: remove redundant straight-line steps)
        """
        pass

    def path_to_commands(self, path):
        """
        Convert simplified path into robot commands.

        Example output:
            [("F", 10), ("R", 90), ("F", 20)]

        Returns:
            commands: list of tuples
        """
        pass
    