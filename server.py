import socket
import json
import threading
import sys
import random
import time


class GameState:
    def __init__(self):
        self.reset_state()

    def reset_state(self): #sets the entire game back to default values
        self.board_width = 20
        self.board_height = 20

        self.snake1 = [(3, 10), (2, 10), (1, 10)]
        self.snake2 = [(16, 10), (17, 10), (18, 10)]

        self.snake1_direction = "RIGHT"
        self.snake2_direction = "LEFT"

        self.pies = []
        self.obstacles = []


        self.player1_health = 100
        self.player2_health = 100

        self.time_left = 60

        self.game_over = False
        self.winner = None

        self.snake1_color = (0, 255, 0)
        self.snake2_color = (0, 0, 255)

        self.powerups = []
        #effect timers
        self.player1_frozen_until = 0
        self.player2_frozen_until = 0
        self.player1_confused_until = 0
        self.player2_confused_until = 0

    def generate_pie(self): #spawns food in available spaces 
        while True:
            x = random.randint(0, self.board_width - 1)
            y = random.randint(0, self.board_height - 1)
            new_pie = (x, y)
            if (
                new_pie not in self.snake1
                and new_pie not in self.snake2
                and new_pie not in self.pies
                and new_pie not in self.obstacles
            ):
                self.pies.append(new_pie)
                break
    
    def generate_powerup(self): #spawns a random powerup (freeze or confuse) in available spaces
        while True:
            x = random.randint(0, self.board_width - 1)
            y = random.randint(0, self.board_height - 1)
            new_powerup = (x, y)

            occupied_by_powerup = any(p["pos"] == new_powerup for p in self.powerups)

            if (
                new_powerup not in self.snake1
                and new_powerup not in self.snake2
                and new_powerup not in self.pies
                and new_powerup not in self.obstacles
                and not occupied_by_powerup
            ):
                powerup_type = random.choice(["FREEZE", "CONFUSE"])

                self.powerups.append({
                    "pos": new_powerup,
                    "type": powerup_type
                })
                break

    def generate_obstacles(self): #places obstacles on the board
        self.obstacles = [(8, 8), (8, 9), (8, 10), (12, 8), (12, 9), (12, 10)]

    def change_direction(self, player, new_direction): #updates snake direction while preventing immediate reversing 
        opposite = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT"
        }

        if player == 1:
            if new_direction != opposite[self.snake1_direction]:
                self.snake1_direction = new_direction

        elif player == 2:
            if new_direction != opposite[self.snake2_direction]:
                self.snake2_direction = new_direction

    def get_new_head(self, snake, direction): #calculates next head position based on direction
        head_x, head_y = snake[0]
        if direction == "UP":
            return (head_x, head_y - 1)
        elif direction == "DOWN":
            return (head_x, head_y + 1)
        elif direction == "LEFT":
            return (head_x - 1, head_y)
        elif direction == "RIGHT":
            return (head_x + 1, head_y)

    def move_snake(self, player): #moves snake forward and grows it if any pies are eaten
        if player == 1:
            new_head = self.get_new_head(self.snake1, self.snake1_direction)
            self.snake1.insert(0, new_head)
            if new_head in self.pies:
                self.pies.remove(new_head)
                self.player1_health += 10
                self.generate_pie()
            else:
                self.snake1.pop()
        elif player == 2:
            new_head = self.get_new_head(self.snake2, self.snake2_direction)
            self.snake2.insert(0, new_head)
            if new_head in self.pies:
                self.pies.remove(new_head)
                self.player2_health += 10
                self.generate_pie()
            else:
                self.snake2.pop()

    def check_collisions(self): #detects all types of collisions (walls, obstacles, self, opponent) and thus decreasing health
        head1 = self.snake1[0]
        head2 = self.snake2[0]

        player1_collision = False
        player2_collision = False

        #walls
        if head1[0] < 0 or head1[0] >= self.board_width or head1[1] < 0 or head1[1] >= self.board_height:
            player1_collision = True
        if head2[0] < 0 or head2[0] >= self.board_width or head2[1] < 0 or head2[1] >= self.board_height:
            player2_collision = True
        #obstacles, self, opponent
        if head1 in self.obstacles:
            player1_collision = True
        if head2 in self.obstacles:
            player2_collision = True
        if head1 in self.snake1[1:]:
            player1_collision = True
        if head2 in self.snake2[1:]:
            player2_collision = True
        if head1 in self.snake2:
            player1_collision = True
        if head2 in self.snake1:
            player2_collision = True
        if head1 == head2:
            player1_collision = True
            player2_collision = True

        if player1_collision:
            self.player1_health -= 20
        if player2_collision:
            self.player2_health -= 20
        if self.player1_health < 0:
            self.player1_health = 0
        if self.player2_health < 0:
            self.player2_health = 0

        return {
            "player1_collision": player1_collision,
            "player2_collision": player2_collision
        }

    def check_game_over(self): #determines if the match has ended and declares winner
        if self.player1_health <= 0 and self.player2_health <= 0:
            self.game_over = True
            self.winner = "DRAW"
        elif self.player1_health <= 0:
            self.game_over = True
            self.winner = "PLAYER 2"
        elif self.player2_health <= 0:
            self.game_over = True
            self.winner = "PLAYER 1"
        elif self.time_left <= 0:
            self.game_over = True
            if self.player1_health > self.player2_health:
                self.winner = "PLAYER 1"
            elif self.player2_health > self.player1_health:
                self.winner = "PLAYER 2"
            else:
                self.winner = "DRAW"

    def get_state(self): #sends updated game states to clients
        return {
            "board_width": self.board_width,
            "board_height": self.board_height,
            "snake1": self.snake1,
            "snake2": self.snake2,
            "snake1_direction": self.snake1_direction,
            "snake2_direction": self.snake2_direction,
            "pies": self.pies,
            "powerups": self.powerups,
            "obstacles": self.obstacles,
            "player1_health": self.player1_health,
            "player2_health": self.player2_health,
            "time_left": self.time_left,
            "game_over": self.game_over,
            "winner": self.winner,
            "snake1_color": self.snake1_color,
            "snake2_color": self.snake2_color,
            "player1_frozen": time.monotonic() < self.player1_frozen_until,
            "player2_frozen": time.monotonic() < self.player2_frozen_until,
            "player1_confused": time.monotonic() < self.player1_confused_until,
            "player2_confused": time.monotonic() < self.player2_confused_until
        }
    
    def check_powerup_collection(self, player): #applies powerup effects if collected
        if player == 1:
            head = self.snake1[0]

            for powerup in self.powerups:
                if powerup["pos"] == head:
                    if powerup["type"] == "FREEZE":
                        self.player2_frozen_until = time.monotonic() + 3
                    elif powerup["type"] == "CONFUSE":
                        self.player1_confused_until = time.monotonic() + 3

                    self.powerups.remove(powerup)
                    self.generate_powerup()
                    break

        elif player == 2:
            head = self.snake2[0]

            for powerup in self.powerups:
                if powerup["pos"] == head:
                    if powerup["type"] == "FREEZE":
                        self.player1_frozen_until = time.monotonic() + 3
                    elif powerup["type"] == "CONFUSE":
                        self.player2_confused_until = time.monotonic() + 3

                    self.powerups.remove(powerup)
                    self.generate_powerup()
                    break

    def reverse_direction(self, direction): #reverses movement direction (caused by the confuse pie)
        reverse_map = {
                "UP": "DOWN",
                "DOWN": "UP",
                "LEFT": "RIGHT",
                "RIGHT": "LEFT"
            }
        return reverse_map.get(direction, direction)


