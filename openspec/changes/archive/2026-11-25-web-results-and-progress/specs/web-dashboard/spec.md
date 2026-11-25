# Spec Delta

## MODIFIED Requirements

### Requirement: Results Section Explained

The client SHALL present the results section as an entry point to the attempt history, showing the most recent completed attempts, and SHALL offer a control that opens the history.

#### Scenario: Results section

- **WHEN** the dashboard renders
- **THEN** the results section names the attempts the user has completed and offers a control that opens the history

#### Scenario: Recent results are shown

- **WHEN** the dashboard renders for a user who has completed attempts
- **THEN** the results section lists the most recent attempts with the material they belong to and their multiple-choice score

#### Scenario: No attempts yet

- **WHEN** the user has not completed any attempt
- **THEN** the results section explains that results appear after a first completed test and still offers the control that opens the history

#### Scenario: Loading is not empty

- **WHEN** the attempts request has not finished yet
- **THEN** the empty state is not shown and a loading indication is presented instead

#### Scenario: Control opens history

- **WHEN** the user activates the control of the results section
- **THEN** the browser opens the results page

#### Scenario: Attempts request fails

- **WHEN** loading the attempts fails with a server error
- **THEN** the section shows a readable message and offers a control that retries the request without hiding the rest of the dashboard

### Requirement: Application Navigation

The client SHALL present one persistent navigation shell on every authenticated page, naming at least the dashboard, the practice page and the results page, and SHALL mark the entry of the page currently shown.

#### Scenario: Entries are visible

- **WHEN** any authenticated page renders
- **THEN** the dashboard, practice and results entries are all shown

#### Scenario: Current page is marked

- **WHEN** the user is on the practice page
- **THEN** the practice entry is visually marked as the current one

#### Scenario: Current results page is marked

- **WHEN** the user is on the results page
- **THEN** the results entry is visually marked as the current one

#### Scenario: Navigation outlives page changes

- **WHEN** the user moves between authenticated pages
- **THEN** the shell is neither removed nor rebuilt and keeps its state
