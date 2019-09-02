Feature: Search in Sogou website
  In order to search in sogou website
  As a visitor
  We will search the NBA best player

  Scenario: Search NBA player
    Given I have the english name "<search_name>"
    When I search it in sogou website
    Then I see the entire name "<search_name>"

  Examples:
    | search_name | search_result |
    | Jordan | Michael |
    | Curry | Stephen |
    | Kobe | Bryant |
