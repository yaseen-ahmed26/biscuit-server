# Project Notes
Challenges solved, designs notes etc.

### 1. Fixed Issues and Challenges
1. **Type Errors**: In schemas.py, the created_at for all schemas was set to a string, rather than a datetime object itself. Caused the request to fail (500 internal server error) because I was doing .datetime.today() on a field that required a string.

2. **UserUpdate Schema Inheritance**: The UserUpdate schema was inheriting from UserBase, which UserUpdate overrode those fields anyways. Caused weird issues in the Swagger docs like missing fields. So it was changed to just inherit from BaseModel.

3. **Incorrect Dependency Injections**: Dependency Injections only work with HTTP requests and websockets, you can't do it on good old helper functions. So just inject it in the websocket endpoint.

4. **Failing to connect to the websocket**: The original apporach was for the connection manager to be a list of websockets. This would've been fine if it was a global chat or multiplayer game, but because we only want to log in the user on 1 client, it was changed to a dictionary of websockets, each with its own unique session ID.

5. **Cleanup when the websocket closes unexpectedly**: If the user closes their game, it does not remove the database row, meaning it is left behind forever. The fix was to just clean it up in the finally block of the websocket.

6. **Not checking if the new user/email is the same as the old**: Somehow this broke, not sure why. It wasn't checking if the old username is the same as the new one.

7. **Websockets not closing when code is input**: The websocket did not close because originally, I was only deleting it from Python's memory. Must call .close() on the websocket to close it. This is also async so must be done with async def/await.

8. **"Unexpected ASGI message 'websocket.close', after sending 'websocket.close' or response already completed."**: This wsa caused because I was called await websocket.close() twice. Once in the manager.disconnect() and another in the finally block of the try/except. When I manually called manager.disconnect() it also ran the finally block which tried to clsoe the connected again.

9. **Lazy Loading**: FastAPI required some data, but the user object didn't have it. But SQLAlchemy wasn't allowed to load it alongside and so needed a database query.

10. **Remember to add new routers to main.py**: I spent 30 minutes trying to figure out why the /refresh endpoint wasn't working. Only to realise I didn't add it to the main.py.

11. **Paramaters need type hints of defaults**: Got a 422 in /refresh endpoint because there was a param user_info with no default type hint. So Pydantic was confused and FastAPI defaulted it to a query paramter which wasn't in the URL.

12. **Circular imports**: Tried to move the new routers list in main.py to constants.py. Then it created a loop where it loaded codes.py, but during when constants.py wasn't fully initialized. So the imports codes.py got from constants.py haven't been loaded yet. So just keep that routers list in main.py.

13. **Cookie paths matter**: Refresh token path was only set to the /refresh token meaning it wasn't sent to anything else, so the database couldn't delete it. 

---
### 2. Notes
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

- ~~Removed local_id from saves because it wasn't being used. It will be used for sessions instead.~~ 
    - Going back to this original idea. Godot will simply store the local_id (now save_id) locally and use that to get the save data when starting up. The downside is there can only be 1 logged in device at a time, later on this'll change to the new sessions idea.

- Temporarily doing save_id, it's not secure but I will leave it like this for now.

- Should seperate UserBase into GameSave which only contains the game data and SaveBase which has the user_id

- By default, refresh tokens are attached to all API requests which isn't necessary or safe. Restrict the path to only the route it should be attached to, in this case, refresh.

- Also by default, the token will disappear once the user closes the browser which defeats the purpose of refresh tokens. 7 * 24 * 3600 is exactly 7 days.

- ~~No data is needed for /refresh endpoint so can remove the schema. Also, need to check if the refresh token is empty (None)~~
    - Removed.

- Refactor auth/login and auth/refresh to be less duplicated. Can have 2 helpers, one for each token type.

- You can have custom websocket expiry codes. There are specific ranges, 1000-3000 is the standard codes like 1000 for noraml closure. 3000-4000 is for specific libraries or frameworks. Then 4000-5000 is custom codes. Good to have so the client can much easier know what happened rather than trying to parse JSON.
