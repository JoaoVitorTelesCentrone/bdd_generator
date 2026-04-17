"""
Tests for bist/bist_parser.py — Gherkin .feature file parser.

Cenários cobertos:
  - Nome da Feature é extraído corretamente
  - Cenários e seus steps são parsados
  - Background steps são separados dos cenários
  - Tags @foo são atribuídas ao cenário seguinte
  - Keywords em português (Dado/Quando/Então/E/Mas) são reconhecidas
  - Linhas de comentário (#) e linhas em branco são ignoradas
  - Feature com múltiplos cenários
  - parse_feature_file lê do disco corretamente
  - Step.full_text() retorna keyword + texto
"""
import sys, os, textwrap
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from bist.bist_parser import parse_feature_text, parse_feature_file, Feature, Scenario, Step


# ── helpers ───────────────────────────────────────────────────────────────────

def parse(text: str) -> Feature:
    return parse_feature_text(textwrap.dedent(text))


# ── feature name ─────────────────────────────────────────────────────────────

class TestFeatureName:
    """Cenário: Nome da Feature é extraído corretamente"""

    def test_basic_feature_name(self):
        f = parse("""
            Feature: User Login
        """)
        assert f.name == "User Login"

    def test_feature_name_with_extra_spaces(self):
        f = parse("Feature:   Checkout Flow   ")
        assert f.name == "Checkout Flow"

    def test_feature_keyword_case_insensitive(self):
        f = parse("feature: Something")
        assert f.name == "Something"

    def test_empty_feature_name(self):
        f = parse("Feature:")
        assert f.name == ""

    def test_feature_description_lines_captured(self):
        f = parse("""
            Feature: Login
              As a user
              I want to log in
        """)
        assert "As a user" in f.description


# ── scenario parsing ──────────────────────────────────────────────────────────

class TestScenarioParsing:
    """Cenário: Cenários e seus steps são parsados"""

    def test_single_scenario_name(self):
        f = parse("""
            Feature: Login
              Scenario: Valid login
                Given I am on login page
        """)
        assert len(f.scenarios) == 1
        assert f.scenarios[0].name == "Valid login"

    def test_steps_are_captured(self):
        f = parse("""
            Feature: Login
              Scenario: Valid login
                Given I am on login page
                When I fill "email" with "user@test.com"
                Then I should see "Dashboard"
        """)
        steps = f.scenarios[0].steps
        assert len(steps) == 3

    def test_step_keywords_are_preserved(self):
        f = parse("""
            Feature: Login
              Scenario: Example
                Given context
                When action
                Then result
                And another result
                But not this
        """)
        keywords = [s.keyword for s in f.scenarios[0].steps]
        assert keywords == ["Given", "When", "Then", "And", "But"]

    def test_step_text_excludes_keyword(self):
        f = parse("""
            Feature: X
              Scenario: Y
                Given I am on the home page
        """)
        step = f.scenarios[0].steps[0]
        assert step.text == "I am on the home page"
        assert step.keyword == "Given"

    def test_step_full_text(self):
        step = Step(keyword="When", text='I click "Submit"')
        assert step.full_text() == 'When I click "Submit"'

    def test_multiple_scenarios(self):
        f = parse("""
            Feature: Auth
              Scenario: Login
                Given I am on login page
              Scenario: Logout
                Given I am logged in
                When I click logout
        """)
        assert len(f.scenarios) == 2
        assert f.scenarios[0].name == "Login"
        assert f.scenarios[1].name == "Logout"
        assert len(f.scenarios[1].steps) == 2

    def test_scenario_outline_is_parsed(self):
        f = parse("""
            Feature: Checkout
              Scenario Outline: Buy item
                Given I have "<item>"
        """)
        assert len(f.scenarios) == 1
        assert f.scenarios[0].name == "Buy item"


# ── background ────────────────────────────────────────────────────────────────

class TestBackground:
    """Cenário: Background steps são separados dos cenários"""

    def test_background_steps_separated(self):
        f = parse("""
            Feature: Auth
              Background:
                Given I am logged in
                And cookies are set
              Scenario: View dashboard
                When I go to dashboard
        """)
        assert len(f.background_steps) == 2
        assert len(f.scenarios[0].steps) == 1

    def test_background_steps_keywords(self):
        f = parse("""
            Feature: X
              Background:
                Given setup step
                And another setup
        """)
        kws = [s.keyword for s in f.background_steps]
        assert kws == ["Given", "And"]

    def test_background_does_not_appear_in_scenarios(self):
        f = parse("""
            Feature: X
              Background:
                Given bg step
              Scenario: S1
                When action
        """)
        step_texts = [s.text for s in f.scenarios[0].steps]
        assert "bg step" not in step_texts


