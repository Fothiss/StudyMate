# web-dashboard Specification

## Purpose

Gives a signed-in user one screen that shows what they have already uploaded, lets them add more, and names the parts of the product that do not exist yet instead of offering controls that cannot work.

## Requirements

### Requirement: Materials Summary

The client SHALL show on the dashboard how many materials the user owns and which of them were uploaded most recently.

#### Scenario: User has materials

- **WHEN** the dashboard renders for a user who owns materials
- **THEN** the materials block shows the total count and the most recent items with their title and upload date

#### Scenario: Newest first

- **WHEN** the user owns several materials
- **THEN** they are listed newest first

#### Scenario: List updates after upload

- **WHEN** a material is uploaded from the dashboard
- **THEN** the new material appears in the list and the count increases without a page reload

### Requirement: Empty Materials State

The client SHALL show an explanatory empty state instead of a blank list when the user has no materials.

#### Scenario: No materials

- **WHEN** the user owns no materials
- **THEN** the materials block shows a zero count, an explanation that materials can be added, and the upload control

#### Scenario: Loading is not empty

- **WHEN** the materials request has not finished yet
- **THEN** the empty state is not shown

### Requirement: Material Upload From Dashboard

The client SHALL let an authenticated user upload a `.pdf`, `.docx` or `.pptx` file together with a title directly from the dashboard.

#### Scenario: Successful upload

- **WHEN** the user submits a supported file and a non-empty title
- **THEN** the material is accepted and appears in the materials block

#### Scenario: Unsupported file type

- **WHEN** the API answers `415`
- **THEN** the block shows a readable message naming the accepted formats and the list is unchanged

#### Scenario: File too large

- **WHEN** the API answers `413`
- **THEN** the block shows a readable message naming the size limit and the list is unchanged

#### Scenario: Empty title

- **WHEN** the title is empty
- **THEN** the client reports it next to the field and sends no request

#### Scenario: Original filename is shown

- **WHEN** a material is listed
- **THEN** the original filename the user uploaded is displayed with it

### Requirement: Unavailable Sections Explained

The client SHALL present the tests and results sections as unavailable and SHALL NOT offer controls in them that cannot work.

#### Scenario: Tests section

- **WHEN** the dashboard renders
- **THEN** the tests section explains that tests appear once questions can be generated from a material and contains no actionable control

#### Scenario: Results section

- **WHEN** the dashboard renders
- **THEN** the results section explains that results appear after a first completed test and contains no actionable control

### Requirement: User Identity In Header

The client SHALL show the login of the signed-in user and a sign-out control in the dashboard header.

#### Scenario: Login is shown

- **WHEN** the dashboard renders for a signed-in user
- **THEN** the header shows the `username` returned by `/users/me`

#### Scenario: Profile cannot be read

- **WHEN** `/users/me` answers `401`
- **THEN** the session is cleared and the browser moves to `/login`

### Requirement: Loading And Failure States

The client SHALL distinguish a pending request from a failed one and SHALL let the user recover from a failure.

#### Scenario: Requests pending

- **WHEN** the dashboard is waiting for the profile or the material list
- **THEN** a loading indication is shown instead of content

#### Scenario: Request fails

- **WHEN** loading the profile or the material list fails with a server error
- **THEN** the dashboard shows a readable message and a control that retries the request
