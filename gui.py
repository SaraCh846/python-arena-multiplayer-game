import pygame
import threading
import time
from client_network import NetworkClient
import math
pygame.init()

#window size
WIDTH = 1100
HEIGHT = 750

#color options
WHITE = (255, 255, 255)
PINK = (255, 105, 180)
PURPLE = (75, 0, 130)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

CARD_BG = (12, 12, 18)
CARD_BORDER = (170, 170, 200)
ACCENT = (0, 255, 200)
MUTED = (190, 190, 210)
INPUT_BG = (10, 10, 16)
ERROR_RED = (255, 90, 90)

#fonts
FONT = pygame.font.SysFont(None, 40)
SMALL_FONT = pygame.font.SysFont(None, 30)
LABEL_FONT = pygame.font.SysFont(None, 22)

#default game settings
DEFAULT_BOARD_WIDTH = 20
DEFAULT_BOARD_HEIGHT = 20
DEFAULT_STARTING_HEALTH = 100
DEFAULT_TIME_LEFT = 60

CELL_SIZE = 25
BOARD_X = 40
BOARD_Y = 100 


def draw_text(screen, text, font, color, x, y): #draw text on screen
    text_surface = font.render(text, True, color) 
    screen.blit(text_surface, (x, y))

def draw_input_box(screen, text, x, y, w, h, active=True): #draw styled input field 
    rect = pygame.Rect(x, y, w, h)

    fill_color = INPUT_BG
    border_color = ACCENT if active else CARD_BORDER

    pygame.draw.rect(screen, fill_color, rect, border_radius=12)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=12)

    text_surface = SMALL_FONT.render(text, True, WHITE)
    screen.blit(text_surface, (x + 14, y + 12))

def draw_center_card(screen, x, y, w, h): #draw centered UI panel
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, CARD_BG, rect, border_radius=18)
    pygame.draw.rect(screen, CARD_BORDER, rect, 3, border_radius=18)

def draw_username_screen(screen, username_text, error_message):
    screen.fill(BLACK)

    card_w = 560
    card_h = 360
    card_x = (WIDTH - card_w) // 2
    card_y = (HEIGHT - card_h) // 2

    draw_center_card(screen, card_x, card_y, card_w, card_h)

    title_x = card_x + 40
    draw_text(screen, "Python Arena", FONT, WHITE, title_x, card_y + 35)
    draw_text(screen, "Enter your username", FONT, ACCENT, title_x, card_y + 95)

    draw_text(screen, "Username", SMALL_FONT, MUTED, title_x, card_y + 165)
    draw_input_box(screen, username_text, title_x, card_y + 200, 480, 56, active=True)

    draw_text(screen, "Press ENTER to continue", SMALL_FONT, MUTED, title_x, card_y + 280)

    if error_message:
        draw_text(screen, error_message, SMALL_FONT, ERROR_RED, title_x, card_y + 320)

def draw_connect_screen(screen, ip_text, port_text, active_field, error_message):
    screen.fill(BLACK)

    card_w = 620
    card_h = 470
    card_x = (WIDTH - card_w) // 2
    card_y = (HEIGHT - card_h) // 2

    draw_center_card(screen, card_x, card_y, card_w, card_h)

    title_x = card_x + 40
    draw_text(screen, "Python Arena", FONT, WHITE, title_x, card_y + 35)
    draw_text(screen, "Connect to Server", FONT, ACCENT, title_x, card_y + 95)

    draw_text(screen, "Server IP Address", SMALL_FONT, MUTED, title_x, card_y + 165)
    draw_input_box(
        screen,
        ip_text,
        title_x,
        card_y + 200,
        540,
        56,
        active=(active_field == "ip")
    )

    draw_text(screen, "Server Port", SMALL_FONT, MUTED, title_x, card_y + 280)
    draw_input_box(
        screen,
        port_text,
        title_x,
        card_y + 315,
        540,
        56,
        active=(active_field == "port")
    )

    draw_text(screen, "TAB = switch field", SMALL_FONT, MUTED, title_x, card_y + 390)
    draw_text(screen, "ENTER = connect", SMALL_FONT, MUTED, title_x + 250, card_y + 390)

    if error_message:
        draw_text(screen, error_message, SMALL_FONT, ERROR_RED, title_x, card_y + 440)

