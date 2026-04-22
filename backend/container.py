"""
Dependency Injection container.

Builds use cases with their concrete dependencies.
FastAPI routers call container functions to get pre-built use cases
instead of newing up dependencies inline.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.evaluators.scorer import BDDScorer

from backend.infrastructure.generator_factory import GeneratorFactory
from backend.application.generate_bdd import GenerateBDDUseCase
from backend.application.evaluate_bdd import EvaluateBDDUseCase
from backend.application.generate_unit_tests import GenerateUnitTestsUseCase


def get_generate_use_case(model: str, threshold: float) -> GenerateBDDUseCase:
    """
    Builds a GenerateBDDUseCase for a specific model + threshold combination.

    A new instance is created per request because:
    - Different requests may use different models / thresholds.
    - LLM generator instances hold no shared mutable state.
    """
    generator = GeneratorFactory.create(model)
    scorer    = BDDScorer(threshold=threshold)
    return GenerateBDDUseCase(generator=generator, scorer=scorer)


def get_evaluate_use_case(threshold: float) -> EvaluateBDDUseCase:
    scorer = BDDScorer(threshold=threshold)
    return EvaluateBDDUseCase(scorer=scorer)


def get_unit_test_use_case(model: str) -> GenerateUnitTestsUseCase:
    generator = GeneratorFactory.create(model, max_tokens=8192)
    return GenerateUnitTestsUseCase(generator=generator)
