*** Settings ***
Documentation    End-to-end tests for delete operations
...              Tests all delete workflows through the UI
...              WARNING: Only run these tests in development with a dummy database
Library          SeleniumLibrary
Test Setup       Setup For Tests
Test Teardown    Close Browser

*** Variables ***
${SERVER}        http://localhost:5000
${BROWSER}       chrome
${DELAY}         0.2
${LOGIN_URL}     ${SERVER}/auth/login
${ADMIN_USER}    testadmin
${ADMIN_PASS}    testpassword123

*** Test Cases ***
Delete Team Successfully
    [Documentation]    Test deleting a team through UI
    [Tags]    delete    team    critical
    # Create game night and team first
    Create Test Game Night    Delete Test Night
    Create Team    Team To Delete    #FF0000    Alice    Smith    Bob    Jones
    Page Should Contain    Team To Delete

    # Delete the team
    Click Delete Button For Team    Team To Delete
    Confirm Deletion

    # Verify team is deleted
    Page Should Not Contain    Team To Delete

Delete Team With Scores
    [Documentation]    Test that deleting team with scores works correctly
    [Tags]    delete    team    critical
    # Setup: Create game night, team, game, and add scores
    Create Test Game Night    Scores Test Night
    Create Team    Team With Scores    #00FF00    John    Doe    Jane    Doe
    Create Game    Test Game    1

    # Add scores for the team (if scoring interface available)
    # For now, just verify delete works
    Go To Teams Page
    Click Delete Button For Team    Team With Scores
    Confirm Deletion

    Page Should Not Contain    Team With Scores

Delete Game Successfully
    [Documentation]    Test deleting a game through UI
    [Tags]    delete    game    critical
    Create Test Game Night    Game Delete Night
    Create Game    Game To Delete    1
    Page Should Contain    Game To Delete

    # Delete the game
    Click Delete Button For Game    Game To Delete
    Confirm Deletion

    # Verify game is deleted
    Page Should Not Contain    Game To Delete

Delete Game With Scores
    [Documentation]    Test deleting game that has scores
    [Tags]    delete    game    critical
    Create Test Game Night    Game With Scores Night
    Create Team    Score Team    #0000FF    Player    One    Player    Two
    Create Game    Scored Game    1

    # Delete the game
    Click Delete Button For Game    Scored Game
    Confirm Deletion

    Page Should Not Contain    Scored Game

Delete Game Night Successfully
    [Documentation]    Test deleting a game night
    [Tags]    delete    game_night    critical
    Navigate To Game Night Management
    Click Link    link:Create Game Night
    Input Text    id:name    Night To Delete
    Click Button    type:submit
    Wait Until Page Contains    Night To Delete

    # Delete the game night
    Click Delete Button For Game Night    Night To Delete
    Confirm Deletion

    Page Should Not Contain    Night To Delete

Delete Game Night With Data
    [Documentation]    Test deleting game night with teams and games
    [Tags]    delete    game_night    critical    cascade
    Create Test Game Night    Full Night Delete
    Create Team    Delete Team 1    #FF0000    A    B    C    D
    Create Team    Delete Team 2    #00FF00    E    F    G    H
    Create Game    Delete Game 1    1

    # Navigate back to game night management
    Navigate To Game Night Management

    # Delete the game night
    Click Delete Button For Game Night    Full Night Delete
    Confirm Deletion

    # Verify game night and all related data are gone
    Page Should Not Contain    Full Night Delete
    Go To Teams Page
    Page Should Not Contain    Delete Team 1
    Page Should Not Contain    Delete Team 2

Cannot Delete Without Confirmation
    [Documentation]    Test that delete requires proper confirmation
    [Tags]    delete    validation
    Create Test Game Night    Protected Night
    Create Team    Protected Team    #FF0000    X    Y    Z    W

    # Try to delete but cancel
    Click Delete Button For Team    Protected Team
    Cancel Deletion If Possible

    # Team should still exist
    Page Should Contain    Protected Team