def connect_gui(): #takes user input and attempts to connect to server 
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Python Arena - Connect")

    clock = pygame.time.Clock()
    ip_text = ""
    port_text = ""
    active_field = "ip"
    error_message = ""
    running = True

    while running:
        for event in pygame.event.get(): #event handling
            if event.type == pygame.QUIT: #close window
                pygame.quit()
                return None

            if event.type == pygame.KEYDOWN: #keyboard input
                if event.key == pygame.K_ESCAPE: #ESC to exit
                    pygame.quit()
                    return None

                elif event.key == pygame.K_TAB: #tab to switch field
                    active_field = "port" if active_field == "ip" else "ip"

                elif event.key == pygame.K_BACKSPACE: #backspace to delete charachters
                    if active_field == "ip":
                        ip_text = ip_text[:-1]
                    else:
                        port_text = port_text[:-1]

                elif event.key == pygame.K_RETURN: #enter to connect
                    if ip_text.strip() == "" or port_text.strip() == "":
                        error_message = "Please enter both server IP and port."
                    else:
                        try:
                            server_port = int(port_text.strip())
                            client = NetworkClient(ip_text.strip(), server_port)
                            client.connect()
                            return client
                        except ValueError:
                            error_message = "Port must be a number."
                        except Exception as e:
                            error_message = f"Could not connect: {e}"

                else: #typing input
                    if active_field == "ip":
                        if event.unicode.isprintable():
                            ip_text += event.unicode
                    elif active_field == "port":
                        if event.unicode.isdigit():
                            port_text += event.unicode

        draw_connect_screen(screen, ip_text, port_text, active_field, error_message)
        pygame.display.flip()
        clock.tick(60)

def draw_panel(screen, x, y, w, h, border_color=WHITE, fill_color=(10, 10, 16)):
    rect = pygame.Rect(x, y, w, h)

    pygame.draw.rect(screen, fill_color, rect, border_radius=14)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=14)

    pygame.draw.rect(screen, (40, 40, 60), rect, 1, border_radius=14)

def draw_lobby_screen(screen, username, players, selected_index, status_message, chosen_opponent):
    screen.fill(BLACK)

    draw_lobby_snake(screen, 760, 70, ACCENT, (0, 180, 140), phase=0)

    #add titles
    draw_text(screen, "Python Arena", FONT, WHITE, 80, 55)
    draw_text(screen, "Game Lobby", FONT, ACCENT, 80, 100)
    draw_text(screen, f"Logged in as: {username}", SMALL_FONT, MUTED, 80, 145)

    #adding list of players (on the left side)
    left_x = 80
    left_y = 210
    left_w = 470
    left_h = 310
    draw_panel(screen, left_x, left_y, left_w, left_h, border_color=CARD_BORDER, fill_color=INPUT_BG)

    draw_text(screen, "Online Players", FONT, WHITE, left_x + 20, left_y + 20)

    if not players:
        draw_text(screen, "No other players online yet.", SMALL_FONT, MUTED, left_x + 20, left_y + 95)
    else:
        for i, player in enumerate(players): #loop through all players
            y = left_y + 90 + i * 42
            is_selected = (i == selected_index) #check if any is currently selected

            name = player["username"]
            status = player["status"]

            if status == "BUSY":
                dot_color = YELLOW
                text_color = YELLOW if is_selected else MUTED
            else:
                dot_color = ACCENT
                pulse = 180 + int(50 * math.sin(pygame.time.get_ticks() * 0.008))
                text_color = (pulse, pulse, pulse) if is_selected else MUTED

            if is_selected:
                pygame.draw.rect(screen, (30, 30, 40), (left_x + 12, y - 6, left_w - 24, 34), border_radius=8)
                pygame.draw.rect(screen, ACCENT, (left_x + 12, y - 6, left_w - 24, 34), 2, border_radius=8)

            pygame.draw.circle(screen, dot_color, (left_x + 28, y + 10), 6)
            draw_text(screen, f"{name} ({status})", SMALL_FONT, text_color, left_x + 45, y)

    #list of instructions (on the right side)
    right_x = 620
    right_y = 210
    right_w = 390
    right_h = 210
    draw_panel(screen, right_x, right_y, right_w, right_h, border_color=CARD_BORDER, fill_color=INPUT_BG)

    draw_text(screen, "How to Play", FONT, WHITE, right_x + 20, right_y + 20)
    draw_text(screen, "UP / DOWN = choose player", SMALL_FONT, MUTED, right_x + 20, right_y + 85)
    draw_text(screen, "ENTER = challenge player", SMALL_FONT, MUTED, right_x + 20, right_y + 125)

    if any(player["status"] == "BUSY" for player in players):
        draw_text(screen, "W = watch ongoing match", SMALL_FONT, MUTED, right_x + 20, right_y + 165)

    status_x = 80
    status_y = 570
    status_w = 930
    status_h = 55
    draw_panel(screen, status_x, status_y, status_w, status_h, border_color=ACCENT if status_message else CARD_BORDER, fill_color=INPUT_BG)

    line1_y = status_y + 10
    line2_y = status_y + 34

    if chosen_opponent:
        draw_text(screen, f"Selected opponent: {chosen_opponent}", SMALL_FONT, CYAN, status_x + 18, line1_y)

    if status_message:
        draw_text(screen, status_message, SMALL_FONT, YELLOW, status_x + 28, line2_y)

