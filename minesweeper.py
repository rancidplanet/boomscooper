import pygame
import sys
import os
from pprint import pprint
from random import randrange,choice,seed


# Initialize Pygame
pygame.init()

# Define the screen size
screen_width = 600  # Width of the window
screen_height = 600  # Height of the window
screen = pygame.display.set_mode((screen_width, screen_height))

# Set window title
pygame.display.set_caption("Minesweeper")

# Define colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# Define grid properties
grid_size = 30  # 30x30 grid
cell_size = screen_width // grid_size  # Size of each cell (calculated based on screen size)

# Define FPS (frames per second)
fps = 60
clock = pygame.time.Clock()

# Load Assets
open_sprite = pygame.image.load('assets/open.png')
open_sprite = pygame.transform.scale(open_sprite, (cell_size, cell_size))

# List of all the sprite filenames you mentioned
sprite_filenames = [
    '0n.png', '1n.png', '2n.png', '3n.png', '4n.png',
    '5n.png', '6n.png', '7n.png', '8n.png', 'bomb.png',
    'boom.png', 'flag.png','open.png'
]

# Dictionary to hold the loaded sprite objects
sprites = {}

# Load and scale each sprite
for filename in sprite_filenames:
    # Load the image from the assets folder
    sprite = pygame.image.load(os.path.join('assets', filename))
    
    # Scale the image to match the cell size
    sprite = pygame.transform.scale(sprite, (cell_size, cell_size))
    
    # Save the sprite object in the dictionary, using the filename (without extension) as the key
    sprite_name = os.path.splitext(filename)[0]  # Remove file extension (.png)
    sprites[sprite_name] = sprite


# Map grid values to the correct sprite names
def get_sprite_name(cell_value):
    if cell_value == -1:
        return 'bomb'
    elif cell_value == 'f':
        return 'flag'
    else:
        return f"{cell_value}n"  # For example, '0n', '1n', etc.


def _in_bounds(grid,x,y):	
	if 0 <= x < len(grid) and 0 <= y < len(grid[0]):
		return True
	else: 
		return False

def count_neighboring_mines(grid, row, col):
    # If the current cell is a mine (-1), skip it
    if grid[row][col] == -1:
        return -1

    # Directions for neighboring cells (row_offset, col_offset)
    directions = [(-1, -1), (-1, 0), (-1, 1),  # Top-left, Top, Top-right
                  (0, -1),         (0, 1),    # Left,        Right
                  (1, -1), (1, 0), (1, 1)]    # Bottom-left, Bottom, Bottom-right

    # Count the mines around the current cell
    mine_count = 0
    for direction in directions:
        new_row, new_col = row + direction[0], col + direction[1]

        # Check if the neighbor is within the grid boundaries
        if _in_bounds(grid,new_row,new_col) != False:
            if grid[new_row][new_col] == -1:
                mine_count += 1

    return mine_count

# Create board function that makes the grid, places mines, and populates adjacent cells
def create_board(x: int,y: int,mines: int):
	def _cluster_place(grid,x,y,mines_left,cluster_range):
		# Directions for neighboring cells (row_offset, col_offset)
		directions = [(-1, -1), (-1, 0), (-1, 1),  # Top-left, Top, Top-right
				 (0, -1),         (0, 1),    # Left,        Right
				 (1, -1), (1, 0), (1, 1)]    # Bottom-left, Bottom, Bottom-right

		if mines_left > 7:
			mines_to_place = randrange(1,7)
	
		else: mines_to_place = mines_left

		print(f"There are {mines_left} mines left, and we're clustering {mines_to_place} mines {cluster_range} cells apart")

		# Make all available coordinates in range
		coords = []
		for vector in directions:
			for j in range(cluster_range):
				pos = j * vector[0] , j * vector[1]
				pos = pos[0] + x, pos[1] + y # update relative to random position given
				if _in_bounds(grid,pos[0],pos[1]):
					coords.append(pos)

		final_mines = mines_to_place
		while mines_to_place > 0:
			new_row,new_col = choice(coords)
			if _in_bounds(grid,new_row,new_col) == True:
				pos = grid[new_row][new_col] 
				if pos == -1: continue
				grid[new_row][new_col] = -1
				mines_to_place -=1
			else:
				continue
		
		print("Done clustering mines!")
		return grid, mines_left - final_mines
				

	# Main board logic. Won't make a board with 0 mines, or with no dimensions
	if mines <=0:
		return False
	if x == 0 and y == 0:
		return False

	#Make grid, place mines
	else:
		print("Making grid, placing mines")
		grid = [[0 for j in range(y)] for i in range(x)]
		mines_counter = mines
		while mines_counter > 0:
			t_x = randrange(x)
			t_y = randrange(y)
			pos = grid[t_x][t_y]
			if pos == -1: 
				continue
			else: #place mine
				grid, mines_counter = _cluster_place(grid,t_x,t_y,mines_counter,5)
		
		#Puts number in grid for neighboring mines	
		new_grid = [ [count_neighboring_mines(grid, i, j) for i in range(x)] for j in range(y)]		
		return new_grid


# Main game loop
def game_loop():
	grid = create_board(30,30,20)

	# Clear the screen
	screen.fill((0, 0, 0))

	# Draw the grid
	for row in range(len(grid)):
		for col in range(len(grid[row])):
		    sprite_name = get_sprite_name(grid[row][col])
		    sprite = sprites[sprite_name]
		    # Calculate the position for each sprite
		    x = row * cell_size
		    y = col * cell_size
		    # Draw the sprite at the calculated position
		    screen.blit(sprite, (x, y))

	# Update the display
	pygame.display.flip()


	while True:
	# Handle events
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN or event.type == pygame.KEYDOWN:
				print(event)

			if event.type == pygame.MOUSEBUTTONDOWN:
				print(f"clicked tile at {event.pos}")
				x,y = event.pos
				tile_x = x // cell_size
				tile_y = y // cell_size
				print(f"CLicked tile at {tile_x},{tile_y}")
				print(get_sprite_name(grid[tile_x][tile_y]) )
				screen.blit(sprites['boom'],(tile_x * cell_size,tile_y * cell_size))
			if pygame.mouse.get_pressed()[0] == True:
				print("CLICKING")


		pygame.display.flip()
		clock.tick(fps)


# Run the game
if __name__=='__main__':
	seed()
	game_loop()