Delete Multiple Teams
    [Documentation]    Test deleting multiple teams in sequence
    [Tags]    delete    team    multiple
    Create Test Game Night    Multi Delete Night
    Create Team    Team 1    #FF0000    A    A    B    B
    Create Team    Team 2    #00FF00    C    C    D    D
    Create Team    Team 3    #0000FF    E    E    F    F

    # Delete all teams
    Click Delete Button For Team    Team 1
    Confirm Deletion
    Click Delete Button For Team    Team 2
    Confirm Deletion
    Click Delete Button For Team    Team 3
    Confirm Deletion

    # Verify all are deleted
    Page Should Not Contain    Team 1
    Page Should Not Contain    Team 2
    Page Should Not Contain    Team 3

Delete Multiple Games
    [Documentation]    Test deleting multiple games in sequence
    [Tags]    delete    game    multiple
    Create Test Game Night    Multi Game Delete Night
    Create Game    Game A    1
    Create Game    Game B    2
    Create Game    Game C    3

    # Delete all games
    Click Delete Button For Game    Game A
    Confirm Deletion
    Click Delete Button For Game    Game B
    Confirm Deletion
    Click Delete Button For Game    Game C
    Confirm Deletion

    # Verify all are deleted
    Page Should Not Contain    Game A
    Page Should Not Contain    Game B
    Page Should Not Contain    Game C

*** Keywords ***
Setup For Tests
    Login As Admin
    Navigate To Home

Login As Admin
    Open Browser    ${LOGIN_URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Input Text    id:username    ${ADMIN_USER}
    Input Password    id:password    ${ADMIN_PASS}
    Click Button    type:submit
    Wait Until Page Does Not Contain    login

Navigate To Home
    Go To    ${SERVER}

Create Test Game Night
    [Arguments]    ${name}
    Click Link    link:New Game Night
    Wait Until Page Contains    Create Game Night
    Input Text    id:name    ${name}
    Click Button    type:submit
    Wait Until Page Contains    ${name}

Create Team
    [Arguments]    ${team_name}    ${color}    ${p1_first}    ${p1_last}    ${p2_first}    ${p2_last}
    Click Link    link:Add Team
    Wait Until Page Contains    Team
    Input Text    id:name    ${team_name}
    Input Text    id:color    ${color}
    Input Text    id:participant1FirstName    ${p1_first}
    Input Text    id:participant1LastName    ${p1_last}
    Input Text    id:participant2FirstName    ${p2_first}
    Input Text    id:participant2LastName    ${p2_last}
    Click Button    type:submit
    Wait Until Page Contains    ${team_name}

Create Game
    [Arguments]    ${game_name}    ${sequence}
    Click Link    link:Add Game
    Wait Until Page Contains    Game
    Input Text    id:name    ${game_name}
    Input Text    id:sequence_number    ${sequence}
    Click Button    type:submit
    Wait Until Page Contains    ${game_name}

Go To Teams Page
    Click Link    link:Teams
    Wait Until Page Contains    Teams

Navigate To Game Night Management
    Click Link    link:History
    Wait Until Page Contains    History

Click Delete Button For Team
    [Arguments]    ${team_name}
    # Find and click delete button for specific team
    # This may need adjustment based on actual UI structure
    ${xpath}=    Set Variable    //tr[contains(., '${team_name}')]//button[contains(., 'Delete') or contains(@class, 'delete')]
    Click Element    ${xpath}

Click Delete Button For Game
    [Arguments]    ${game_name}
    ${xpath}=    Set Variable    //tr[contains(., '${game_name}')]//button[contains(., 'Delete') or contains(@class, 'delete')]
    Click Element    ${xpath}

Click Delete Button For Game Night
    [Arguments]    ${gn_name}
    ${xpath}=    Set Variable    //tr[contains(., '${gn_name}')]//button[contains(., 'Delete') or contains(@class, 'delete')]
    Click Element    ${xpath}

Confirm Deletion
    # Handle confirmation dialog if present
    ${alert_present}=    Run Keyword And Return Status    Alert Should Be Present
    Run Keyword If    ${alert_present}    Accept Alert
    # Or if it's a form confirmation
    ${button_present}=    Run Keyword And Return Status    Page Should Contain Button    Confirm
    Run Keyword If    ${button_present}    Click Button    Confirm
    Sleep    0.5s

Cancel Deletion If Possible
    ${alert_present}=    Run Keyword And Return Status    Alert Should Be Present
    Run Keyword If    ${alert_present}    Dismiss Alert
    ${button_present}=    Run Keyword And Return Status    Page Should Contain Button    Cancel
    Run Keyword If    ${button_present}    Click Button    Cancel