def draw_lobby_snake(screen, base_x, base_y, head_color, body_color, phase=0):
    t = pygame.time.get_ticks() * 0.005 + phase
    snake_length = 7

    for i in range(snake_length):
        x = base_x + i * 22
        y = base_y + int(8 * math.sin(t + i * 0.45))

        rect = pygame.Rect(x, y, 16, 16)

        color = head_color if i == 0 else body_color
        pygame.draw.rect(screen, color, rect, border_radius=7)

        if i == 0:
            pygame.draw.rect(screen, WHITE, rect, 1, border_radius=7)
            pygame.draw.circle(screen, WHITE, (x + 5, y + 6), 2)
            pygame.draw.circle(screen, WHITE, (x + 11, y + 6), 2)

def lobby_gui(client, existing_username=None, seeded_messages=None): #listens for server messages and handles username input, updating player list, and matchmaking logic
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Python Arena Lobby")

    clock = pygame.time.Clock()
    running = True

    if existing_username is None:
        current_screen = "username"
        username_text = ""
        username = None
    else:
        current_screen = "lobby"
        username_text = existing_username
        username = existing_username

    username_error = ""
    waiting_for_username_reply = False

    players = []
    selected_index = 0
    chosen_opponent = None
    status_message = ""

    message_queue = list(seeded_messages) if seeded_messages else [] #messages from previous game
    state_lock = threading.Lock()

    def receive_messages():
        nonlocal running
        while running:
            message = client.receive_message()
            if message is None: 
                with state_lock:
                    message_queue.append({"type": "DISCONNECTED"})
                break
            with state_lock:
                message_queue.append(message)

    threading.Thread(target=receive_messages, daemon=True).start()

    if existing_username is not None:
        already_have_list = any(m.get("type") == "PLAYER_LIST" for m in message_queue)
        already_have_start = any(m.get("type") == "GAME_START" for m in message_queue)
        if not already_have_list and not already_have_start:
            time.sleep(0.1)
            client.send_message({"type": "REQUEST_PLAYER_LIST"})

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return None

            if event.type == pygame.KEYDOWN:
                if current_screen == "username":
                    if event.key == pygame.K_RETURN:
                        if username_text.strip() == "":
                            username_error = "Please enter a username."
                        elif not waiting_for_username_reply:
                            client.send_message({
                                "type": "USERNAME",
                                "username": username_text.strip()
                            })
                            username_error = "Checking username..."
                            waiting_for_username_reply = True
                    elif event.key == pygame.K_BACKSPACE:
                        if not waiting_for_username_reply:
                            username_text = username_text[:-1]
                    else:
                        if not waiting_for_username_reply:
                            if len(username_text) < 15 and event.unicode.isprintable():
                                username_text += event.unicode

                elif current_screen == "lobby":
                    if event.key == pygame.K_w:
                        if any(player["status"] == "BUSY" for player in players):
                            client.send_message({"type": "WATCH_MATCH"})
                            status_message = "Joining as spectator..."
                    elif event.key == pygame.K_UP and players:
                        selected_index = (selected_index - 1) % len(players)
                    elif event.key == pygame.K_DOWN and players:
                        selected_index = (selected_index + 1) % len(players)
                    elif event.key == pygame.K_RETURN and players:
                        selected_player = players[selected_index]
                        if selected_player["status"] == "BUSY":
                            status_message = f'{selected_player["username"]} is busy right now.'
                        else:
                            chosen_opponent = selected_player["username"]
                            client.send_message({
                                "type": "CHOOSE_OPPONENT",
                                "opponent": chosen_opponent
                            })
                            status_message = f"Challenge sent to {chosen_opponent}. Waiting for them to choose you back."

        with state_lock:
            pending_messages = message_queue[:]
            message_queue.clear()

        for message in pending_messages:
            msg_type = message.get("type")

            if msg_type == "USERNAME_OK":
                waiting_for_username_reply = False
                username = username_text.strip()
                setup = setup_snake_gui(username)
                if setup is None:
                    running = False
                    pygame.quit()
                    return None
                client.send_message({
                    "type": "PLAYER_SETUP",
                    "snake_style": setup["snake_style"],
                    "snake_color": setup["snake_color"]
                })
                client.send_message({"type": "REQUEST_PLAYER_LIST"})
                current_screen = "lobby"
                status_message = "Choose a player to challenge."

            elif msg_type == "USERNAME_TAKEN":
                waiting_for_username_reply = False
                username_error = "Username is already taken. Try another one."

            elif msg_type == "PLAYER_LIST": #updates players list 
                if username is not None:
                    new_players = [p for p in message["players"] if p["username"] != username]
                    old_selection_name = None
                    if players and selected_index < len(players):
                        old_selection_name = players[selected_index]["username"]
                    players = new_players
                    if not players:
                        selected_index = 0
                    elif old_selection_name is not None:
                        matching_index = next(
                            (i for i, p in enumerate(players) if p["username"] == old_selection_name),
                            None
                        )
                        selected_index = matching_index if matching_index is not None else 0
                    else:
                        selected_index = 0

            elif msg_type == "WAITING_FOR_OPPONENT":
                opponent = message.get("opponent")
                status_message = f"You selected {opponent}. Waiting for them to choose you back."

            elif msg_type == "GAME_BUSY":
                status_message = "A match is already running. Wait until it finishes."

            elif msg_type == "NOT_CHOSEN_BACK":
                opponent = message.get("opponent")
                status_message = f"{opponent} did not choose you back. Choose another opponent."
                chosen_opponent = None

            elif msg_type == "GAME_START": 
                running = False

                if message.get("mode") == "spectator":
                    return {
                        "username": username,
                        "mode": "spectator",
                        "player1_name": message.get("player1_name"),
                        "player2_name": message.get("player2_name")
                    }

                return {
                    "username": username,
                    "opponent": message.get("opponent"),
                    "player_number": message.get("player_number"),
                    "mode": "player"
                }
            elif msg_type == "NO_MATCH_TO_WATCH":
                status_message = "There is no ongoing match to watch."

            elif msg_type == "DISCONNECTED":
                status_message = "Disconnected from server."
                pygame.time.delay(1000)
                running = False
                return None

        if current_screen == "username":
            draw_username_screen(screen, username_text, username_error)
        elif current_screen == "lobby":
            draw_lobby_screen(screen, username, players, selected_index, status_message, chosen_opponent)

        pygame.display.flip()
        clock.tick(60)


