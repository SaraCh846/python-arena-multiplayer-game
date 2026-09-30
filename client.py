from gui import connect_gui, lobby_gui, game_loop
import pygame


def main():
    client = connect_gui() #connects the player to server

    if client is None: #if no connection, exit
        return

    try:
        current_username = None #storing active usernames
        seeded_messages = None #passing messages from game back to lobby

        while True:
            lobby_result = lobby_gui(client, current_username, seeded_messages=seeded_messages) #handles matchmaking and player selection
            seeded_messages = None #clear after usage to avoid duplicates

            if lobby_result is None: #if user exits lobby, terminate
                break

            current_username = lobby_result["username"] #update current username

            result, handoff = game_loop(client, lobby_result)

            if result == "quit": #if user quits
                break
            elif result == "disconnected": #connection to server lost
                break
            elif result == "game_over": #normal game case
                seeded_messages = handoff #pass remaining server messages back to lobby
                continue #return back to lobby for next match

    finally: #smooth network + game shutdown
        client.close()
        pygame.quit()


if __name__ == "__main__":
    main()