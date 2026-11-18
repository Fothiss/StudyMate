# user-auth Specification

## Purpose

Lets a user create their own account and reach only their own data through a token, so every later request resolves to an unambiguous owner.

## Requirements

### Requirement: Account Registration

The system SHALL create a user from a unique `username` and a password of at least 8 characters, and SHALL return the created account without any secret fields.

#### Scenario: Successful registration

- **WHEN** `POST /auth/register` receives a free `username` and a password of at least 8 characters
- **THEN** the system responds with `201` and a body containing `id`, `username` and `created_at`

#### Scenario: Username already taken

- **WHEN** the submitted `username` already exists
- **THEN** the system responds with `409` and no new account is created

#### Scenario: Password too short

- **WHEN** the submitted password is shorter than 8 characters
- **THEN** the system responds with `422` and no account is created

#### Scenario: Required field missing

- **WHEN** the request lacks `username` or password
- **THEN** the system responds with `422` and no account is created

### Requirement: Password Protection

The system SHALL store only an irreversible hash of the password and MUST NOT return the password or its hash in any API response.

#### Scenario: Hash never appears in a response

- **WHEN** a client receives user data from any endpoint
- **THEN** the response body contains no password or password-hash field

#### Scenario: No plaintext password at rest

- **WHEN** an account has been created
- **THEN** the stored password value differs from the password the user submitted

### Requirement: Access Token Issuance

The system SHALL issue an access token for valid credentials and SHALL reject invalid ones without revealing whether the given user exists.

#### Scenario: Successful login

- **WHEN** `POST /auth/login` receives a valid `username` and password
- **THEN** the system responds with `200` and a JSON body containing `access_token` and `token_type` equal to `bearer`

#### Scenario: Wrong password

- **WHEN** the password does not match the stored one
- **THEN** the system responds with `401` and no token

#### Scenario: Unknown user

- **WHEN** the submitted `username` does not exist
- **THEN** the system responds with `401` and the same body as for a wrong password

### Requirement: Authenticated Access

The system SHALL require a valid bearer token on protected endpoints and SHALL determine the user solely from the token contents.

#### Scenario: Valid token

- **WHEN** a request carries `Authorization: Bearer <valid token>`
- **THEN** the request is processed as the token owner

#### Scenario: Missing token

- **WHEN** a protected endpoint is called without an `Authorization` header
- **THEN** the system responds with `401`

#### Scenario: Invalid or expired token

- **WHEN** the token has a bad signature, has expired or belongs to a deleted user
- **THEN** the system responds with `401`

#### Scenario: User cannot be overridden by request data

- **WHEN** the client sends someone else's user identifier in the body or query string
- **THEN** the system still operates on the user taken from the token

### Requirement: Current User Profile

The system SHALL return the data of the user identified by the presented token.

#### Scenario: Read own profile

- **WHEN** `GET /users/me` receives a valid token
- **THEN** the system responds with `200` and a body containing `id`, `username` and `created_at`
