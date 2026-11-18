# web-session Specification

## Purpose

Lets a visitor create an account, sign in, and keep an authenticated browser session so the rest of the application can act on their behalf and send them back to the sign-in form when that session ends.

## Requirements

### Requirement: Sign-in Form

The client SHALL let a visitor submit a username and password and, on success, SHALL store the returned token and open the dashboard.

#### Scenario: Successful sign-in

- **WHEN** the visitor submits credentials that the API accepts on `/login`
- **THEN** the token is stored and the browser moves to `/`

#### Scenario: Rejected credentials

- **WHEN** the API answers `401` to the sign-in request
- **THEN** the form shows a readable message that the username or password is wrong and no token is stored

#### Scenario: Missing field

- **WHEN** the username or the password field is empty
- **THEN** the form reports the missing field and sends no request

#### Scenario: Request in flight

- **WHEN** a sign-in request is pending
- **THEN** the submit control is disabled so the request cannot be sent twice

### Requirement: Registration Form

The client SHALL let a visitor create an account and SHALL sign the new user in automatically after a successful registration.

#### Scenario: Successful registration

- **WHEN** the visitor submits a free username and a password of at least 8 characters on `/register`
- **THEN** the account is created, the client signs in with the same credentials and the browser moves to `/`

#### Scenario: Username already taken

- **WHEN** the API answers `409`
- **THEN** the form shows a readable message that the username is taken and stays on `/register`

#### Scenario: Rejected input

- **WHEN** the API answers `422`
- **THEN** the form shows a readable validation message and the browser does not move to `/`

### Requirement: Session Persistence

The client SHALL keep the access token across page reloads and SHALL attach it to every request to an endpoint that requires authentication.

#### Scenario: Reload keeps the session

- **WHEN** a signed-in user reloads `/`
- **THEN** the dashboard renders without asking for credentials again

#### Scenario: Token is attached

- **WHEN** the client calls an endpoint that requires authentication
- **THEN** the request carries an `Authorization: Bearer <token>` header

### Requirement: Protected Route Access

The client SHALL deny the dashboard to a visitor without a valid token and SHALL send that visitor to the sign-in form.

#### Scenario: No token

- **WHEN** a visitor opens `/` without a stored token
- **THEN** the browser moves to `/login` and no materials request is sent

#### Scenario: Expired or invalid token

- **WHEN** a request to a protected endpoint answers `401`
- **THEN** the stored token is removed and the browser moves to `/login`

#### Scenario: Already signed in

- **WHEN** a signed-in user opens `/login` or `/register`
- **THEN** the browser moves to `/`

### Requirement: Sign Out

The client SHALL let a signed-in user end the session locally and SHALL remove the stored token.

#### Scenario: Sign out

- **WHEN** the user activates the sign-out control
- **THEN** the stored token is removed and the browser moves to `/login`

#### Scenario: Dashboard closed after sign out

- **WHEN** the user opens `/` after signing out
- **THEN** the browser moves to `/login`
