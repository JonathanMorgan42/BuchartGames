*** Settings ***
Documentation    End-to-end tests for scoring functionality
...              Tests complete scoring workflows including live scoring
...              WARNING: Only run these tests in development with a dummy database
Library          SeleniumLibrary
Test Setup       Setup Scoring Test
Test Teardown    Close Browser

*** Variables ***
${SERVER}        http://localhost:5000
${BROWSER}       chrome
${DELAY}         0.2
${LOGIN_URL}     ${SERVER}/auth/login
${ADMIN_USER}    testadmin
${ADMIN_PASS}    testpassword123

*** Test Cases ***
Enter Scores For Game
    [Documentation]    Test entering scores for a game
    [Tags]    scoring    workflow    critical
    Navigate To Games Page
    Click Score Button For Game    Scoring Test Game

    # Enter scores for teams
    Input Score For Team    Team Red    100
    Input Score For Team    Team Blue    85
    Submit Scores

    # Verify scores were saved
    Page Should Contain    saved

Complete Game With Scores
    [Documentation]    Test completing a game with scores
    [Tags]    scoring    workflow    critical
    Navigate To Games Page
    Click Score Button For Game    Complete Test Game

    # Enter scores
    Input Score For Team    Team Red    100
    Input Score For Team    Team Blue    90

    # Mark as complete
    Select Checkbox    id:is_completed
    Submit Scores

    # Verify game is marked complete
    Page Should Contain    completed

Enter Scores With Points Override
    [Documentation]    Test manually overriding points
    [Tags]    scoring    manual
    Navigate To Games Page
    Click Score Button For Game    Override Test Game

    # Enter custom points
    Input Score For Team    Team Red    100
    Input Points For Team    Team Red    10
    Input Score For Team    Team Blue    90
    Input Points For Team    Team Blue    5
    Submit Scores

    Page Should Contain    saved

Enter Time Based Scores
    [Documentation]    Test entering time-based scores
    [Tags]    scoring    time
    Navigate To Games Page
    Click Score Button For Game    Time Test Game

    # Enter time scores (lower is better)
    Input Score For Team    Team Red    45.5
    Input Score For Team    Team Blue    52.3
    Submit Scores

    Page Should Contain    saved

Update Existing Scores
    [Documentation]    Test updating previously entered scores
    [Tags]    scoring    update
    Navigate To Games Page
    Click Score Button For Game    Update Test Game

    # Enter initial scores
    Input Score For Team    Team Red    100
    Submit Scores
    Sleep    0.5s

    # Update scores
    Click Score Button For Game    Update Test Game
    Clear Score For Team    Team Red
    Input Score For Team    Team Red    120
    Submit Scores

    Page Should Contain    saved

Enter Scores With Notes
    [Documentation]    Test adding notes to scores
    [Tags]    scoring    notes
    Navigate To Games Page
    Click Score Button For Game    Notes Test Game

    Input Score For Team    Team Red    100
    Input Notes For Team    Team Red    Excellent performance!
    Submit Scores

    Page Should Contain    saved

Verify Leaderboard Updates
    [Documentation]    Test that leaderboard updates after scoring
    [Tags]    scoring    leaderboard    integration
    # Enter scores for a game
    Navigate To Games Page
    Click Score Button For Game    Leaderboard Test Game
    Input Score For Team    Team Red    100
    Input Score For Team    Team Blue    50
    Submit Scores

    # Navigate to leaderboard
    Navigate To Home
    Page Should Contain    Leaderboard
    # Team Red should be ranked higher
    ${red_position}=    Get Element Position    Team Red
    ${blue_position}=    Get Element Position    Team Blue

Score Multiple Games In Sequence
    [Documentation]    Test scoring multiple games consecutively
    [Tags]    scoring    multiple    workflow
    Navigate To Games Page

    # Score Game 1
    Click Score Button For Game    Multi Game 1
    Input Score For Team    Team Red    100
    Input Score For Team    Team Blue    80
    Submit Scores

    # Score Game 2
    Navigate To Games Page
    Click Score Button For Game    Multi Game 2
    Input Score For Team    Team Red    90
    Input Score For Team    Team Blue    95
    Submit Scores

    # Verify both games are scored
    Navigate To Games Page
    Page Should Contain    Multi Game 1
    Page Should Contain    Multi Game 2

Zero Score Entry
    [Documentation]    Test entering zero as a valid score
    [Tags]    scoring    edge_case
    Navigate To Games Page
    Click Score Button For Game    Zero Test Game
    Input Score For Team    Team Red    0
    Input Score For Team    Team Blue    10
    Submit Scores

    Page Should Contain    saved

Negative Score Entry
    [Documentation]    Test entering negative scores (for penalties)
    [Tags]    scoring    edge_case
    Navigate To Games Page
    Click Score Button For Game    Negative Test Game
    Input Score For Team    Team Red    -5
    Submit Scores

    Page Should Contain    saved

