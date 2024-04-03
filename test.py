import cv2
import numpy as np
import matplotlib.pyplot as plt

# Function to draw clickable boxes
def draw_clickable_boxes(image, boxes, selected_index):
    box_width = image.shape[1] // 6
    box_height = image.shape[0] // len(boxes)
    for i, box in enumerate(boxes):
        if i == selected_index:
            color = (0, 255, 0)  # Selected box color
        else:
            color = (255, 255, 255)  # Default box color
        cv2.rectangle(image, (0, i * box_height), (box_width, (i + 1) * box_height), color, -1)
        cv2.putText(image, box, (10, (i * box_height) + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    return image

# Function to draw graphs
def draw_graphs(screen_width):
# Define the position and size of the graph
    left = screen_width // 6  # Starting x-coordinate of the graph
    width = 5 * (screen_width // 6)  # Width of the graph

    # Create some example data for the graph
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # Create a subplot on the right side of the image
    ax = plt.axes([left / screen_width, 0, width / screen_width, 1])
    ax.plot(x, y)
    ax.set_title('Graph')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_xlim(0, 10)
    ax.set_ylim(-1.2, 1.2)
    ax.grid(True)

# Main function
def main():
    screen_size = (720, 1280)  # Example screen width, you can adjust this accordingly
    # List of clickable boxes
    boxes = ['Graph 1', 'Graph 2', 'Graph 3', 'Graph 4']
    selected_index = 0

    #while True:
    # Create blank image
    image = np.zeros((screen_size[0], screen_size[1], 3), dtype=np.uint8)

    # Draw clickable boxes
    image = draw_clickable_boxes(image, boxes, selected_index)

    # Draw graphs
    draw_graphs(screen_size[1])

    # Display image
    cv2.imshow('Clickable Boxes and Graphs', image)
    while True:
        # Check for user input
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('w') and selected_index > 0:
            selected_index -= 1
        elif key == ord('s') and selected_index < len(boxes) - 1:
            selected_index += 1

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