def setup_snake_gui(username): #allows player to select snake color and shows a preview of the snake 
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Setup")

    #list of available snake colors
    colors = [
        ("Green", GREEN),
        ("Red", RED),
        ("Blue", BLUE),
        ("Yellow", YELLOW),
        ("Cyan", CYAN),
        ("Pink", PINK),
        ("Purple", PURPLE)
    ]

    selected_index = 0
    running = True

    while running:
        screen.fill(BLACK)

        card_w = 920
        card_h = 560
        card_x = (WIDTH - card_w) // 2
        card_y = 70

        draw_center_card(screen, card_x, card_y, card_w, card_h)

        draw_text(screen, "Python Arena", FONT, WHITE, card_x + 35, card_y + 25)
        draw_text(screen, f"Welcome, {username}", FONT, ACCENT, card_x + 35, card_y + 75)
        draw_text(screen, "Customize your snake", SMALL_FONT, MUTED, card_x + 35, card_y + 125)

        colors_x = card_x + 35
        colors_y = card_y + 170
        colors_w = 420
        colors_h = 320
        draw_panel(screen, colors_x, colors_y, colors_w, colors_h, border_color=CARD_BORDER, fill_color=INPUT_BG)

        draw_text(screen, "Choose Snake Color", SMALL_FONT, WHITE, colors_x + 20, colors_y + 20)

        for i, (name, color) in enumerate(colors):
            y = colors_y + 65 + i * 36
            is_selected = (i == selected_index)

            if is_selected:
                pygame.draw.rect(screen, (30, 30, 40), (colors_x + 12, y - 4, colors_w - 24, 30), border_radius=8)
                pygame.draw.rect(screen, ACCENT, (colors_x + 12, y - 4, colors_w - 24, 30), 2, border_radius=8)

            text_color = WHITE if is_selected else MUTED
            prefix = "→ " if is_selected else "  "

            draw_text(screen, f"{prefix}{name}", SMALL_FONT, text_color, colors_x + 20, y)
            pygame.draw.rect(screen, color, (colors_x + 250, y + 2, 90, 24), border_radius=6)
            pygame.draw.rect(screen, WHITE, (colors_x + 250, y + 2, 90, 24), 1, border_radius=6)

        preview_x = card_x + 500
        preview_y = card_y + 170
        preview_w = 385
        preview_h = 160
        draw_panel(screen, preview_x, preview_y, preview_w, preview_h, border_color=CARD_BORDER, fill_color=INPUT_BG)

        draw_text(screen, "Snake Preview", SMALL_FONT, WHITE, preview_x + 120, preview_y + 18)

        preview_color = colors[selected_index][1]
        preview_snake = [(0, 0), (1, 0), (2, 0), (3, 0)]
        old_board_x = BOARD_X
        old_board_y = BOARD_Y

        for i, (sx, sy) in enumerate(preview_snake):
            rect = pygame.Rect(preview_x + 70 + i * 30, preview_y + 75, 22, 22)
            segment_color = lighten_color(preview_color, 50) if i == 0 else preview_color
            pygame.draw.rect(screen, segment_color, rect, border_radius=8)
            if i == 0:
                pygame.draw.circle(screen, WHITE, (rect.x + 6, rect.y + 8), 2)
                pygame.draw.circle(screen, WHITE, (rect.x + 16, rect.y + 8), 2)

        controls_x = preview_x
        controls_y = preview_y + 185
        controls_w = 385
        controls_h = 145
        draw_panel(screen, controls_x, controls_y, controls_w, controls_h, border_color=CARD_BORDER, fill_color=INPUT_BG)

        draw_text(screen, "Controls", SMALL_FONT, WHITE, controls_x + 20, controls_y + 18)
        draw_text(screen, "UP / DOWN = choose color", SMALL_FONT, MUTED, controls_x + 20, controls_y + 50)
        draw_text(screen, "ENTER = confirm", SMALL_FONT, MUTED, controls_x + 20, controls_y + 82)
        draw_text(screen, "Arrow keys will control the snake", SMALL_FONT, MUTED, controls_x + 20, controls_y + 114)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(colors)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(colors)
                elif event.key == pygame.K_RETURN:
                    running = False

    selected_name, selected_color = colors[selected_index]
    return {
        "snake_style": selected_name,
        "snake_color": selected_color,
    }


