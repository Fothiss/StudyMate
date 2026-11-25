# Spec Delta

## MODIFIED Requirements

### Requirement: Quiz Generation From Practice Page

The client SHALL request generation with the chosen counts, SHALL keep the returned test identifier for the later submission, and SHALL show a waiting indication for the whole request, which may take up to a minute.

#### Scenario: Generation pending

- **WHEN** a generation request is in flight
- **THEN** the trigger is disabled and a waiting indication is shown instead of questions

#### Scenario: Generation succeeds

- **WHEN** the API answers `200`
- **THEN** the generated test replaces the configuration form and the first question is shown

#### Scenario: Test identifier is kept

- **WHEN** generation succeeds and the user starts answering
- **THEN** the client keeps the returned test identifier and submits the answers against it

#### Scenario: Generation fails

- **WHEN** the API answers `502` or the request fails
- **THEN** the page shows a readable message, offers a retry control, and shows no partial test

#### Scenario: Material cannot produce a test

- **WHEN** the API answers `422` for the chosen material
- **THEN** the page shows a readable message and no partial test

#### Scenario: Fewer questions than requested

- **WHEN** the API returns fewer questions than were requested
- **THEN** the returned questions are used and the shortfall is stated

### Requirement: Answers Hidden During Practice

The client MUST NOT reveal correct options, open-answer references, scores or feedback while the test is in progress, and the payload it receives during practice MUST NOT carry them.

#### Scenario: Multiple-choice question shown

- **WHEN** a multiple-choice question is displayed before submission
- **THEN** no option is marked, highlighted or otherwise identifiable as correct

#### Scenario: Open question shown

- **WHEN** an open question is displayed before submission
- **THEN** no reference answer and no feedback is shown

#### Scenario: Practice payload carries no answers

- **WHEN** the client receives the generated test before submission
- **THEN** the payload contains no correct option, no index of it and no reference answer that could be inspected

#### Scenario: Result reveals answers

- **WHEN** the user submits the test
- **THEN** the correct option of every multiple-choice question becomes identifiable

### Requirement: Practice Result

After submission the client SHALL show the number of correctly answered multiple-choice questions and a per-question breakdown taken from the stored attempt, naming the answer the user gave and the correct one.

#### Scenario: Choice score

- **WHEN** a test with multiple-choice questions is submitted
- **THEN** the result shows the number of correct answers and the total number of multiple-choice questions as reported by the API

#### Scenario: Breakdown

- **WHEN** the result is displayed
- **THEN** every question shows the answer the user gave, and every multiple-choice question also shows the correct option

#### Scenario: Result is read from the server

- **WHEN** the result is displayed, now or after a reload
- **THEN** its content comes from the stored attempt rather than from a comparison performed in the browser

#### Scenario: Only open questions

- **WHEN** the submitted test contains no multiple-choice questions
- **THEN** no multiple-choice score is presented

### Requirement: Open Answer Evaluation

The client SHALL request evaluation of the stored open answers of the submitted attempt in a single request and SHALL display the returned score and feedback for each of them, and a failed evaluation MUST NOT discard the multiple-choice result already stored.

#### Scenario: Single evaluation request

- **WHEN** the submitted test contains more than one open answer
- **THEN** all of them are evaluated by one request for that attempt

#### Scenario: Feedback displayed

- **WHEN** the evaluation succeeds
- **THEN** every open question shows its score and its feedback

#### Scenario: Evaluation pending

- **WHEN** the evaluation request is in flight
- **THEN** a waiting indication is shown in place of the open-question feedback while the multiple-choice result stays visible

#### Scenario: Evaluation fails

- **WHEN** the evaluation request answers `502` or fails
- **THEN** the page shows a readable message and a control that retries the evaluation, and the multiple-choice result is still shown

### Requirement: Practice State Survives Reload

The client SHALL keep the draft of an unfinished attempt — the test identifier, the answers given and the current question — in the browser session storage, and SHALL restore the result of a submitted attempt from the server when the page is reopened.

#### Scenario: Reload restores the test

- **WHEN** the page is reloaded while a test is in progress
- **THEN** the same test, the answers already given and the current question are shown again without a new generation request

#### Scenario: Reload restores a submitted result

- **WHEN** the page is reloaded while a result is displayed
- **THEN** the result is read again from the stored attempt and shown as before

#### Scenario: Result outlives the tab

- **WHEN** the browser tab is closed and the results page is opened later
- **THEN** the submitted attempt is still available in the history

#### Scenario: New generation replaces stored state

- **WHEN** the user generates a new test
- **THEN** the stored draft of the previous one is discarded

#### Scenario: New tab starts fresh

- **WHEN** the practice page is opened in a new tab
- **THEN** no unfinished draft is restored