# ── tags ─────────────────────────────────────────────────────────────────────

class TestTags:
    """Cenário: Tags @foo são atribuídas ao cenário seguinte"""

    def test_single_tag(self):
        f = parse("""
            Feature: X
              @smoke
              Scenario: Tagged scenario
                Given step
        """)
        assert "smoke" in f.scenarios[0].tags

    def test_multiple_tags_on_one_line(self):
        f = parse("""
            Feature: X
              @smoke @regression @critical
              Scenario: Multi-tagged
                Given step
        """)
        assert set(f.scenarios[0].tags) == {"smoke", "regression", "critical"}

    def test_tag_not_applied_to_wrong_scenario(self):
        f = parse("""
            Feature: X
              Scenario: Untagged
                Given step one
              @important
              Scenario: Tagged
                Given step two
        """)
        assert f.scenarios[0].tags == []
        assert "important" in f.scenarios[1].tags


# ── portuguese keywords ───────────────────────────────────────────────────────

class TestPortugueseKeywords:
    """Cenário: Keywords em português são reconhecidas"""

    def test_dado_quando_entao(self):
        f = parse("""
            Funcionalidade: Login
              Cenário: Login válido
                Dado que estou na página de login
                Quando preencho o email com "user@email.com"
                Então devo ver "Dashboard"
        """)
        assert len(f.scenarios) == 1
        kws = [s.keyword for s in f.scenarios[0].steps]
        assert kws == ["Dado", "Quando", "Então"]

    def test_e_and_mas(self):
        f = parse("""
            Funcionalidade: X
              Cenário: PT conjunctions
                Dado contexto
                E outro contexto
                Mas não este
        """)
        kws = [s.keyword for s in f.scenarios[0].steps]
        assert "E" in kws
        assert "Mas" in kws

    def test_mixed_pt_en_feature(self):
        f = parse("""
            Feature: Mixed
              Scenario: PT steps
                Dado que estou na página
                When I click "OK"
                Então vejo "Sucesso"
        """)
        assert len(f.scenarios[0].steps) == 3


# ── comments and blank lines ──────────────────────────────────────────────────

class TestCommentsAndBlankLines:
    """Cenário: Comentários e linhas em branco são ignorados"""

    def test_comment_lines_ignored(self):
        f = parse("""
            Feature: X
              # This is a comment
              Scenario: S
                # Another comment
                Given step
        """)
        assert len(f.scenarios[0].steps) == 1
        assert f.scenarios[0].steps[0].text == "step"

    def test_blank_lines_ignored(self):
        f = parse("""
            Feature: X


              Scenario: S

                Given step one

                Then step two

        """)
        assert len(f.scenarios[0].steps) == 2


# ── file I/O ──────────────────────────────────────────────────────────────────

class TestParseFromFile:
    """Cenário: parse_feature_file lê do disco corretamente"""

    def test_parse_existing_file(self):
        feature_path = Path(__file__).parent.parent / "smoke_test.feature"
        f = parse_feature_file(str(feature_path))
        assert f.name != ""
        assert len(f.scenarios) > 0

    def test_parse_temp_file(self, tmp_path):
        content = """Feature: Temp
  Scenario: Quick
    Given I am here
    When I do something
    Then I see results
"""
        p = tmp_path / "temp.feature"
        p.write_text(content, encoding="utf-8")
        f = parse_feature_file(str(p))
        assert f.name == "Temp"
        assert len(f.scenarios[0].steps) == 3

    def test_parse_feature_text_and_file_are_consistent(self, tmp_path):
        content = "Feature: Parity\n  Scenario: S\n    Given step\n"
        p = tmp_path / "p.feature"
        p.write_text(content, encoding="utf-8")
        from_text = parse_feature_text(content)
        from_file = parse_feature_file(str(p))
        assert from_text.name == from_file.name
        assert len(from_text.scenarios) == len(from_file.scenarios)
