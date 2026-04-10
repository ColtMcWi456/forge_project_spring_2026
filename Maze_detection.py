import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
from PIL import Image

def order_points(pts):
    # Initialize a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second top-right, the third bottom-right, and the fourth bottom-left
    rect = np.zeros((4, 2), dtype="float32")
    
    # The top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    # Now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    # Return the ordered coordinates
    return rect

def detect_colored_corners(image_path):
    # 1. Load the image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not load image.")
        return None, None

    original_image = image.copy()

    # 2. Convert to HSV Color Space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 3. Define the Color Range (Tuned for BLUE)
    # You will likely need to adjust these values based on your specific markers and lighting
    lower_blue = np.array([100, 100, 50])
    upper_blue = np.array([130, 255, 255])

    # 4. Create a Mask
    # This creates a black and white image where the blue corners are white, and everything else is black
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Optional: Apply some morphological operations to remove small noise in the mask
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # 5. Find Contours on the Mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort by area and keep the largest 4 (assuming they are our 4 corners)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:4]

    corner_points = []

    # 6. Find the center (centroid) of each colored marker
    for contour in contours:
        # Calculate image moments to find the center
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            corner_points.append([cX, cY])
            
            # Draw a red circle at the center of each detected corner
            cv2.circle(original_image, (cX, cY), 7, (0, 0, 255), -1)

    # 7. Verify we found exactly 4 corners and order them
    if len(corner_points) == 4:
        # Convert to numpy array for easier math
        pts = np.array(corner_points)
        # Order the points: Top-Left, Top-Right, Bottom-Right, Bottom-Left
        ordered_corners = order_points(pts)
        
        # Draw lines connecting the ordered corners to visualize the boundary
        cv2.polylines(original_image, [np.int32(ordered_corners)], True, (0, 255, 0), 2)
        
        print("4 Colored corners detected!")
        return ordered_corners, original_image
    else:
        print(f"Error: Found {len(corner_points)} corners instead of 4. Adjust your color mask.")
        return None, original_image

def calculate_angle(p1,p2):
    """ Calculates the angle between a vector created by two points
    and the x axis"""
    
    # Calculate direction vectors
    v1 = [p2[0]-p1[0],p2[1]-p1[1]]
    v2 = [1,0]

    dot_prod = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = (v1[0]**2+v1[1]**2)**0.5

    cos_theta = dot_prod/(mag1)

    angle_rad = math.acos(cos_theta)
    angle_deg = math.degrees(angle_rad)
    return angle_deg

def normalize_img_angle(img,angle):
    """Takes an image and the angle it is canted off of the origin and rotates
    it so that it is normalized"""
    
    img = Image.open(img)
    
    # Define the angle to rotate (e.g., 45 degrees counter-clockwise)
    angle = -angle
    
    # Rotate the image
    # Setting expand=True resizes the output image to fit the entire rotated image
    rotated_image = img.rotate(angle)
    
    # Save the rotated image
    rotated_image.save("Maze_straightened.png")
    
    # Display the image (optional)
    #rotated_image.show()

def find_chunk_centers(corners,chunk_num):
    """ Find the center of each chunk based on maze corners and number of chunks """
    maze_size = float(corners[1][0] - corners[0][0])
    chunk_size = maze_size/chunk_num

    chunk_centers = [[] for _ in range(chunk_num)]

    for i in range(chunk_num):
        x = corners[0][0] + chunk_size/2
        y = corners[0][1] + chunk_size/2+chunk_size*i
        for j in range(chunk_num):
            x = corners[0][0] + chunk_size/2+chunk_size*j
            chunk_centers[i].append([int(x),int(y)])

    return chunk_centers

def find_chunk_corners(center,corners,chunk_num):
    """ Finds the corners of a chunk from its center, the dimensions of the maze,
    and the number of chunks """
    
    maze_size = float(corners[1][0] - corners[0][0])
    dist = (maze_size/chunk_num)/2

    tl = [int(center[0]-dist),int(center[1]-dist)]
    tr = [int(center[0]+dist),int(center[1]-dist)]
    bl = [int(center[0]-dist),int(center[1]+dist)]
    br = [int(center[0]+dist),int(center[1]+dist)]

    # Top left, top right, bottom left, bottom right
    return [tl,tr,bl,br]

def find_start_end(center_points, image):
    """ Finds the start and end points of the maze based on color of space """
    start = None
    end = None

    for i in range(len(center_points)):
        for j in range(len(center_points[i])):
            if (image[center_points[i][j][1], center_points[i][j][0]][1] > image[center_points[i][j][1], center_points[i][j][0]][2]) and (image[center_points[i][j][1], center_points[i][j][0]][1] > image[center_points[i][j][1], center_points[i][j][0]][0]):
                start = center_points[i][j]
            elif (image[center_points[i][j][0], center_points[i][j][1]][0] > image[center_points[i][j][0], center_points[i][j][1]][1]) and (image[center_points[i][j][0], center_points[i][j][1]][0] > image[center_points[i][j][0], center_points[i][j][1]][2]):
                end = center_points[i][j]
    return start, end

