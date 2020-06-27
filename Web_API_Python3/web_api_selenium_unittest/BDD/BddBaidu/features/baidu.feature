Feature: Go to baidu

Scenario: search selenium
  Given I go to "https://www.baidu.com/"
     When I fill in field with id "kw" with "selenium"
     And  I click id "su" with baidu once
     Then I should see "seleniumhq.org" within 2 second
     Then I close browser