# v2 Roadmap
Rough roadmap of features I would like to implement and how I will. 

Note that PostgreSQL will also happen but at the very end of v2.

Also note that the future features on the README were not final.

---

#### Quick Overview
**[ ]** = To-do | **[✓]** = Complete | **[?]** Under Consideration | **[/]** = In Progress

- [✓] Refresh Tokens
- [?] Refresh Tokens for Godot
- [?] Resend Emails
- [✓] Websocket Expiration
- [✓] Refactor auth router to be less duplicated
- [ ] Boolean if account and game has been linked
- Additional Endpoints
    - [ ] GET save_by_username
    - [✓] GET leaderboard_users
    - [✓] POST logout

---

#### Implementation

FEATURES

1. **Refresh tokens**
- Create a database table.
    - Can have the following: hashed_token, id, user_id, is_used, expires_at, os, country.
    - Storing the OS and country may not be possible, depending on implementation.
- Generate a 64 opaque string, hash it and store it in the database (with SHA-256). Send back the raw token as a HTTP cookie.
- Have a auth/refresh endpoint.
    - If token doesn’t exist: 401 (force login)
    - If token is expired: 401 (force login)
    - If token is valid, active and not marked: issue new token.
    - If a token is marked: delete every entry in the database with the user's ID. This means the account is likely compromsied.
- If a new refresh token is issed, mark the old one (is_used = true). If it is used again, we know the account is compromised.
- *****JavaScript must have credentials: true in the request to recieve cookies.
- Edit the /token endpoint to also include a refresh token as a cookie.
- Would now need a /logout endpoint to revoke the refresh token.
- Could move login endpoint to a refresh route, which has /login, /logout and /refresh.

2. **JWT tokens to godot**
- Can likely just use refresh tokens and it should work the same way.
- Would need to edit get_save endpoint to check for a valid refresh token
    - Access token would contain the user's ID so no ened to store locally.
- Much more reliable than the current save IDs being used.

3. **Resend emails (welcome, verify, reset password)**
- Possible, would need a domain.
- Keep simple for now, just a welcome email.
- A verify email may also be simple. allow the user to login, but not be able to link game until verified.
    - Requires a is_verified bool in the users table.
- When the user creates the account, send an email containing a unique code attached to the URL. 
    - When the URL is clicked, backend checks to see if valid, and if it is, flip is_verified.
- Would need a verify_sessions table in the database, would also need to hash codes with SHA-256. 
    - Some columns can be: user_id, hashed_token, expires_at

4. **Convert to PostgreSQL**
- 2 options, either use PostgreSQL with Docker and switch out the URLs or continue to use SQLite locally and only use PostgreSQL for deployment.
    - The latter works but we should mirror production during development as close as possible.

---

SMALL STUFF

1. **Add websocket expiration time (2 mins)**
- Compare the expires_at column and the current time, then just close the websocket.