import copy
import random

from .config import ResearchConfig

_WEIGHT_KEYS = ["cobertura", "clareza", "estrutura", "executabilidade"]
_WEIGHT_DELTA = 0.05


def mutate(config: ResearchConfig, rng: random.Random) -> tuple[ResearchConfig, str]:
    """Returns a mutated config and a human-readable description of the change."""
    new = copy.deepcopy(config)
    strategy = rng.choice(["perturb", "swap", "threshold", "attempts"])

    if strategy == "perturb":
        key = rng.choice(_WEIGHT_KEYS)
        sign = rng.choice([-1, 1])
        old_val = getattr(new, key)
        new_val = round(max(0.05, min(0.60, old_val + sign * _WEIGHT_DELTA)), 4)
        setattr(new, key, new_val)
        _normalize(new)
        desc = f"perturb {key} {old_val:.2f}->{getattr(new, key):.2f}"

    elif strategy == "swap":
        k1, k2 = rng.sample(_WEIGHT_KEYS, 2)
        v1, v2 = getattr(new, k1), getattr(new, k2)
        setattr(new, k1, v2)
        setattr(new, k2, v1)
        desc = f"swap {k1}<->{k2} ({v1:.2f}<->{v2:.2f})"

    elif strategy == "threshold":
        delta = rng.choice([-0.5, +0.5])
        new.threshold = round(max(4.0, min(9.5, new.threshold + delta)), 1)
        desc = f"threshold {config.threshold:.1f}->{new.threshold:.1f}"

    else:  # attempts
        delta = rng.choice([-1, +1])
        new.max_attempts = max(1, min(8, new.max_attempts + delta))
        desc = f"max_attempts {config.max_attempts}->{new.max_attempts}"

    return new, desc


def _normalize(config: ResearchConfig) -> None:
    total = (
        config.cobertura + config.clareza +
        config.estrutura + config.executabilidade
    )
    if total <= 0:
        config.cobertura = config.clareza = config.estrutura = config.executabilidade = 0.25
        return
    config.cobertura       = round(config.cobertura / total, 4)
    config.clareza         = round(config.clareza / total, 4)
    config.estrutura       = round(config.estrutura / total, 4)
    # Compute last weight to guarantee exact sum = 1.0
    config.executabilidade = round(
        1.0 - config.cobertura - config.clareza - config.estrutura, 4
    )
