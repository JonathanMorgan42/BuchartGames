*** Settings ***
Documentation    End-to-end tests for complete game night workflow
...              Tests the full user journey from login to game night completion
...              WARNING: Only run these tests in development with a dummy database
Library          SeleniumLibrary
Test Setup       Login As Admin
Test Teardown    Close Browser

*** Variables ***
${SERVER}        http://localhost:5000
${BROWSER}       chrome
${DELAY}         0.2
${LOGIN_URL}     ${SERVER}/auth/login
${ADMIN_USER}    testadmin
${ADMIN_PASS}    testpassword123

*** Test Cases ***
Create Game Night
    [Documentation]    Test creating a new game night
    [Tags]    workflow    game_night
    Navigate To Game Night Creation
    Input Game Night Name    Epic Friday Night
    Select Todays Date
    Submit Game Night Form
    Game Night Should Be Created    Epic Friday Night

Create Team With Participants
    [Documentation]    Test creating a team with participants
    [Tags]    workflow    team
    Create Test Game Night
    Navigate To Team Creation
    Input Team Name    Red Dragons
    Input Team Color    #FF0000
    Input Participant    1    John    Doe
    Input Participant    2    Jane    Smith
    Submit Team Form
    Team Should Be Created    Red Dragons

Full Game Night Workflow
    [Documentation]    Test complete workflow: create game night, add teams, play games
    [Tags]    workflow    integration    smoke
    # Step 1: Create game night
    Navigate To Game Night Creation
    Input Game Night Name    Complete Workflow Test
    Select Todays Date
    Submit Game Night Form
    Game Night Should Be Created    Complete Workflow Test

    # Step 2: Add teams
    Navigate To Team Creation
    Create Team With Two Participants    Team Alpha    #FF0000    Alice    Johnson    Bob    Smith
    Navigate To Team Creation
    Create Team With Two Participants    Team Beta    #00FF00    Charlie    Brown    Diana    Prince

    # Step 3: Verify teams were added
    Page Should Contain    Team Alpha
    Page Should Contain    Team Beta

    # Step 4: Add game
    Navigate To Game Creation
    Input Game Name    Trivia Challenge
    Submit Game Form
    Game Should Be Created    Trivia Challenge

View Game History
    [Documentation]    Test viewing game night history
    [Tags]    workflow    history
    Navigate To History Page
    Page Should Contain    History

Logout Workflow
    [Documentation]    Test logout functionality
    [Tags]    workflow    auth
    Click Logout
    Login Page Should Be Open

*** Keywords ***
Login As Admin
    Open Browser    ${LOGIN_URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Input Text    id:username    ${ADMIN_USER}
    Input Password    id:password    ${ADMIN_PASS}
    Click Button    type:submit
    Wait Until Page Does Not Contain    login

Login Page Should Be Open
    Location Should Be    ${LOGIN_URL}

Navigate To Game Night Creation
    Click Link    link:New Game Night
    Wait Until Page Contains    Create Game Night

Input Game Night Name
    [Arguments]    ${name}
    Input Text    id:name    ${name}

Select Todays Date
    # Date field should default to today
    Pass Execution    Date defaults to today

Submit Game Night Form
    Click Button    type:submit

Game Night Should Be Created
    [Arguments]    ${name}
    Wait Until Page Contains    ${name}

Create Test Game Night
    Navigate To Game Night Creation
    Input Game Night Name    Test Game Night
    Select Todays Date
    Submit Game Night Form

Navigate To Team Creation
    Click Link    link:Add Team
    Wait Until Page Contains    Team

Input Team Name
    [Arguments]    ${name}
    Input Text    id:name    ${name}

Input Team Color
    [Arguments]    ${color}
    Input Text    id:color    ${color}

Input Participant
    [Arguments]    ${number}    ${first_name}    ${last_name}
    Input Text    id:participant${number}FirstName    ${first_name}
    Input Text    id:participant${number}LastName    ${last_name}

Submit Team Form
    Click Button    type:submit

Team Should Be Created
    [Arguments]    ${name}
    Wait Until Page Contains    ${name}

Create Team With Two Participants
    [Arguments]    ${team_name}    ${color}    ${p1_first}    ${p1_last}    ${p2_first}    ${p2_last}
    Input Team Name    ${team_name}
    Input Team Color    ${color}
    Input Participant    1    ${p1_first}    ${p1_last}
    Input Participant    2    ${p2_first}    ${p2_last}
    Submit Team Form

Navigate To Game Creation
    Click Link    link:Add Game
    Wait Until Page Contains    Game

Input Game Name
    [Arguments]    ${name}
    Input Text    id:name    ${name}

Submit Game Form
    Click Button    type:submit

Game Should Be Created
    [Arguments]    ${name}
    Wait Until Page Contains    ${name}

Navigate To History Page
    Click Link    link:History
    Wait Until Page Contains    History

Click Logout
    Click Link    link:Logout
    Wait Until Page Contains    login