#server setup
HOST = "0.0.0.0"
PORT = 5000

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])

clients = {}
online_users = []
player_state = {}

current_game = None
current_players = {}
match_start_time = None
MATCH_DURATION = 60
current_spectators = set()
state_lock = threading.Lock()


def send_json(sock, data): #sends JSON message to client socket
    try:
        message = json.dumps(data) + "\n"
        sock.sendall(message.encode())
    except:
        pass


def recv_json(sock_file): #receives JSON from client socket
    try:
        line = sock_file.readline()
        if not line:
            return None
        return json.loads(line.strip())
    except:
        return None


def build_player_list(exclude_username=None): #builds lobby player list
    players = []
    for username in clients.keys():
        if username == exclude_username:
            continue
        if username in current_players:
            status = "BUSY"
        else:
            status = "AVAILABLE"
        players.append({
            "username": username,
            "status": status
        })
    return players


def broadcast_player_list(): #sends updated lobby to all connected client
    snapshot = dict(clients) 
    for username, sock in snapshot.items():
        players = build_player_list(exclude_username=username)
        try:
            send_json(sock, {
                "type": "PLAYER_LIST",
                "players": players
            })
        except:
            pass


def send_player_list_to(username): 
    if username not in clients:
        return
    players = build_player_list(exclude_username=username)
    send_json(clients[username], {
        "type": "PLAYER_LIST",
        "players": players
    })


