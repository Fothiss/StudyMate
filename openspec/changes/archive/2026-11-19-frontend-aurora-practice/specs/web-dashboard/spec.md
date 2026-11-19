# Spec Delta

## MODIFIED Requirements

### Requirement: User Identity In Header

The client SHALL show the login of the signed-in user and a sign-out control in the application shell of every authenticated page.

#### Scenario: Login is shown

- **WHEN** the dashboard renders for a signed-in user
- **THEN** the shell shows the `username` returned by `/users/me`

#### Scenario: Profile cannot be read

- **WHEN** `/users/me` answers `401`
- **THEN** the session is cleared and the browser moves to `/login`

## REMOVED Requirements

### Requirement: Quiz Generation From Dashboard

**Reason**: Generation moves to a dedicated practice page (`web-quiz`), so the dashboard no longer selects a material, generates a test or renders questions inline. Every scenario this requirement covered is preserved there, in a form that also lets the user choose how many and which kinds of questions to produce.

**Migration**: Open the practice page from the dashboard and configure the test there. No stored data is involved: generated tests were transient and are not migrated.

## ADDED Requirements

### Requirement: Practice Entry Point

The dashboard SHALL offer a primary control that opens the practice page, and SHALL show it whether or not the user owns materials.

#### Scenario: Control is present

- **WHEN** the dashboard renders
- **THEN** a control leading to the practice page is visible

#### Scenario: No materials yet

- **WHEN** the user owns no materials
- **THEN** the control is still present and the practice page itself explains that a material must be uploaded first

### Requirement: Application Navigation

The client SHALL present one persistent navigation shell on every authenticated page, naming at least the dashboard and the practice page, and SHALL mark the entry of the page currently shown.

#### Scenario: Entries are visible

- **WHEN** any authenticated page renders
- **THEN** the dashboard entry and the practice entry are both shown

#### Scenario: Current page is marked

- **WHEN** the user is on the practice page
- **THEN** the practice entry is visually marked as the current one

#### Scenario: Navigation outlives page changes

- **WHEN** the user moves between authenticated pages
- **THEN** the shell is neither removed nor rebuilt and keeps its state

### Requirement: Theme Selection

The client SHALL let the user switch between a dark and a light theme, SHALL keep the chosen theme across reloads, and SHALL fall back to the operating system preference when the user has not chosen one.

#### Scenario: Switching themes

- **WHEN** the user activates the theme control
- **THEN** the colours change immediately without a page reload

#### Scenario: Choice is kept

- **WHEN** a user who chose a theme reloads any page
- **THEN** the chosen theme is applied

#### Scenario: No choice made

- **WHEN** the user has never chosen a theme
- **THEN** the theme follows the operating system preference
