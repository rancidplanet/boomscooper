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
pygame.display.set_caption("Boomscooper")

# Define colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# Define grid properties
grid_size = 30  # 30x30 grid
cell_size = screen_width // grid_size  # Size of each cell (calculated based on screen size)

# Define FPS (frames per second)
fps = 60
clock = pygame.time.Clock()

# List of all the sprite filenames you mentioned
sprite_filenames = [
    '0.png', '1.png', '2.png', '3.png', '4.png',
    '5.png', '6.png', '7.png', '8.png', 'bomb.png',
    'flag.png','hidden.png','bomb_flash_1.png','bomb_flash_2.png'
]

# Dictionary to hold the loaded sprite objects
sprites = {}


# Directions for neighboring cells (row_offset, col_offset)
directions = [(-1, -1), (-1, 0), (-1, 1),  # Top-left, Top, Top-right
		 (0, -1),         (0, 1),    # Left,        Right
		 (1, -1), (1, 0), (1, 1)]    # Bottom-left, Bottom, Bottom-right


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
def get_sprite_name(c):
    cell_value = c["value"]
    if cell_value == -1:
        return 'bomb'
    else:
        return f"{cell_value}"  # For example, '0n', '1n', etc.


def _in_bounds(grid,x,y):	
	if 0 <= x < len(grid) and 0 <= y < len(grid[0]):
		return True
	else: 
		return False

# Counts nearby mines to assign a number to a cell
def count_neighboring_mines(grid, row, col):
    # If the current cell is a mine (-1), skip it
    if grid[row][col]["value"] == -1:
        return -1

    # Count the mines around the current cell
    mine_count = 0
    for direction in directions:
        new_row, new_col = row + direction[0], col + direction[1]

        # Check if the neighbor is within the grid boundaries
        if _in_bounds(grid,new_row,new_col) != False:
            if grid[new_row][new_col]["value"] == -1:
                mine_count += 1

    return mine_count

# Create board function that makes the grid, places mines, and populates adjacent cells
def create_board(x: int,y: int,mines: int):
	def _cluster_place(grid,x,y,mines_left,cluster_range):
		if mines_left == 1:
			grid[x][y]["value"] = -1
			return grid, 0

 		# Find valid neighbor cells
		coords = find_n_neighbors(grid,cluster_range,x,y)
		
		# Places a random amount of mines in available spaces
		mines_to_place = randrange(0,mines_left )
		mines_placed = 0
		print(f"placing {mines_to_place}")
		for m in range(0,mines_to_place):
			new_row,new_col = choice(coords)
			pos = grid[new_row][new_col]["value"] 
			if pos != -1: 
				print(f"Placing a mine at {new_row},{new_col}, mines left: {mines_to_place}")
				grid[new_row][new_col]["value"] = -1
				mines_placed+= 1


		mines_left =  mines_left - mines_placed
		print(f"Done clustering mines! Mines left:{mines_left}")
		return grid, mines_left
				

	# Main board logic. Won't make a board with 0 mines, or with no dimensions
	if mines <=0:
		return False
	if x == 0 and y == 0:
		return False

	#Make grid, place mines
	else:
		print("Making grid, placing mines")
		
		grid = [[{"value":0,"hidden":True,"flag": False} for j in range(y)] for i in range(x)]
		mines_counter = mines
		while mines_counter != 0:
			t_x = randrange(x)
			t_y = randrange(y)
			tile_temp = grid[t_x][t_y]
			if tile_temp["value"] == -1: 
				continue
			else: #place mine
				grid, mines_counter = _cluster_place(grid,t_x,t_y,mines_counter,5)
		
		#Puts number in grid for neighboring mines	
		new_grid = [ [{"value": count_neighboring_mines(grid, i, j),"hidden":True,"flag":False} for i in range(x)] for j in range(y)]		
		return new_grid

def find_n_neighbors(grid,dist,x,y):
	# Make all available coordinates in range
	coords = []
	for vector in directions:
		for j in range(dist+1):
			pos = j * vector[0] , j * vector[1]
			pos = pos[0] + x, pos[1] + y # update relative to random position given
			if _in_bounds(grid,pos[0],pos[1]):
				coords.append((pos[0],pos[1]))
	
	return coords


def explode(grid,x,y):
	print(f"{pygame.time.get_ticks()}")
	flash_interval = 1000 # miliseconds betwee flashing
	flashes=10
	LAST = pygame.time.get_ticks()
	mode = 1
	while flashes > 0:
		clock.tick(fps)
		CURR = pygame.time.get_ticks()
		delta = CURR - LAST
		print(delta)
		if delta >= flash_interval:
			flashes-=1
			LAST = CURR
			if mode == 1:
				screen.blit(sprites['bomb_flash_1'], (x*cell_size, y*cell_size))
				mode = 2
				pygame.display.flip()
				continue
			if mode == 2:
				screen.blit(sprites['bomb_flash_2'], (x*cell_size, y*cell_size))
				mode = 1
				pygame.display.flip()
				continue

# Draw sprite, return updated grid
def reveal_cell(grid,tile):
		s = get_sprite_name(grid[tile[0]][tile[1]] )
		screen.blit(sprites[s],(tile[0]*cell_size,tile[1]*cell_size) )
		grid[tile[0]][tile[1]]["hidden"] = False
		return grid

def click_splash(grid,coor):
	x,y = coor
	neighbors = find_n_neighbors(grid,1,x,y)
	grid = reveal_cell(grid,coor)
	val = grid[x][y]["value"]
	
	if val == -1:
		explode(grid,x,y)
		return
	if val != 0:
		return
	for tile in neighbors:
		if grid[tile[0]][tile[1]]["hidden"] == True:
			click_splash(grid,tile)
		
def flag_tile(grid,x,y):
	grid[x][y]["flag"] = True
	sprite = sprites["flag"]	
	screen.blit(sprite, (x*cell_size, y*cell_size))
	return grid	

# Main game loop
def game_loop():
	length = 30
	width = 30
	grid = create_board(length,width,30)

	# Clear the screen
	screen.fill((0, 0, 0))

	# Draw the starting grid
	for row in range(len(grid)):
		for col in range(len(grid[row])):
		    sprite = sprites['hidden']
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
				x,y = event.pos
				tile_x = x // cell_size
				tile_y = y // cell_size
				if event.button == 1: #left click, reveal
					click_splash(grid,(tile_x,tile_y) )
				if event.button == 3: #right click, flag
					grid = flag_tile(grid,tile_x,tile_y)

			if pygame.mouse.get_pressed()[0] == True:
				print("CLICKING")


		pygame.display.flip()
		clock.tick(fps)


# Run the game
if __name__=='__main__':
	seed()
	game_loop()

