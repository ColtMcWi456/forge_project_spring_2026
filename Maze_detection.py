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

# --- Example Usage ---
corners, result_image = detect_colored_corners('Maze_tilt.png')

if corners is not None:
    print("Ordered Corner Coordinates:\n", corners)
    cv2.imshow("Detected Corners", result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
cv2.imwrite('Edged.png', result_image)




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

angle = calculate_angle(corners[0],corners[1])

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
    rotated_image.show()

normalize_img_angle('Maze_tilt.png',angle) # Need to rotate coordinates too

corners, result_image = detect_colored_corners('Maze_straightened.png')

print("Ordered Corner Coordinates:\n", corners)
cv2.imshow("Detected Corners", result_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('Edged.png', result_image)



def find_chunk_centers(corners,chunk_num):
    """ Find the center of each chunk based on maze corners and number of chunks """
    maze_size = float(corners[1][0] - corners[0][0])
    chunk_size = maze_size/chunk_num

    chunk_centers = []

    for i in range(chunk_num):
        x = corners[0][0] + chunk_size/2
        y = corners[0][1] + chunk_size/2+chunk_size*i
        for j in range(chunk_num):
            x = corners[0][0] + chunk_size/2+chunk_size*j
            chunk_centers.append([float(x),float(y)])

    return chunk_centers

def find_chunk_corners(center,corners,chunk_num):
    """ Finds the corners of a chunk from its center, the dimensions of the maze,
    and the number of chunks """
    
    maze_size = float(corners[1][0] - corners[0][0])
    dist = (maze_size/chunk_num)/2

    tl = [float(center[0]-dist),float(center[1]-dist)]
    tr = [float(center[0]+dist),float(center[1]-dist)]
    bl = [float(center[0]-dist),float(center[1]+dist)]
    br = [float(center[0]+dist),float(center[1]+dist)]

    # Top left, top right, bottom left, bottom right
    return [tl,tr,bl,br]

pts = np.array(find_chunk_centers(corners,6))

corners = find_chunk_corners(pts[0],corners,6)
corners


img = mpimg.imread('Maze_straightened.png')
plt.imshow(img)


# Draw points at coordinates (100, 150) and (200, 250)
plt.scatter(pts[:, 0], pts[:, 1], c='red', s=40) # s is marker size
plt.show()