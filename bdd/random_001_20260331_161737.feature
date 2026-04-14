# ============================================
# BDD Scenario Suite
# Gerado em: 2026-03-31 16:17:37.149556
# Modelo: deepseek-coder:6.7b
# Total de Cenários: 1
#
# User Story:
# Como usuário, quero que o seguinte problema seja corrigido: (bug) Verify your email address emails broken on Hotmail and Outlook
#
# Issue: (bug) Verify your email address emails broken on Hotmail and Outlook
# Story Points: 1.0
# ============================================

```gherkin
Feature: Verify Email Functionality on Hotmail and Outlook

Scenario: User receives a verification email in Outlook and is able to verify it
  Given I am logged into the Outlook web client with a valid account
  When I receive an email asking me to verify my email address
  Then I should be able to click on the "Verify Email Address" link in the email
  And I should see a confirmation message saying that the verification was successful

Scenario: User receives a verification email in Hotmail and is not able to verify it
  Given I am logged into the Hotmail web client with a valid account
  When I receive an email asking me to verify my email address
  Then I should NOT be able to click on the "Verify Email Address" link in the email
  And I should see an error message saying that there was a problem verifying your email

Scenario: User receives a verification email in Hotmail and is able to verify it with correct details
  Given I am logged into the Hotmail web client with a valid account
  When I receive an email asking me to verify my email address with correct details
  Then I should be able to click on the "Verify Email Address" link in the email
  And I should see a confirmation message saying that the verification was successful

Scenario: User receives a verification email in Outlook and is not able to verify it with incorrect details
  Given I am logged into the Outlook web client with an invalid account
  When I receive an email asking me to verify my email address with incorrect details
  Then I should NOT be able to click on the "Verify Email Address" link in the email
  And I should see an error message saying that there was a problem verifying your email
```