def lighten_color(color, amount=40):
    return tuple(min(255, c + amount) for c in color)

def draw_grid(screen, board_width, board_height): #draws internal lines
    grid_color = (50, 50, 50)
    for x in range(1, board_width):
        pygame.draw.line(
            screen, grid_color,
            (BOARD_X + x * CELL_SIZE, BOARD_Y),
            (BOARD_X + x * CELL_SIZE, BOARD_Y + board_height * CELL_SIZE)
        )
    for y in range(1, board_height):
        pygame.draw.line(
            screen, grid_color,
            (BOARD_X, BOARD_Y + y * CELL_SIZE),
            (BOARD_X + board_width * CELL_SIZE, BOARD_Y + y * CELL_SIZE)
        )

def draw_board(screen, board_width, board_height): #draws outer borders
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, board_width * CELL_SIZE, board_height * CELL_SIZE)
    pygame.draw.rect(screen, WHITE, board_rect, 3, border_radius=8)

def draw_snake(screen, snake, color): 
    margin = 3
    for i, segment in enumerate(snake):
        x, y = segment
        rect = pygame.Rect(
            BOARD_X + x * CELL_SIZE + margin,
            BOARD_Y + y * CELL_SIZE + margin,
            CELL_SIZE - 2 * margin,
            CELL_SIZE - 2 * margin
        )
        segment_color = lighten_color(color) if i == 0 else color
        pygame.draw.rect(screen, segment_color, rect, border_radius=8)
        if i == 0:
            eye_radius = 2
            pygame.draw.circle(screen, WHITE, (rect.x + 7, rect.y + 8), eye_radius)
            pygame.draw.circle(screen, WHITE, (rect.x + rect.width - 7, rect.y + 8), eye_radius)

def draw_snake_label(screen, snake, name, color, y_offset=0): #displays the chosen username above the snake
    if not snake:
        return

    head_x, head_y = snake[0]

    head_pixel_x = BOARD_X + head_x * CELL_SIZE + CELL_SIZE // 2
    head_pixel_y = BOARD_Y + head_y * CELL_SIZE

    text_surface = LABEL_FONT.render(name, True, color)
    text_rect = text_surface.get_rect()

    label_x = head_pixel_x - text_rect.width // 2 - 8
    label_y = head_pixel_y - 34 + y_offset

    bg_rect = pygame.Rect(
        label_x,
        label_y,
        text_rect.width + 10,
        text_rect.height + 4
)

    pygame.draw.rect(screen, (25, 25, 25), bg_rect, border_radius=8)
    pygame.draw.rect(screen, color, bg_rect, 2, border_radius=8)

    screen.blit(text_surface, (label_x + 5, label_y + 2))

    
    arrow_tip = (head_pixel_x, head_pixel_y + 2)
    arrow_left = (head_pixel_x - 4, label_y + bg_rect.height)
    arrow_right = (head_pixel_x + 4, label_y + bg_rect.height)

    pygame.draw.polygon(screen, color, [arrow_left, arrow_right, arrow_tip])

def draw_pies(screen, pies): 
    for pie in pies:
        x, y = pie
        center_x = BOARD_X + x * CELL_SIZE + CELL_SIZE // 2
        center_y = BOARD_Y + y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, RED, (center_x, center_y), CELL_SIZE // 3)
        pygame.draw.circle(screen, WHITE, (center_x - 4, center_y - 4), 2)

def draw_obstacles(screen, obstacles):
    margin = 2
    for obstacle in obstacles:
        x, y = obstacle
        rect = pygame.Rect(
            BOARD_X + x * CELL_SIZE + margin,
            BOARD_Y + y * CELL_SIZE + margin,
            CELL_SIZE - 2 * margin,
            CELL_SIZE - 2 * margin
        )
        pygame.draw.rect(screen, (120, 120, 120), rect, border_radius=4)
        pygame.draw.rect(screen, (170, 170, 170), rect, 2, border_radius=4)