def notify_previous_waiters(chosen_player, new_opponent):
    for username, state in player_state.items():
        if username == chosen_player:
            continue
        if state.get("opponent") == chosen_player and state.get("ready"):
            if new_opponent != username:
                if username in clients:
                    send_json(clients[username], {
                        "type": "NOT_CHOSEN_BACK",
                        "opponent": chosen_player
                    })
                player_state[username]["opponent"] = None
                player_state[username]["ready"] = False


def send_state_to_match_players(message_type="GAME_STATE"): #sends current game state to all players and spectators
    global current_game, current_players, current_spectators

    if current_game is None:
        return

    updated_state = current_game.get_state()

    recipients = list(current_players.keys()) + list(current_spectators)

    for username in recipients:
        if username in clients:
            send_json(clients[username], {
                "type": message_type,
                **updated_state
            })


def create_match(player1, player2): #initializes a new game between two players
    global current_game, current_players, match_start_time

    with state_lock:
        current_game = GameState()
        current_game.generate_obstacles()
        for _ in range(6):
            current_game.generate_pie()
        for _ in range(5):   
            current_game.generate_powerup()

        match_start_time = time.monotonic()
        current_game.time_left = MATCH_DURATION

        current_players = {
            player1: 1,
            player2: 2
        }

        player1_color = player_state.get(player1, {}).get("snake_color")
        player2_color = player_state.get(player2, {}).get("snake_color")

        if player1_color is not None:
            current_game.snake1_color = tuple(player1_color)
        if player2_color is not None:
            current_game.snake2_color = tuple(player2_color)

    send_json(clients[player1], {
        "type": "GAME_START",
        "opponent": player2,
        "player_number": 1
    })

    send_json(clients[player2], {
        "type": "GAME_START",
        "opponent": player1,
        "player_number": 2
    })

    send_state_to_match_players("GAME_STATE")
    broadcast_player_list()

    threading.Thread(target=run_match_timer, daemon=True).start()


def reset_match_state():
    global current_game, current_players, current_spectators, match_start_time

    for player_name in current_players:
        if player_name in player_state:
            player_state[player_name]["opponent"] = None
            player_state[player_name]["ready"] = False

    current_game = None
    current_players = {}
    current_spectators = set()
    match_start_time = None


def run_match_timer():
    global current_game

    last_sent_time = None

    while True:
        time.sleep(0.1)

        with state_lock:
            if current_game is None:
                break
            if current_game.game_over:
                break
            if match_start_time is None:
                break

            elapsed_time = time.monotonic() - match_start_time
            current_game.time_left = max(0, int(MATCH_DURATION - elapsed_time))
            current_game.check_game_over()

            game_is_over = current_game.game_over
            current_time_left = current_game.time_left

        if current_time_left != last_sent_time:
            last_sent_time = current_time_left
            send_state_to_match_players("GAME_STATE")

        if game_is_over:
            send_state_to_match_players("GAME_OVER")
            with state_lock:
                reset_match_state()
            broadcast_player_list()
            break


