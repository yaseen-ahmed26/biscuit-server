# Project Notes
This is some personal notes based off the project. Mix of what things mean, what different tools I'm using do, analogies etc.

---
### TOOLS
**Python**: The programming language

**FastAPI**: The backend framework being used

**SQLite**: The database being used

**SQLAlchemy**: The ORM* used to talk in Python to the database instead of raw SQL

**Pydantic**: FastAPI data validation for data coming in and going out of the backend

---
### PACKAGES
**FastAPI, SQLAlchemy**: ^

**Passlib (Argon2)**: Used for password hashing. Argon2 is the more modern and more resistant to GPU cracking attacks.

**Pyjwt**: Library recommended to use with FastAPI, simple and focused for JWT tokens.

**Nanoid**: Used to generate short codes and IDs.

---
### JARGON
**API (Application Programming Interface)**: The 'waiter' (FastAPI) between the 'kitchen' (database) and the 'customer' (the client, e.g. web, mobile, game)

**Endpoint**: The location where the backend receives API calls for data. It is the specific URL and HTTP method (e.g. GET /api/posts)

***ORM (Object Relational Mapping)**: Instead of writing raw prone-to-error SQL, an ORM (in this case, SQLAlchemy) allows for accessing the database record as though they were regular Python objects. 

**Schemas**: Data blueprints for Pydantic to use

**Models**: A table within the database for holding specific information away from everything else

**Dependency Injection**: A way to tell FastAPI "hey, this function depends on another external tool. Get that tool first before running this". In this case, it'll likely be a database connection or validating tokens

**Session**: A temporary workspace opened to the database for a single request, then is automagically closed

**Authentication**: Answers the question of "Who are you?". Once authenticated (logged in), user receives a token.

**Authorisation**: Answers the question of "What are you allowed to do?". Once a user is logged in, they can only do certain actions. For example, an admin can delete any posts whereas a user can only delete theirs.

**JWT (Json Web Tokens)**: A token given to the frontend client when the user logs in. That token is needed for protected routes, such as updating user settings.

**Password Hashing**: Scramble the password with a unique salt for every different password (even if the password itself is the same)

**Websockets**: A way to have 2 way persistent communication between the client and server. With regular HTTP request, it can only be inititated by the client

---
### HTTP CODES
**200**: (Success) General request was successful

**201**: (Success) A new resource was created

**204**: (Success) No content received

**400**: (Error) The client sent data that the server invalidated

**401**: (Error) "I don't know who you are"

**403**: (Error): You don't have permission to do this

**404**: (Error) Content was not found

**422**: (Error) Request could not be processed due to missing or invalid fields

---
### (FIXED) ISSUES
1. Type Errors
In schemas.py, the created_at for all schemas was set to a string, rather than a datetime object itself. Caused the request to fail (500 internal server error) because I was doing .datetime.today() on a field that required a string.

2. UserUpdate Schema Inheritance
The UserUpdate schema was inheriting from UserBase, which UserUpdate overrode those fields anyways. Caused weird issues in the Swagger docs like missing fields. So it was changed to just inherit from BaseModel.

3. Incorrect Dependency Injections
Dependency Injections only work with HTTP requests and websockets, you can't do it on good old helper functions. So just inject it in the websocket endpoint.

4. Failing to connect to the websocket
The original apporach was for the connection manager to be a list of websockets. This would've been fine if it was a global chat or multiplayer game, but because we only want to log in the user on 1 client, it was changed to a dictionary of websockets, each with its own unique session ID.

5. Cleanup when the websocket closes unexpectedly
If the user closes their game, it does not remove the database row, meaning it is left behind forever. The fix was to just clean it up in the finally block of the websocket.

6. Not checking if the new user/email is the same as the old
Somehow this broke, not sure why. It wasn't checking if the old username is the same as the new one.

7. Websockets not closing when code is input
The websocket did not close because originally, I was only deleting it from Python's memory. Must call .close() on the websocket to close it. This is also async so must be done with async def/await.

8. "Unexpected ASGI message 'websocket.close', after sending 'websocket.close' or response already completed."
This wsa caused because I was called await websocket.close() twice. Once in the manager.disconnect() and another in the finally block of the try/except. When I manually called manager.disconnect() it also ran the finally block which tried to clsoe the connected again.

9. Lazy Loading
FastAPI required some data, but the user object didn't have it. But SQLAlchemy wasn't allowed to load it alongside and so needed a database query.

---
### NOTES
- There cannot be any trailing commas when testing out in Swagger. Gives a 422 JSON Decode error otherwise.
- When adding new fields to SQLite, it is often better to just delete the old database file and let it create a new one. In real production, you'd use migrations so you don't wipe existing user data.
- Never store raw passwords in the database if it gets stolen, bye bye data and hello lawsuits.
- A .env file is for secret environment variables, basically if you have top secret CIA files we don't want people to see. Include in gitignore, that's cruical.
- Difference between encryption and hashing is that the former is reversable, the latter is not. Argon2 generates a differnt salt for every password, the same password can have differnt hashes.
- For security, don't reveal what went wrong when failing to login. Don't which is incorrect (password or email). Or just lie and say the password is incorrect when its the email.
- Best practise to organise routes, with paramiticised ones at the end.
- You have to keep the websocket open, otherwise FastAPI thinks the client is dead. Even if the client is not expected to send anything, we still have to check to keep the connection alive.
- You can in fact do login_code = login_code. Python and SQLAlchemy passed year 8 and can distinguish the difference. This is also standard practicse.
- When verifying the code, we don't need to then delete the database row. When the websocket is closed, it already does it in the finally block of try/except.
- session_id wasn't really needed, since every login code is unique, that can be used as the session ID.
- ~~Removed local_id from saves because it wasn't being used. It will be used for sessions instead.~~ Going back to this original idea. Godot will simply store the local_id (now save_id) locally and use that to get the save data when starting up. The downside is there can only be 1 logged in device at a time, later on this'll change to the new sessions idea.
- Temporarily doing save_id, it's not secure but I will leave it like this for now.
- Should seperate UserBase into GameSave which only contains the game data and SaveBase which has the user_id

---
### MISC
- python -c "import secrets; print(secrets.token_hex(32))"
Run this command in the terminal for a super super secret key.

- JSON Web Tokens (JWT) Structure
It has 3 parts. (1) Header: contains the algorithm and type. (2) Payload: contains the data and expiration. (3) Signature: proves the token wasn't tampered with. Signature is created with our secret key meaning only our server can create valid tokens.

- cascade = "all, delete-orphan"
Doing this in a relationship tells SQLAlchemy to also delete the associated save data. If then that save data becomes an orphan and isn't connected to a user, then delete it. Also automagically saves it to the database when a new save is made.