# DSShop Server

A open source server, fully customizable.
Authentication is via a code sent by the [DSShop Bot](https://github.com/DSShop/DSShop-Bot).

It contains a Self-Repair tool, if something goes wrong.

### Its made for Linux, but SHOULD also work on Windows. No support is given if running on Windows.

# Requirements:

- a MongoDB database
    - Inside the MongoDB, you need:
        - A database called "dsshop"
            - Create a collection called "serverauth" - You will need this to link your Discord account to the server panel

            - Create a collection called "tips": This will contain tips about the panel or your project - To add a tip, you need the [DSShop Bot](https://github.com/DSShop/DSShop-Bot)

- A Linux machine
    - A Windows machine should also work, but support is only provided for Windows.

- A Discord account to link the panel to
    - This is gonna be removed soon.

- A open web port.
    - This is obviously to host the server.

- Permissions to create folders and save files


# Optional requirements:

- A Discord Webhook
    - This is only if you want Logging of the server and the panel

- A terminal like Windows Terminal, that supports colors
    - If you want a better aspect of the panel