def handle_client(client_socket, addr): #handles communication with a single client (username setup, matchmaking, moves, chat, disconnection)
    global current_game, current_players

    print(f"Connection from {addr}")

    client_file = client_socket.makefile("r")
    username = None

    try:
        while True:
            msg = recv_json(client_file)

            if msg is None:
                break

            msg_type = msg.get("type")

            #username handling
            if msg_type == "USERNAME":
                requested_username = msg.get("username")

                if not requested_username:
                    continue

                with state_lock:
                    if requested_username in clients or requested_username in online_users:
                        username_taken = True
                    else:
                        username_taken = False
                        username = requested_username
                        clients[username] = client_socket
                        online_users.append(username)
                        player_state[username] = {
                            "opponent": None,
                            "ready": False,
                            "snake_style": None,
                            "snake_color": None
                        }

                if username_taken:
                    send_json(client_socket, {"type": "USERNAME_TAKEN"})
                    continue

                send_json(client_socket, {"type": "USERNAME_OK"})
                broadcast_player_list()

            elif msg_type == "PLAYER_SETUP":
                if username is None:
                    continue
                with state_lock:
                    if username in player_state:
                        player_state[username]["snake_style"] = msg.get("snake_style")
                        player_state[username]["snake_color"] = msg.get("snake_color")

            elif msg_type == "REQUEST_PLAYER_LIST":
                if username is not None:
                    send_player_list_to(username)

            #matchmaking
            elif msg_type == "CHOOSE_OPPONENT":
                opponent = msg.get("opponent")
                should_create_match = False
                waiting_for_mutual = False
                game_busy = False

                with state_lock:
                    if username not in player_state:
                        continue
                    if opponent not in clients:
                        continue
                    if opponent == username:
                        continue

                    if opponent in current_players:
                        game_busy = True
                    else:
                        notify_previous_waiters(username, opponent)
                        player_state[username]["opponent"] = opponent
                        player_state[username]["ready"] = True

                        if (
                            player_state.get(opponent, {}).get("opponent") == username
                            and player_state[opponent]["ready"]
                        ):
                            if current_game is not None and not current_game.game_over:
                                game_busy = True
                            else:
                                should_create_match = True
                        else:
                            waiting_for_mutual = True

                if game_busy:
                    send_json(client_socket, {"type": "GAME_BUSY"})
                    continue

                if waiting_for_mutual:
                    send_json(client_socket, {
                        "type": "WAITING_FOR_OPPONENT",
                        "opponent": opponent
                    })

                if should_create_match:
                    create_match(username, opponent)

            elif msg_type == "WATCH_MATCH":
                with state_lock:
                    if username is None:
                        continue
                    if current_game is None:
                        send_json(client_socket, {"type": "NO_MATCH_TO_WATCH"})
                        continue
                    if username in current_players:
                        continue

                    current_spectators.add(username)

                    player_names = list(current_players.keys())
                    if len(player_names) == 2:
                        player1_name = player_names[0]
                        player2_name = player_names[1]
                    else:
                        player1_name = "Player 1"
                        player2_name = "Player 2"

                send_json(client_socket, {
                    "type": "GAME_START",
                    "mode": "spectator",
                    "player1_name": player1_name,
                    "player2_name": player2_name
                })

                send_state_to_match_players("GAME_STATE")

            #movement
            elif msg_type == "MOVE":
                direction = msg.get("direction")

                with state_lock:
                    if current_game is None:
                        continue
                    if username not in current_players:
                        continue

                    player_number = current_players[username]
                    now = time.monotonic()

                    if player_number == 1 and now < current_game.player1_frozen_until:
                        continue

                    if player_number == 2 and now < current_game.player2_frozen_until:
                        continue

                    if player_number == 1 and now < current_game.player1_confused_until:
                        direction = current_game.reverse_direction(direction)

                    if player_number == 2 and now < current_game.player2_confused_until:
                        direction = current_game.reverse_direction(direction)

                    current_game.change_direction(player_number, direction)

                    old_snake1 = current_game.snake1[:]
                    old_snake2 = current_game.snake2[:]

                    current_game.move_snake(player_number)
                    current_game.check_powerup_collection(player_number)
                    collision_result = current_game.check_collisions()

                    if collision_result["player1_collision"]:
                        current_game.snake1 = old_snake1
                    if collision_result["player2_collision"]:
                        current_game.snake2 = old_snake2

                    current_game.check_game_over()
                    game_is_over = current_game.game_over

                send_state_to_match_players("GAME_STATE")

                if game_is_over:
                    send_state_to_match_players("GAME_OVER")
                    with state_lock:
                        reset_match_state()
                    broadcast_player_list()

            #chat
            elif msg_type == "CHAT":
                text = msg.get("text", "").strip()

                if not text:
                    continue

                with state_lock:
                    if current_game is None:
                        continue

                    if username not in current_players and username not in current_spectators:
                        continue

                    recipients = list(current_players.keys()) + list(current_spectators)

                for player_name in recipients:
                    if player_name in clients:
                        send_json(clients[player_name], {
                            "type": "CHAT",
                            "from": username,
                            "text": text
                        })

    finally: #cleanup when client disconnects
        in_match = False
        remaining_players = []

        with state_lock:
            if username:
                clients.pop(username, None)
                online_users[:] = [u for u in online_users if u != username]
                player_state.pop(username, None)
                current_spectators.discard(username)

            if username and username in current_players:
                in_match = True
                remaining_players = list(current_players.keys())
                reset_match_state()

        if in_match:
            for player_name in remaining_players:
                if player_name != username and player_name in clients:
                    send_json(clients[player_name], {"type": "OPPONENT_LEFT"})

        client_file.close()
        client_socket.close()
        broadcast_player_list()


def main(): #starts TCP server and accepts incoming connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Server running on port {PORT}")

    while True:
        client_socket, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(client_socket, addr),
            daemon=True
        ).start()


if __name__ == "__main__":
    main()