def draw_side_panel(screen, state, match_info=None): #shows health, timer, and spectator info
    player1_health = state.get("player1_health", DEFAULT_STARTING_HEALTH)
    player2_health = state.get("player2_health", DEFAULT_STARTING_HEALTH)
    time_left = state.get("time_left", DEFAULT_TIME_LEFT)
    player1_frozen = state.get("player1_frozen", False)
    player2_frozen = state.get("player2_frozen", False)
    player1_confused = state.get("player1_confused", False)
    player2_confused = state.get("player2_confused", False)
    draw_text(screen, "Game Info", FONT, WHITE, 650, 120)

    if match_info is not None:
        mode = match_info.get("mode", "player")
        username = match_info.get("username", "Unknown")
        opponent = match_info.get("opponent", "Unknown")
        player_number = match_info.get("player_number", "?")
        if mode == "spectator":
            player1_name = match_info.get("player1_name", "Player 1")
            player2_name = match_info.get("player2_name", "Player 2")

            draw_text(screen, f"Watching: {player1_name} vs {player2_name}", SMALL_FONT, WHITE, 650, 170)
            draw_text(screen, f"Player 1 Health: {player1_health}", SMALL_FONT, WHITE, 650, 255)
            draw_text(screen, f"Player 2 Health: {player2_health}", SMALL_FONT, WHITE, 650, 295)
            draw_text(screen, f"Time Left: {time_left}", SMALL_FONT, WHITE, 650, 335)
            draw_text(screen, "Spectator Mode", SMALL_FONT, YELLOW, 650, 500)
            return
        if player_number == 1:
            your_label = f"You: {username} (Player 1)"
            opp_label = f"Opponent: {opponent} (Player 2)"
        else:
            your_label = f"You: {username} (Player 2)"
            opp_label = f"Opponent: {opponent} (Player 1)"

        draw_text(screen, your_label, SMALL_FONT, WHITE, 650, 170)
        draw_text(screen, opp_label, SMALL_FONT, WHITE, 650, 205)

        draw_text(screen, f"Player 1 Health: {player1_health}", SMALL_FONT, WHITE, 650, 255)
        draw_text(screen, f"Player 2 Health: {player2_health}", SMALL_FONT, WHITE, 650, 295)
        draw_text(screen, f"Time Left: {time_left}", SMALL_FONT, WHITE, 650, 335)
    else:
        draw_text(screen, f"Player 1 Health: {player1_health}", SMALL_FONT, WHITE, 650, 190)
        draw_text(screen, f"Player 2 Health: {player2_health}", SMALL_FONT, WHITE, 650, 230)
        draw_text(screen, f"Time Left: {time_left}", SMALL_FONT, WHITE, 650, 270)
        if player1_frozen:
            draw_text(screen, "Player 1 is frozen!", SMALL_FONT, CYAN, 650, 320)

        if player2_frozen:
            draw_text(screen, "Player 2 is frozen!", SMALL_FONT, CYAN, 650, 360)
        if player1_confused:
            draw_text(screen, "Player 1 controls reversed!", SMALL_FONT, YELLOW, 650, 400)

        if player2_confused:
            draw_text(screen, "Player 2 controls reversed!", SMALL_FONT, YELLOW, 650, 440)

    draw_text(screen, "Controls:", SMALL_FONT, WHITE, 650, 460)
    draw_text(screen, "UP / DOWN / LEFT / RIGHT", SMALL_FONT, WHITE, 650, 500)

def draw_game_state(screen, state, match_info=None, chat_messages=None, chat_input="", chat_typing=False, chat_input_rect=None): #draw snakes, board, food, powerups, UI panels, and chat window
    screen.fill(BLACK)
    board_width = state.get("board_width", DEFAULT_BOARD_WIDTH)
    board_height = state.get("board_height", DEFAULT_BOARD_HEIGHT)
    snake1 = state.get("snake1", [])
    snake2 = state.get("snake2", [])
    pies = state.get("pies", [])
    powerups = state.get("powerups", [])
    obstacles = state.get("obstacles", [])
    snake1_color = state.get("snake1_color", GREEN)
    snake2_color = state.get("snake2_color", BLUE)
    draw_text(screen, "Snake Game", FONT, WHITE, 40, 30)
    draw_board(screen, board_width, board_height)
    draw_grid(screen, board_width, board_height)
    draw_snake(screen, snake1, snake1_color)
    draw_snake(screen, snake2, snake2_color)
    if match_info is not None:
        if match_info.get("mode") == "player":
            username = match_info.get("username", "You")
            opponent = match_info.get("opponent", "Opponent")
            player_number = match_info.get("player_number", 1)

            if player_number == 1:
                name1 = username
                name2 = opponent
            else:
                name1 = opponent
                name2 = username

            draw_snake_label(screen, snake1, name1, snake1_color, y_offset=-8)
            draw_snake_label(screen, snake2, name2, snake2_color, y_offset=8)

        elif match_info.get("mode") == "spectator":
            name1 = match_info.get("player1_name", "Player 1")
            name2 = match_info.get("player2_name", "Player 2")

            draw_snake_label(screen, snake1, name1, snake1_color, y_offset=-8)
            draw_snake_label(screen, snake2, name2, snake2_color, y_offset=8)
    draw_pies(screen, pies)
    draw_powerups(screen, powerups)
    draw_obstacles(screen, obstacles)
    draw_side_panel(screen, state, match_info)
    if chat_messages is None:
        chat_messages = []
    if chat_input_rect is not None:
        draw_chat_panel(screen, chat_messages, chat_input, chat_typing, chat_input_rect)

