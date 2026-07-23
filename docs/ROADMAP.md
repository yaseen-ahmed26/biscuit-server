# v2 Roadmap
Rough roadmap of features I would like to implement and how I will. Note that PostgreSQL will also happen but at the very end of v2.

---

#### Quick Overview
**[ ]** = To-do | **[x]** = Complete | **[?]** Under Consideration | **[/]** = In Progress

- [/] Refresh Tokens
- [?] Refresh Tokens for Godot
- [?] Resend Emails
- [ ] Websocket Expiration
- Additional Endpoints
    - [ ] GET save_by_username
    - [ ] GET leaderboard_users

---

#### Timeline

1. implement refresh tokens
this requires a new database table, new endpoints

the website requires a lot of changes. api calls need to be handled in a way where if there is a 401 invalid access token, call the /refresh token, then try the original api request again

/refresh token should be in its own route

3. leaderboards

this should be simple. add a leaderboards endpoint in saves route. returns 10 top most biscuits (keep simple, only have 1 leaderboard)

4. shareable stats link

would need to have another endpoint GET get_save_by_username or similar

5. websocket expiration

easy, just check the current time against the expires_at since we already look out for messages from godot

---

#### Implementation

- **refresh tokens**

create database tables: hashed_token, id, user_id, is_used, expires_at, os, country

have a /refresh endpoint to check refresh tokens:

if token doesn’t exist: 401 (force login)

if token is expired: 401 (force login)

if token is valid, active and not marked: generate a 64 character string, hash it and store it in the database (with SHA-256). send back the raw token as a http cookie

if token is marked: go nuclear and delete every refresh token with the user’s id on it

when the frontend gets a 401 invalid or expired access token, call that /refresh endpoint

server then marks the old one (is_used = true) and issues a new one then return the raw one

*****js must have credentials: true in the request

edit the /token endpoint to also include a refresh token as a cookie

would now need a /logout endpoint to revoke the refresh token

could move login endpoint to a refresh route, which has /login, /logout and /refresh

- **jwt tokens to godot**

can likely just use refresh tokens and it should work the same way

would need to edit get_save endpoint to check for a valid refresh token

this'll be much more secure than passing the save id as a query param, since the refresh token has the user id in the table, we can use that to get the save data though would be slower if there's hundreds of users

- **resend emails (welcome, verify, reset password)**

would need to buy a domain

keep simple for now, just a welcome email

verify email may also be simple. allow the user to login, but not be able to link game until verified

add a is_verified bool to users table

when the user creates the account, send an email containing a unique code attached to the url. when the url is clicked, backend checks to see if valid, and if it is, flip is_verified

would need a verify_sessions table in the database, would also need to hash codes with SHA-256. 

has columns for user_id, hashed_token, expires_at

js would call an endpoint /verify, send the code and backend check if its valid and expired. if its expired, user can just click button again on the website

- **convert to postgresql and alembic**

2 options, either use postgre with docker and switch out the urls or continue to use sqlite locally and only use posrgre for deployment

the latter works but we should mirror production during development as close as possible 

---

SMALL STUFF

- **add websocket expiration time (2 mins)**

simple, since we’re constantly checking to see if the client sent a message, we can also just check the time

compare the expires_at column and the current time, then just close the websocket

---

ADDITIONAL

- **needs a get_save_by_user endpoint**

used by the website for sharable links

- **needs a get_leaderboard_users endpoint**

takes some query params, filter data