*** Settings ***
Documentation    End-to-end tests for login functionality
...              These tests use Robot Framework to simulate real user interactions
...              WARNING: Only run these tests in development with a dummy database
Library          SeleniumLibrary
Test Setup       Open Browser To Login Page
Test Teardown    Close Browser

*** Variables ***
${SERVER}        http://localhost:5000
${BROWSER}       chrome
${DELAY}         0.2
${LOGIN_URL}     ${SERVER}/auth/login
${VALID_USER}    testadmin
${VALID_PASS}    testpassword123

*** Test Cases ***
Valid Login
    [Documentation]    Test successful login with valid credentials
    [Tags]    smoke    auth
    Input Username    ${VALID_USER}
    Input Password    ${VALID_PASS}
    Submit Credentials
    Welcome Page Should Be Open

Invalid Password
    [Documentation]    Test login with invalid password
    [Tags]    auth    negative
    Input Username    ${VALID_USER}
    Input Password    wrongpassword
    Submit Credentials
    Login Should Fail With Error    Invalid username or password

Empty Username
    [Documentation]    Test login with empty username
    [Tags]    auth    negative    validation
    Input Username    ${EMPTY}
    Input Password    ${VALID_PASS}
    Submit Credentials
    Page Should Contain    required

Empty Password
    [Documentation]    Test login with empty password
    [Tags]    auth    negative    validation
    Input Username    ${VALID_USER}
    Input Password    ${EMPTY}
    Submit Credentials
    Page Should Contain    required

Both Fields Empty
    [Documentation]    Test login with both fields empty
    [Tags]    auth    negative    validation
    Input Username    ${EMPTY}
    Input Password    ${EMPTY}
    Submit Credentials
    Page Should Contain    required

Nonexistent User
    [Documentation]    Test login with nonexistent username
    [Tags]    auth    negative
    Input Username    nonexistentuser
    Input Password    ${VALID_PASS}
    Submit Credentials
    Login Should Fail With Error    Invalid username or password

SQL Injection Attempt
    [Documentation]    Test login is protected against SQL injection
    [Tags]    auth    security
    Input Username    ' OR '1'='1
    Input Password    ' OR '1'='1
    Submit Credentials
    Login Should Fail With Error    Invalid username or password

*** Keywords ***
Open Browser To Login Page
    Open Browser    ${LOGIN_URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Login Page Should Be Open

Login Page Should Be Open
    Title Should Be    GameNight Login
    Location Should Be    ${LOGIN_URL}

Input Username
    [Arguments]    ${username}
    Input Text    id:username    ${username}

Input Password
    [Arguments]    ${password}
    Input Password    id:password    ${password}

Submit Credentials
    Click Button    type:submit

Welcome Page Should Be Open
    Location Should Not Be    ${LOGIN_URL}
    Page Should Contain    Game

Login Should Fail With Error
    [Arguments]    ${error_message}
    Location Should Be    ${LOGIN_URL}
    Page Should Contain    ${error_message}