def draw_powerups(screen, powerups):
    for powerup in powerups:
        x, y = powerup["pos"]
        powerup_type = powerup["type"]

        center_x = BOARD_X + x * CELL_SIZE + CELL_SIZE // 2
        center_y = BOARD_Y + y * CELL_SIZE + CELL_SIZE // 2

        if powerup_type == "FREEZE":
            pygame.draw.circle(screen, CYAN, (center_x, center_y), CELL_SIZE // 3)
            pygame.draw.circle(screen, WHITE, (center_x - 3, center_y - 3), 2)

        elif powerup_type == "CONFUSE":
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), CELL_SIZE // 3)
            pygame.draw.circle(screen, RED, (center_x - 4, center_y - 4), 2)
            pygame.draw.circle(screen, RED, (center_x + 4, center_y + 3), 2)

def draw_waiting_screen(screen, match_info=None):
    screen.fill(BLACK)
    draw_text(screen, "Waiting for game state from server...", FONT, WHITE, 40, 40)

    if match_info is not None and match_info.get("mode") == "spectator":
        draw_text(screen, "Spectator mode: waiting for the live match view...", SMALL_FONT, WHITE, 40, 100)
    else:
        draw_text(screen, "Use arrow keys during the match.", SMALL_FONT, WHITE, 40, 100)

def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = word if current_line == "" else current_line + " " + word

        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line != "":
                lines.append(current_line)
                current_line = ""

            while font.size(word)[0] > max_width:
                piece = ""
                for char in word:
                    test_piece = piece + char
                    if font.size(test_piece)[0] <= max_width:
                        piece = test_piece
                    else:
                        break

                lines.append(piece)
                word = word[len(piece):]

            current_line = word

    if current_line != "":
        lines.append(current_line)

    return lines

def draw_chat_panel(screen, chat_messages, chat_input, chat_typing, chat_input_rect): #displays chat history and input field 
    draw_text(screen, "Chat", FONT, WHITE, 650, 390)

    chat_box_rect = pygame.Rect(640, 430, 400, 180)
    pygame.draw.rect(screen, (40, 40, 40), chat_box_rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, chat_box_rect, 2, border_radius=8)

    max_text_width = chat_box_rect.width - 20
    all_lines = []

    for msg in chat_messages:
        wrapped_lines = wrap_text(msg, SMALL_FONT, max_text_width)
        all_lines.extend(wrapped_lines)

    line_height = 30
    max_visible_lines = (chat_box_rect.height - 20) // line_height
    visible_lines = all_lines[-max_visible_lines:]

    start_y = chat_box_rect.y + 10
    for i, line in enumerate(visible_lines):
        draw_text(screen, line, SMALL_FONT, WHITE, chat_box_rect.x + 10, start_y + i * line_height)

    pygame.draw.rect(screen, (40, 40, 40), chat_input_rect, border_radius=8)
    border_color = YELLOW if chat_typing else WHITE
    pygame.draw.rect(screen, border_color, chat_input_rect, 2, border_radius=8)

    if chat_typing:
        display_text = chat_input
        text_color = YELLOW
    else:
        display_text = chat_input if chat_input else "Click here to type"
        text_color = GRAY

    input_lines = wrap_text(display_text, SMALL_FONT, chat_input_rect.width - 20)
    input_display = input_lines[-1] if input_lines else ""

    draw_text(screen, input_display, SMALL_FONT, text_color, chat_input_rect.x + 10, chat_input_rect.y + 8) #displays the winner + countdown back to lobby

def draw_game_over_screen(screen, state, match_info=None, seconds_left=5):
    screen.fill(BLACK)

    card_w = 620
    card_h = 360
    card_x = (WIDTH - card_w) // 2
    card_y = (HEIGHT - card_h) // 2

    draw_center_card(screen, card_x, card_y, card_w, card_h)

    winner = state.get("winner", "No winner")
    player1_health = state.get("player1_health", DEFAULT_STARTING_HEALTH)
    player2_health = state.get("player2_health", DEFAULT_STARTING_HEALTH)

    display_winner = winner

    if match_info is not None:
        if match_info.get("mode") == "player":
            username = match_info.get("username", "You")
            opponent = match_info.get("opponent", "Opponent")
            player_number = match_info.get("player_number", 1)

            if player_number == 1:
                player1_name = username
                player2_name = opponent
            else:
                player1_name = opponent
                player2_name = username

        elif match_info.get("mode") == "spectator":
            player1_name = match_info.get("player1_name", "Player 1")
            player2_name = match_info.get("player2_name", "Player 2")
        else:
            player1_name = "Player 1"
            player2_name = "Player 2"

        if winner == "PLAYER 1":
            display_winner = player1_name
        elif winner == "PLAYER 2":
            display_winner = player2_name
        elif winner == "DRAW":
            display_winner = "Draw"

    draw_text(screen, "Game Over", FONT, WHITE, card_x + 40, card_y + 35)
    draw_text(screen, f"Winner: {display_winner}", FONT, ACCENT, card_x + 40, card_y + 95)

    draw_text(screen, f"Player 1 Health: {player1_health}", SMALL_FONT, MUTED, card_x + 40, card_y + 175)
    draw_text(screen, f"Player 2 Health: {player2_health}", SMALL_FONT, MUTED, card_x + 40, card_y + 215)

    draw_text(screen, f"Returning to lobby in {seconds_left} seconds...", SMALL_FONT, YELLOW, card_x + 40, card_y + 295)