def is_wall(point, center_points, direction, image):
    """ Determines if a point is a wall or path based on the color of the space """
    for i in range(len(center_points)):
        for j in range(len(center_points[i])):
            if center_points[i][j] == point:
                index_i = i
                index_j = j

    if direction == 'up':
        new_index_i -= 1
        new_index_j = index_j

        if new_index_i < 0:
            return True

        distance = abs(center_points[new_index_i][new_index_j][0] - center_points[index_i][index_j][0]) + abs(center_points[new_index_i][new_index_j][1] - center_points[index_i][index_j][1])

        for i in range(distance):
            if image[point[1]-i, point[0]].mean() < 0.5: 
                return True

    elif direction == 'down':
        new_index_i += 1
        new_index_j = index_j

        if new_index_i >= len(center_points):
            return True

        distance = abs(center_points[new_index_i][new_index_j][0] - center_points[index_i][index_j][0]) + abs(center_points[new_index_i][new_index_j][1] - center_points[index_i][index_j][1])

        for i in range(distance):
            if image[point[1]+i, point[0]].mean() < 0.5: 
                return True
            
    elif direction == 'left':
        new_index_i = index_i
        new_index_j -= 1

        if new_index_j < 0:
            return True

        distance = abs(center_points[new_index_i][new_index_j][0] - center_points[index_i][index_j][0]) + abs(center_points[new_index_i][new_index_j][1] - center_points[index_i][index_j][1])

        for i in range(distance):
            if image[point[1], point[0]-i].mean() < 0.5: 
                return True
            
    else: # direction == 'right'
        new_index_i = index_i
        new_index_j += 1

        if new_index_j >= len(center_points[0]):
            return True

        distance = abs(center_points[new_index_i][new_index_j][0] - center_points[index_i][index_j][0]) + abs(center_points[new_index_i][new_index_j][1] - center_points[index_i][index_j][1])

        for i in range(distance):
            if image[point[1], point[0]+i].mean() < 0.5: 
                return True
    
    return False

def BFS(start, end, center_points, image):
    """ Breadth First Search to find the path from start to end """
    queue = [start]
    visited = set()
    parent_map = {}

    while queue:
        current = queue.pop(0)

        if current == end:
            # Reconstruct path
            path = []
            while current in parent_map:
                path.append(current)
                current = parent_map[current]
            path.append(start)
            return path[::-1]  # Return reversed path

        visited.add(tuple(current))

        for direction in ['up', 'down', 'left', 'right']:
            if not is_wall(current, center_points, direction, image):
                # Get the new point based on direction
                if direction == 'up':
                    new_point = [current[0], current[1] - 1]
                elif direction == 'down':
                    new_point = [current[0], current[1] + 1]
                elif direction == 'left':
                    new_point = [current[0] - 1, current[1]]
                else:  # right
                    new_point = [current[0] + 1, current[1]]

                if tuple(new_point) not in visited and new_point not in queue:
                    queue.append(new_point)
                    parent_map[tuple(new_point)] = current

    # Find Path


    return None

# --- Example Usage ---
corners, result_image = detect_colored_corners('maze_marked_up.png')

"""
if corners is not None:
    print("Ordered Corner Coordinates:\n", corners)
    cv2.imshow("Detected Corners", result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
cv2.imwrite('Edged.png', result_image)
"""

angle = calculate_angle(corners[0],corners[1])

normalize_img_angle('maze_marked_up.png',angle) # Need to rotate coordinates too

corners, result_image = detect_colored_corners('Maze_straightened.png')

"""
print("Ordered Corner Coordinates:\n", corners)
cv2.imshow("Detected Corners", result_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('Edged.png', result_image)
"""

center_pts = find_chunk_centers(corners,8)

#corners = find_chunk_corners(center_pts[0],corners,8)

img = mpimg.imread('Maze_straightened.png')
plt.imshow(img)

start, end = find_start_end(center_pts, img)

print("Start:", start)
print("End:", end)

path = BFS(start, end, center_pts, img)

# for i in range(len(center_pts)):
#     for j in range(len(center_pts[i])):
#         plt.scatter(center_pts[i][j][0], center_pts[i][j][1], c='blue', s=40)
plt.scatter(start[0], start[1], c='green', s=100)
plt.scatter(end[0], end[1], c='red', s=100)
for i in range(len(path)):
    plt.scatter(path[i][0], path[i][1], c='yellow', s=50)
plt.show()