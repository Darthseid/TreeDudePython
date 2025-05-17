import curses
import random
import time
import pygame

TREE_HEIGHT = 20
BRANCH_PROBABILITY = 2/3  # Equal probability of left, right, none
LEFT = "L"
RIGHT = "R"
NONE = " "

# Offsets may need tuning depending on terminal font/emoji width
LEFT_OFFSET = 4
RIGHT_OFFSET = 2

BASE_CHOP_TIME = 3.0
INITIAL_GAME_TIME = BASE_CHOP_TIME * 3

# Emoji representations
TREE_EMOJI = "🌳"
BRANCH_EMOJI = "🌿"
PLAYER_EMOJI = "🧑‍🚒"

def generate_branch():
    if random.random() < BRANCH_PROBABILITY:
        return random.choice([LEFT, RIGHT])
    return NONE

def draw_game(stdscr, tree, player_side, chops, high_score, game_over, time_remaining, is_new_high):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    center_x = width // 2

    # Draw the tree with branches
    for i, branch in enumerate(tree):
        y = i + 1
        if branch == LEFT:
            stdscr.addstr(y, center_x - LEFT_OFFSET, BRANCH_EMOJI)
        elif branch == RIGHT:
            stdscr.addstr(y, center_x + RIGHT_OFFSET, BRANCH_EMOJI)
        stdscr.addstr(y, center_x, TREE_EMOJI)

    # Draw the player
    player_y = TREE_HEIGHT + 2
    if player_side == LEFT:
        stdscr.addstr(player_y, center_x - LEFT_OFFSET, PLAYER_EMOJI)
    else:
        stdscr.addstr(player_y, center_x + RIGHT_OFFSET, PLAYER_EMOJI)

    # Display score and timer
    stdscr.addstr(0, 2, f"Chops: {chops}")
    stdscr.addstr(2, 2, f"Time: {max(0, time_remaining):.2f}s")

    # Game over message
    if game_over:
        stdscr.addstr(player_y + 2, center_x - 5, "GAME OVER!")
        if is_new_high:
            stdscr.addstr(player_y + 3, center_x - 8, f"New High Score!: {high_score}")
        else:
            stdscr.addstr(player_y + 3, center_x - 9, f"Current High Score: {high_score}")
        stdscr.addstr(player_y + 4, center_x - 9, "Press 'r' to restart")

    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)

    high_score = 0
    is_new_high = False

    def init_game():
        pygame.mixer.init()
        pygame.mixer.music.load("Lumber.mp3")
        pygame.mixer.music.play(-1)
        tree = [generate_branch() for _ in range(TREE_HEIGHT)]
        return tree, RIGHT, 0, False, INITIAL_GAME_TIME, time.time()

    tree, player_side, chops, game_over, time_remaining, last_time = init_game()

    while True:
        now = time.time()
        delta_time = now - last_time
        last_time = now
        if chops > high_score:
            high_score = chops
            is_new_high = True
        if not game_over:
            time_remaining -= delta_time

        draw_game(stdscr, tree, player_side, chops, high_score, game_over, time_remaining, is_new_high)

        key = stdscr.getch()

        if game_over:
            if key == ord('r'):
                tree, player_side, chops, game_over, time_remaining, last_time = init_game()
                continue
            else:
                continue

        if time_remaining <= 0:
            game_over = True
            continue

        if key == ord('a'):
            player_side = LEFT
        elif key == ord('d'):
            player_side = RIGHT
        else:
            continue

        if tree[-1] == player_side:
            game_over = True
            continue

        tree.pop()
        tree.insert(0, generate_branch())
        chops += 1
        time_remaining += BASE_CHOP_TIME / chops if chops > 0 else 0

if __name__ == "__main__":
    curses.wrapper(main)
