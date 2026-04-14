# ============================================
# BDD Scenario Suite
# Gerado em: 2026-03-31 16:46:13.290994
# Modelo: deepseek-coder:6.7b
# Total de Cenários: 1
#
# User Story:
# Disable editing on permaweb posts for now
#
# Issue: Disable editing on permaweb posts for now
# Story Points: 1.0
# ============================================

Aqui estão alguns cenários Gherkin para a história "Disable editing on permaweb posts for now":

```gherkin
Feature: Disable Editing On Permaweb Posts For Now

Scenario: Happy path scenario
  Given I am an authenticated user with the role of admin
  When I navigate to a specific post on the platform
  Then I should see an option to disable editing on that post
  And I can click on this option to turn off the ability to edit the post

Scenario: User without necessary permissions
  Given I am an authenticated user with the role of non-admin
  When I navigate to a specific post on the platform
  Then I should not see an option to disable editing on that post

Scenario: Post does not exist
  Given I am an admin user and I do not have access to a specific post
  When I try to navigate to this non-existent post
  Then I should be redirected to the main feed with an error message indicating that the post does not exist

Scenario: Post is locked by another user
  Given I am an admin user and there are two instances of a specific post - one being edited by me, and the other being edited by another user
  When I navigate to this second instance of the post
  Then I should see an option to disable editing on that post
  And when I click it, it should lock the post for editing by the current user only
```

Esse é um exemplo básico e pode ser expandido de acordo com as necessidades da história. As regras definidas (simples: 3-4, média: 4-6, complexa: 6-8 cenários) estão sendo seguindo neste exemplo.