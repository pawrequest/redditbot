#!/usr/bin/env python
import random
import socket
import sys
import asyncio
import asyncpraw


async def receive_connection():
    """Wait for and then return a connected socket.."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client, _ = await asyncio.get_event_loop().sock_accept(server)
    server.close()
    return client


def send_message(client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode("utf-8"))
    client.close()


async def main():
    """Provide the program's entry point when directly executed."""
    print("Go here while logged into the account you want to create a token for: https://www.reddit.com/prefs/apps/")
    print("Click the create an app button. Put something in the name field and select the script radio button.")
    print("Put http://localhost:8080 in the redirect uri field and click create app")
    client_id = input("Enter the client ID, it's the line just under Personal use script at the top: ")
    client_secret = input("Enter the client secret, it's the line next to secret: ")
    commaScopes = input("Now enter a comma separated list of scopes, or all for all tokens: ")

    if commaScopes.lower() == "all":
        scopes = ["*"]
    else:
        scopes = commaScopes.strip().split(",")

    reddit = asyncpraw.Reddit(
        client_id=client_id.strip(),
        client_secret=client_secret.strip(),
        redirect_uri="http://localhost:8080",
        user_agent="asyncpraw_refresh_token_example",
    )
    state = str(random.randint(0, 65000))
    # url = reddit.auth.reddit_id(scopes, state, "permanent")
    url = reddit.auth.url(scopes, state, "permanent")  # Correct method to get auth URL

    print(f"Now open this url in your browser: {url}")
    sys.stdout.flush()

    client = await receive_connection()
    data = (await asyncio.get_event_loop().sock_recv(client, 1024)).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = {key: value for (key, value) in [token.split("=") for token in param_tokens]}

    if state != params["state"]:
        send_message(
            client,
            f"State mismatch. Expected: {state} Received: {params['state']}",
        )
        return 1
    elif "error" in params:
        send_message(client, params["error"])
        return 1

    refresh_token = await reddit.auth.authorize(params["code"])
    send_message(client, f"Refresh token: {refresh_token}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
