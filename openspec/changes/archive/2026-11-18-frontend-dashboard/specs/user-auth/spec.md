# Spec Delta

## MODIFIED Requirements

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

### Requirement: Current User Profile

The system SHALL return the data of the user identified by the presented token.

#### Scenario: Read own profile

- **WHEN** `GET /users/me` receives a valid token
- **THEN** the system responds with `200` and a body containing `id`, `username` and `created_at`
