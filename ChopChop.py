import curses
import random
import time
import pygame

TREE_HEIGHT = 20
BRANCH_PROBABILITY = 0.6
LEFT = "L"
RIGHT = "R"
NONE = " "
LEFT_OFFSET = 6
RIGHT_OFFSET = 3
BASE_CHOP_TIME = 3.0
INITIAL_GAME_TIME = BASE_CHOP_TIME * 3
BASE_CHOP_ADDITION = BASE_CHOP_TIME

def generate_branch(prev_side):
    if random.random() < BRANCH_PROBABILITY:
        return LEFT if prev_side == RIGHT else RIGHT
    return NONE

def draw_game(stdscr, tree, player_side, chops, high_score, game_over, time_remaining, is_new_high):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    for i, branch in enumerate(tree):
        y = i + 1
        center_x = width // 2
        if branch == LEFT:
            stdscr.addstr(y, center_x - LEFT_OFFSET, "<==")
        elif branch == RIGHT:
            stdscr.addstr(y, center_x + RIGHT_OFFSET, "==>")
        stdscr.addstr(y, center_x, "||")

    player_y = TREE_HEIGHT + 2
    center_x = width // 2
    if player_side == LEFT:
        stdscr.addstr(player_y, center_x - LEFT_OFFSET, "(O)")
    else:
        stdscr.addstr(player_y, center_x + RIGHT_OFFSET, "(O)")

    stdscr.addstr(0, 2, f"Chops: {chops}")
    stdscr.addstr(2, 2, f"Time: {max(0, time_remaining):.2f}s")

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

    high_score = 0  # Track high score for the session
    is_new_high = False  # Track if current game beat the high score

    def init_game():
        pygame.mixer.init()
        pygame.mixer.music.load("Lumber.mp3")
        pygame.mixer.music.play(-1)

        tree = []
        last_branch_side = RIGHT

        for _ in range(TREE_HEIGHT):
            branch = generate_branch(last_branch_side)
            if branch != NONE:
                last_branch_side = branch
            tree.append(branch)

        return tree, RIGHT, 0, False, INITIAL_GAME_TIME, time.time(), last_branch_side

    tree, player_side, chops, game_over, time_remaining, last_time, last_branch_side = init_game()

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
                tree, player_side, chops, game_over, time_remaining, last_time, last_branch_side = init_game()
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
        new_branch = generate_branch(last_branch_side)
        if new_branch != NONE:
            last_branch_side = new_branch
        tree.insert(0, new_branch)
        chops += 1
        time_remaining += BASE_CHOP_ADDITION / chops if chops > 0 else 0

if __name__ == "__main__":
    curses.wrapper(main)