def game_loop(client, match_info=None): #runs main game screen by processing keyboard input 
    #chat setup 
    chat_messages = []
    chat_input = ""
    chat_typing = False
    MAX_CHAT_MESSAGES = 5
    chat_input_rect = pygame.Rect(650, 640, 380, 40)
    MAX_CHAT_LENGTH = 80

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")

    clock = pygame.time.Clock()
    running = True
    latest_state = None
    connection_alive = True
    game_over_time = None
    showing_game_over = False
    disconnected = False
    user_quit = False

    state_lock = threading.Lock()
    handoff_queue = []
    stop_recv = threading.Event() 

    def receive_messages(): #keeps game in sync with the server 
        nonlocal latest_state, running, connection_alive, disconnected, showing_game_over, game_over_time
        while not stop_recv.is_set():
            try:
                message = client.receive_message()
            except (ConnectionAbortedError, ConnectionResetError, OSError):
                connection_alive = False
                disconnected = True
                if not showing_game_over:
                    running = False
                break

            if message is None:
                connection_alive = False
                disconnected = True
                if not showing_game_over:
                    running = False
                break

            msg_type = message.get("type")

            if stop_recv.is_set() or not running:
                with state_lock:
                    handoff_queue.append(message)
                break

            if msg_type == "GAME_START":
                with state_lock:
                    handoff_queue.append(message)
                break
            elif msg_type == "PLAYER_LIST":
                with state_lock:
                    handoff_queue.append(message)
                break
            elif msg_type == "GAME_STATE":
                with state_lock:
                    latest_state = message
            elif msg_type == "GAME_OVER":
                with state_lock:
                    latest_state = message
                    showing_game_over = True
                    game_over_time = pygame.time.get_ticks()
            elif msg_type == "OPPONENT_LEFT":
                running = False
                break
            elif msg_type == "CHAT":
                with state_lock:
                    sender = message.get("from", "Unknown")
                    text = message.get("text", "")
                    full_message = f"{sender}: {text}"
                    chat_messages.append(full_message)
                    if len(chat_messages) > MAX_CHAT_MESSAGES:
                        chat_messages.pop(0)

    recv_thread = threading.Thread(target=receive_messages, daemon=True)
    recv_thread.start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                user_quit = True
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if chat_input_rect.collidepoint(event.pos):
                    chat_typing = True
                else:
                    chat_typing = False
            if event.type == pygame.KEYDOWN:
                if chat_typing:
                    if event.key == pygame.K_RETURN:
                        if chat_input.strip():
                            client.send_message({
                                "type": "CHAT",
                                "text": chat_input.strip()
                            })
                        chat_input = ""
                        chat_typing = False

                    elif event.key == pygame.K_ESCAPE:
                        chat_input = ""
                        chat_typing = False

                    elif event.key == pygame.K_BACKSPACE:
                        chat_input = chat_input[:-1]

                    else:
                        if len(chat_input) < MAX_CHAT_LENGTH and event.unicode.isprintable():
                            chat_input += event.unicode

                else:
                    if match_info is not None and match_info.get("mode") == "spectator":
                        pass
                    else:
                        if event.key == pygame.K_UP:
                            client.send_message({"type": "MOVE", "direction": "UP"})
                        elif event.key == pygame.K_DOWN:
                            client.send_message({"type": "MOVE", "direction": "DOWN"})
                        elif event.key == pygame.K_LEFT:
                            client.send_message({"type": "MOVE", "direction": "LEFT"})
                        elif event.key == pygame.K_RIGHT:
                            client.send_message({"type": "MOVE", "direction": "RIGHT"})

        with state_lock:
            current_state = latest_state.copy() if latest_state is not None else None

        if current_state is not None:
            if showing_game_over or current_state.get("game_over", False):
                if not showing_game_over:
                    showing_game_over = True
                    game_over_time = pygame.time.get_ticks()

                elapsed = pygame.time.get_ticks() - game_over_time
                seconds_left = max(0, 5 - elapsed // 1000)

                draw_game_over_screen(screen, current_state, match_info, seconds_left)

                #return to lobby after 5 seconds from the game ending
                if pygame.time.get_ticks() - game_over_time >= 5000:
                    running = False
            else:
                draw_game_state(screen, current_state, match_info, chat_messages, chat_input, chat_typing, chat_input_rect)
        else:
            draw_waiting_screen(screen, match_info)

        pygame.display.flip()
        clock.tick(60)

    stop_recv.set()
    recv_thread.join(timeout=2.0)

    with state_lock:
        pending = list(handoff_queue)

    if user_quit:
        return "quit", pending
    if disconnected:
        return "disconnected", pending
    return "game_over", pending