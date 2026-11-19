# web-quiz Specification

## Purpose

Lets a signed-in user configure a practice test over one of their own materials, answer it without seeing the correct answers beforehand, and receive a scored result with a breakdown of every question.

## Requirements

### Requirement: Practice Configuration

The client SHALL let the user pick one of their materials and request how many multiple-choice and how many open questions the test should contain, and SHALL NOT send a generation request when both counts are zero.

#### Scenario: Materials offered

- **WHEN** the user owns at least one material
- **THEN** every material can be chosen as the test source and the most recent one is preselected

#### Scenario: Default counts

- **WHEN** the practice page opens
- **THEN** the form requests five multiple-choice questions and zero open questions

#### Scenario: Both counts zero

- **WHEN** the requested multiple-choice count and open count are both zero
- **THEN** the form reports the problem next to the fields and sends no request

#### Scenario: Counts out of range

- **WHEN** a requested count is negative or above the documented maximum
- **THEN** the form rejects the value without sending a request

### Requirement: Quiz Generation From Practice Page

The client SHALL request generation with the chosen counts and SHALL show a waiting indication for the whole request, which may take up to a minute.

#### Scenario: Generation pending

- **WHEN** a generation request is in flight
- **THEN** the trigger is disabled and a waiting indication is shown instead of questions

#### Scenario: Generation succeeds

- **WHEN** the API answers `200`
- **THEN** the generated test replaces the configuration form and the first question is shown

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

The client MUST NOT reveal correct options, open-answer references, scores or feedback while the test is in progress.

#### Scenario: Multiple-choice question shown

- **WHEN** a multiple-choice question is displayed before submission
- **THEN** no option is marked, highlighted or otherwise identifiable as correct

#### Scenario: Open question shown

- **WHEN** an open question is displayed before submission
- **THEN** no reference answer and no feedback is shown

#### Scenario: Result reveals answers

- **WHEN** the user submits the test
- **THEN** the correct option of every multiple-choice question becomes identifiable

### Requirement: Sequential Practice Progress

The client SHALL present one question at a time together with the position in the test, and SHALL let the user revisit answered questions without losing the chosen answers.

#### Scenario: Position is shown

- **WHEN** a question is displayed
- **THEN** its position and the total number of questions are shown

#### Scenario: Moving backwards

- **WHEN** the user returns to a previously answered question
- **THEN** the answer already given for it is still there

#### Scenario: Submitting with unanswered questions

- **WHEN** the user submits while some questions are unanswered
- **THEN** the submission is accepted and each unanswered multiple-choice question counts as incorrect

### Requirement: Practice Result

After submission the client SHALL show how many multiple-choice questions were answered correctly and a per-question breakdown that names the answer the user gave and the correct one.

#### Scenario: Choice score

- **WHEN** a test with multiple-choice questions is submitted
- **THEN** the result shows the number of correct answers and the total number of multiple-choice questions

#### Scenario: Breakdown

- **WHEN** the result is displayed
- **THEN** every question shows the answer the user gave, and every multiple-choice question also shows the correct option

#### Scenario: Only open questions

- **WHEN** the submitted test contains no multiple-choice questions
- **THEN** no multiple-choice score is presented

### Requirement: Open Answer Evaluation

The client SHALL send the user's answers to open questions to the API in a single request and SHALL display the returned score and feedback for each of them, and a failed evaluation MUST NOT discard the multiple-choice result already computed.

#### Scenario: Single evaluation request

- **WHEN** the submitted test contains more than one open answer
- **THEN** all of them are sent in one request

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

The client SHALL keep the generated test, the answers given and the resulting score in the browser session storage, and SHALL restore them when the page is reloaded in the same tab.

#### Scenario: Reload restores the test

- **WHEN** the page is reloaded while a test is in progress or a result is displayed
- **THEN** the test, the answers already given and any computed result are shown again without a new generation request

#### Scenario: New generation replaces stored state

- **WHEN** the user generates a new test
- **THEN** the stored test and answers of the previous one are discarded

#### Scenario: New tab starts fresh

- **WHEN** the practice page is opened in a new tab
- **THEN** no previous test is restored