Decimal Score Entry
    [Documentation]    Test entering decimal/float scores
    [Tags]    scoring    edge_case
    Navigate To Games Page
    Click Score Button For Game    Decimal Test Game
    Input Score For Team    Team Red    95.75
    Input Score For Team    Team Blue    88.25
    Submit Scores

    Page Should Contain    saved

Live Scoring Quick Update
    [Documentation]    Test rapid score updates during live play
    [Tags]    scoring    live    performance
    Navigate To Games Page
    Click Score Button For Game    Live Test Game

    # Rapidly update scores
    Input Score For Team    Team Red    10
    Sleep    0.2s
    Clear Score For Team    Team Red
    Input Score For Team    Team Red    20
    Sleep    0.2s
    Clear Score For Team    Team Red
    Input Score For Team    Team Red    30
    Submit Scores

    Page Should Contain    saved

*** Keywords ***
Setup Scoring Test
    Login As Admin
    # Create test game night with teams and games
    Create Test Game Night    Scoring Test Night
    Create Test Team    Team Red    #FF0000
    Create Test Team    Team Blue    #0000FF
    Create Test Game    Scoring Test Game    1
    Create Test Game    Complete Test Game    2
    Create Test Game    Override Test Game    3
    Create Test Game    Time Test Game    4
    Create Test Game    Update Test Game    5
    Create Test Game    Notes Test Game    6
    Create Test Game    Leaderboard Test Game    7
    Create Test Game    Multi Game 1    8
    Create Test Game    Multi Game 2    9
    Create Test Game    Zero Test Game    10
    Create Test Game    Negative Test Game    11
    Create Test Game    Decimal Test Game    12
    Create Test Game    Live Test Game    13

Login As Admin
    Open Browser    ${LOGIN_URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Input Text    id:username    ${ADMIN_USER}
    Input Password    id:password    ${ADMIN_PASS}
    Click Button    type:submit
    Wait Until Page Does Not Contain    login

Create Test Game Night
    [Arguments]    ${name}
    Click Link    link:New Game Night
    Wait Until Page Contains    Create Game Night
    Input Text    id:name    ${name}
    Click Button    type:submit
    Wait Until Page Contains    ${name}

Create Test Team
    [Arguments]    ${team_name}    ${color}
    Click Link    link:Add Team
    Wait Until Page Contains    Team
    Input Text    id:name    ${team_name}
    Input Text    id:color    ${color}
    Input Text    id:participant1FirstName    Player
    Input Text    id:participant1LastName    One
    Input Text    id:participant2FirstName    Player
    Input Text    id:participant2LastName    Two
    Click Button    type:submit
    Wait Until Page Contains    ${team_name}

Create Test Game
    [Arguments]    ${game_name}    ${sequence}
    Click Link    link:Add Game
    Wait Until Page Contains    Game
    Input Text    id:name    ${game_name}
    Input Text    id:sequence_number    ${sequence}
    Click Button    type:submit
    Wait Until Page Contains    ${game_name}

Navigate To Home
    Click Link    link:Home
    Wait Until Page Contains    Game

Navigate To Games Page
    Click Link    link:Games
    Wait Until Page Contains    Games

Click Score Button For Game
    [Arguments]    ${game_name}
    ${xpath}=    Set Variable    //tr[contains(., '${game_name}')]//a[contains(., 'Score') or contains(@href, '/scores/edit/')]
    Click Element    ${xpath}
    Wait Until Page Contains    Score

Input Score For Team
    [Arguments]    ${team_name}    ${score_value}
    # Find the score input for the specific team
    ${team_row}=    Set Variable    //tr[contains(., '${team_name}')]
    ${score_input}=    Set Variable    ${team_row}//input[contains(@id, 'score-') or contains(@name, 'score')]
    Input Text    ${score_input}    ${score_value}

Input Points For Team
    [Arguments]    ${team_name}    ${points}
    ${team_row}=    Set Variable    //tr[contains(., '${team_name}')]
    ${points_input}=    Set Variable    ${team_row}//input[contains(@id, 'points-') or contains(@name, 'points')]
    Input Text    ${points_input}    ${points}

Input Notes For Team
    [Arguments]    ${team_name}    ${notes}
    ${team_row}=    Set Variable    //tr[contains(., '${team_name}')]
    ${notes_input}=    Set Variable    ${team_row}//input[contains(@id, 'notes-') or contains(@name, 'notes')]
    Input Text    ${notes_input}    ${notes}

Clear Score For Team
    [Arguments]    ${team_name}
    ${team_row}=    Set Variable    //tr[contains(., '${team_name}')]
    ${score_input}=    Set Variable    ${team_row}//input[contains(@id, 'score-') or contains(@name, 'score')]
    Clear Element Text    ${score_input}

Submit Scores
    Click Button    type:submit
    Sleep    0.5s

Get Element Position
    [Arguments]    ${text}
    ${elements}=    Get WebElements    xpath://body//*[contains(text(), '${text}')]
    ${count}=    Get Length    ${elements}
    [Return]    ${count}
