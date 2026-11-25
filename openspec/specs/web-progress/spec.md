# web-progress Specification

## Purpose

Lets a user open the history of completed tests, inspect any past attempt in full and see how they are progressing across their materials.

## Requirements

### Requirement: Attempt History List

The client SHALL list the attempts owned by the current user newest first, naming the material, the submission date and the multiple-choice score of each, and SHALL let the user open any of them.

#### Scenario: History is shown

- **WHEN** the user opens the results page
- **THEN** their attempts are listed newest first with the material name, the date and the multiple-choice score of each

#### Scenario: Empty history

- **WHEN** the user has not completed any attempt
- **THEN** the page explains that a result appears after the first completed test and offers a control that opens the practice page

#### Scenario: Loading is not empty

- **WHEN** the attempts request has not finished yet
- **THEN** a loading indication is shown instead of the empty state

#### Scenario: Request fails

- **WHEN** loading the attempts fails with a server error
- **THEN** the page shows a readable message and a control that retries the request

#### Scenario: Attempt is opened

- **WHEN** the user selects an attempt from the list
- **THEN** the breakdown of that attempt is displayed

#### Scenario: Results page requires a session

- **WHEN** a visitor without a stored token opens the results page
- **THEN** the browser moves to the sign-in form and no attempts request is sent

### Requirement: Attempt Detail

The client SHALL show a chosen attempt with every question, the answer given, the correct option for multiple-choice questions and the stored score and feedback for open ones, and SHALL address the attempt by URL so reopening it keeps the breakdown.

#### Scenario: Detail is shown

- **WHEN** the user opens an attempt
- **THEN** every question of its test is shown together with the answer the user gave and whether it was correct

#### Scenario: Open answers show score and feedback

- **WHEN** the attempt contains evaluated open answers
- **THEN** each of them shows its score and its feedback next to the reference answer

#### Scenario: Unevaluated open answers

- **WHEN** the attempt contains open answers that were never evaluated
- **THEN** they are shown as not checked, with a control that starts the evaluation

#### Scenario: Unanswered questions are named

- **WHEN** a question of the attempt was left unanswered
- **THEN** it is shown as unanswered instead of being omitted

#### Scenario: Reopening keeps the breakdown

- **WHEN** the user reloads the page or opens the attempt link in a new tab
- **THEN** the same attempt breakdown is loaded from the server

#### Scenario: Attempt cannot be read

- **WHEN** the API answers `404` for the requested attempt
- **THEN** the page shows a readable message and a control that returns to the history

### Requirement: Progress Summary

The client SHALL summarise the user's progress per material: how many attempts were submitted and the multiple-choice score of the latest one.

#### Scenario: Summary per material

- **WHEN** the user has attempts over several materials
- **THEN** each material with attempts shows its attempt count and the score of its latest attempt

#### Scenario: Material without attempts

- **WHEN** a material has no attempts
- **THEN** it is not presented in the summary as if it had been practised

#### Scenario: Test without multiple-choice questions

- **WHEN** an attempt came from a test that had no multiple-choice questions
- **THEN** its summary line reports no multiple-choice score instead of a zero out of zero
