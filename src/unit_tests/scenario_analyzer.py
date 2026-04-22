"""
Semantic analysis layer for BDD → unit test generation.

Sits between GherkinParser (raw AST) and PromptBuilder (LLM prompt).
Extracts structured signals — SUT name, mock dependencies, method hints,
arrange/act/assert blueprints — without requiring any NLP library.

All inference is heuristic: "good enough to guide the LLM" is the goal.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .gherkin_parser import GherkinFeature, GherkinScenario, GherkinStep


# ─────────────────────────────────────────────────────────────────────────────
# Enums & value objects
# ─────────────────────────────────────────────────────────────────────────────

class ScenarioType(str, Enum):
    HAPPY_PATH   = "happy_path"
    ERROR        = "error"
    AUTH         = "auth"
    BOUNDARY     = "boundary"
    PARAMETRIZED = "parametrized"

    def label(self) -> str:
        return {
            "happy_path":   "HAPPY PATH  — fluxo principal bem-sucedido",
            "error":        "ERROR       — comportamento esperado em caso de falha",
            "auth":         "AUTH        — controle de acesso / permissão",
            "boundary":     "BOUNDARY    — valor de borda ou condição extrema",
            "parametrized": "PARAMETRIZED — múltiplos conjuntos de dados (Outline)",
        }[self.value]


@dataclass
class TestDataPoint:
    value: str
    dtype: str        # "email" | "url" | "number" | "boolean" | "string"
    phase: str        # "arrange" | "act" | "assert"
    step_text: str


@dataclass
class ArrangeHint:
    """One mock configuration for the Arrange phase."""
    dependency: str       # class name, e.g. "UserRepository"
    variable:   str       # variable name, e.g. "user_repository"
    method:     str       # method to stub, e.g. "find_by_email"
    args:       list[str] # literal args, e.g. ['"user@example.com"']
    returns:    str       # stub return, e.g. 'User(id=1, email="...", active=True)'
    is_error_path: bool = False


@dataclass
class ActHint:
    """The single Act call deduced from When steps."""
    sut_variable: str     # e.g. "auth_service"
    method:       str     # e.g. "login"
    args:         list[str]
    is_async:     bool = False
    raw_steps:    list[str] = field(default_factory=list)


@dataclass
class AssertHint:
    """One assertion deduced from a Then step."""
    kind:              str  # "equality"|"boolean"|"exception"|"mock_called"|"contains"|"null"
    description:       str  # human-readable description for the prompt
    target:            str  # e.g. "result.token" or "user_repository.block_account"
    expected:          str  # e.g. '"jwt-token-abc123"' or 'True'
    exception_class:   Optional[str] = None
    exception_message: Optional[str] = None


@dataclass
class ScenarioAnalysis:
    name:          str
    stype:         ScenarioType
    arrange_hints: list[ArrangeHint]
    act_hint:      Optional[ActHint]
    assert_hints:  list[AssertHint]
    test_data:     list[TestDataPoint]
    outline_rows:  list[dict[str, str]] = field(default_factory=list)

    def format_for_prompt(self) -> str:
        lines: list[str] = [
            f"━━ {self.name}",
            f"   Tipo: {self.stype.label()}",
        ]

        if self.test_data:
            vals = " | ".join(f"{d.dtype}:{d.value}" for d in self.test_data[:8])
            lines.append(f"   Dados de teste: {vals}")

        if self.outline_rows:
            lines.append(f"   Outline rows ({len(self.outline_rows)}):")
            for row in self.outline_rows:
                lines.append("     " + ", ".join(f"{k}={v}" for k, v in row.items()))

        if self.arrange_hints:
            lines.append("   ARRANGE (Dado que):")
            for h in self.arrange_hints:
                args_str = ", ".join(h.args) if h.args else "..."
                lines.append(f"     mock {h.variable}.{h.method}({args_str}) → {h.returns}")

        if self.act_hint:
            args_str = ", ".join(self.act_hint.args) if self.act_hint.args else "..."
            prefix = "await " if self.act_hint.is_async else ""
            lines.append(f"   ACT (Quando):    result = {prefix}{self.act_hint.sut_variable}.{self.act_hint.method}({args_str})")

        if self.assert_hints:
            lines.append("   ASSERT (Então):")
            for a in self.assert_hints:
                if a.kind == "exception":
                    exc = a.exception_class or "Exception"
                    msg = f' com mensagem "{a.exception_message}"' if a.exception_message else ""
                    lines.append(f"     → espera exceção {exc}{msg}")
                elif a.kind == "mock_called":
                    lines.append(f"     → verifica {a.target} foi chamado")
                else:
                    lines.append(f"     → {a.target} == {a.expected}  [{a.description}]")

        return "\n".join(lines)


@dataclass
class FeatureAnalysis:
    feature_name:           str
    sut_class:              str
    sut_variable:           str
    sut_module:             str
    background_deps:        list[tuple[str, str]]  # (ClassName, variable_name)
    background_data:        list[TestDataPoint]
    scenarios:              list[ScenarioAnalysis]

    def format_for_prompt(self) -> str:
        lines = [
            f"Feature: {self.feature_name}",
            f"SUT inferido: {self.sut_class} (variável: {self.sut_variable}, módulo: {self.sut_module})",
        ]
        if self.background_deps:
            dep_str = ", ".join(f"{cls} ({var})" for cls, var in self.background_deps)
            lines.append(f"Dependências do Background: {dep_str}")
        lines.append(f"Total de cenários: {len(self.scenarios)}")
        lines.append("")
        for sc in self.scenarios:
            lines.append(sc.format_for_prompt())
            lines.append("")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Pattern tables  (order matters — first match wins)
# ─────────────────────────────────────────────────────────────────────────────

_ERROR_KEYWORDS = re.compile(
    r"\b(erro|inválid|invalid|incorret|incorrect|falh|fail|negad|denied|"
    r"bloqueado|blocked|não permit|nao permit|forbid|unauthoriz|"
    r"recusad|reject|exception|expirado|expired|inexistent|not found|"
    r"sem acesso|sem permissão|sem permissao)\b",
    re.IGNORECASE,
)
_AUTH_KEYWORDS = re.compile(
    r"\b(permissão|permissao|autorização|autorizacao|role|perfil|"
    r"administrador|admin|privilege|privilegio|access denied|"
    r"unauthorized|forbidden|acesso negado|sem acesso)\b",
    re.IGNORECASE,
)
_BOUNDARY_KEYWORDS = re.compile(
    r"\b(limit|máximo|maximo|mínimo|minimo|zero|vazio|em branco|nulo|null|"
    r"overflow|edge|extremo|exatamente|exactly|boundary|"
    r"primeiro|último|ultimo|máx|max|min)\b",
    re.IGNORECASE,
)

# SUT class inference: (pattern, (ClassName, variable_name, module_name))
_SUT_DOMAIN: list[tuple[re.Pattern, tuple[str, str, str]]] = [
    (re.compile(r"\b(login|autent|auth)\b", re.I),                    ("AuthService",           "auth_service",           "auth")),
    (re.compile(r"\b(logout|sair|deslogar)\b", re.I),                 ("AuthService",           "auth_service",           "auth")),
    (re.compile(r"\b(cadastr|registr|signup|sign.up)\b", re.I),       ("RegistrationService",   "registration_service",   "registration")),
    (re.compile(r"\b(carrinho|shopping.cart|cart)\b", re.I),          ("CartService",            "cart_service",           "cart")),
    (re.compile(r"\b(pagamento|payment|checkout|fatura|billing)\b", re.I), ("PaymentService",   "payment_service",        "payment")),
    (re.compile(r"\b(pedido|order)\b", re.I),                         ("OrderService",           "order_service",          "order")),
    (re.compile(r"\b(produto|product)\b", re.I),                      ("ProductService",         "product_service",        "product")),
    (re.compile(r"\b(usuário|usuario|user|conta|account)\b", re.I),   ("UserService",            "user_service",           "user")),
    (re.compile(r"\b(notificac|notification|email.service)\b", re.I), ("NotificationService",   "notification_service",   "notification")),
    (re.compile(r"\b(férias|ferias|vacation|holiday)\b", re.I),       ("VacationService",        "vacation_service",       "vacation")),
    (re.compile(r"\b(aprovac|approval|aprovar)\b", re.I),             ("ApprovalService",        "approval_service",       "approval")),
    (re.compile(r"\b(permissão|permissao|permission|autorizac)\b", re.I), ("PermissionService", "permission_service",     "permission")),
    (re.compile(r"\b(senha|password|reset)\b", re.I),                 ("PasswordService",        "password_service",       "password")),
    (re.compile(r"\b(relatorio|report)\b", re.I),                     ("ReportService",          "report_service",         "report")),
    (re.compile(r"\b(estoque|stock|inventory)\b", re.I),              ("InventoryService",       "inventory_service",      "inventory")),
    (re.compile(r"\b(desconto|discount|coupon|cupom)\b", re.I),       ("DiscountService",        "discount_service",       "discount")),
    (re.compile(r"\b(perfil|profile)\b", re.I),                       ("ProfileService",         "profile_service",        "profile")),
    (re.compile(r"\b(busca|search|pesquisa)\b", re.I),                ("SearchService",          "search_service",         "search")),
    (re.compile(r"\b(audit|log|rastreamento)\b", re.I),               ("AuditService",           "audit_service",          "audit")),
    (re.compile(r"\b(transfer|transfere)\b", re.I),                   ("TransferService",        "transfer_service",       "transfer")),
    (re.compile(r"\b(saque|withdraw)\b", re.I),                       ("WalletService",          "wallet_service",         "wallet")),
    (re.compile(r"\b(depósito|deposito|deposit)\b", re.I),            ("WalletService",          "wallet_service",         "wallet")),
]

# Dependency signals in Given steps: (pattern, (ClassName, variable_name))
_DEPENDENCY_SIGNALS: list[tuple[re.Pattern, tuple[str, str]]] = [
    (re.compile(r"\b(usuário|usuario|user|conta|account)\b", re.I),   ("UserRepository",      "user_repository")),
    (re.compile(r"\b(token|jwt|sessão|sessao|session)\b", re.I),      ("TokenService",         "token_service")),
    (re.compile(r"\b(produto|product|item)\b", re.I),                 ("ProductRepository",   "product_repository")),
    (re.compile(r"\b(estoque|stock|inventory)\b", re.I),              ("StockService",         "stock_service")),
    (re.compile(r"\b(pedido|order|carrinho|cart)\b", re.I),           ("OrderRepository",     "order_repository")),
    (re.compile(r"\b(pagamento|payment|stripe|gateway)\b", re.I),     ("PaymentGateway",       "payment_gateway")),
    (re.compile(r"\b(email|notificac|notification)\b", re.I),         ("NotificationService", "notification_service")),
    (re.compile(r"\b(cache|redis)\b", re.I),                          ("CacheService",         "cache_service")),
    (re.compile(r"\b(permissão|permissao|permission|role|acl|rbac)\b", re.I), ("PermissionService", "permission_service")),
    (re.compile(r"\b(senha|password|hash|bcrypt)\b", re.I),           ("PasswordEncoder",     "password_encoder")),
    (re.compile(r"\b(férias|ferias|vacation)\b", re.I),               ("VacationRepository",  "vacation_repository")),
    (re.compile(r"\b(aprovac|approval)\b", re.I),                     ("ApprovalRepository",  "approval_repository")),
    (re.compile(r"\b(audit|evento|event)\b", re.I),                   ("EventBus",             "event_bus")),
    (re.compile(r"\b(arquivo|file|storage|s3|bucket)\b", re.I),       ("StorageService",       "storage_service")),
    (re.compile(r"\b(relatorio|report)\b", re.I),                     ("ReportRepository",    "report_repository")),
    (re.compile(r"\b(desconto|discount|coupon|cupom)\b", re.I),       ("DiscountRepository",  "discount_repository")),
    (re.compile(r"\b(saldo|balance|carteira|wallet)\b", re.I),        ("WalletRepository",    "wallet_repository")),
    (re.compile(r"\b(tempo|timer|clock|agendamento|schedule)\b", re.I), ("Clock",             "clock")),
]

# When step verb → method name
_METHOD_SIGNALS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(fazer login|realiza login|tenta login|loga|autentica|entra com)\b", re.I), "login"),
    (re.compile(r"\b(logout|sair|deslogar|encerra sessão)\b", re.I),  "logout"),
    (re.compile(r"\b(cadastra|registra|cria conta|signup|se registra)\b", re.I), "register"),
    (re.compile(r"\b(adiciona ao carrinho|add to cart)\b", re.I),     "addToCart"),
    (re.compile(r"\b(remove do carrinho|remove item)\b", re.I),       "removeFromCart"),
    (re.compile(r"\b(finaliza compra|checkout|confirma pedido)\b", re.I), "checkout"),
    (re.compile(r"\b(cancela pedido|cancel order)\b", re.I),          "cancelOrder"),
    (re.compile(r"\b(aprova|approve)\b", re.I),                       "approve"),
    (re.compile(r"\b(rejeita|reject|recusa)\b", re.I),                "reject"),
    (re.compile(r"\b(solicita férias|pede férias|request vacation)\b", re.I), "requestVacation"),
    (re.compile(r"\b(busca|pesquisa|search|find|procura)\b", re.I),   "search"),
    (re.compile(r"\b(cria|criar|cadastra|create)\b", re.I),           "create"),
    (re.compile(r"\b(atualiza|edita|update|edit)\b", re.I),           "update"),
    (re.compile(r"\b(deleta|remove|exclu|delete)\b", re.I),           "delete"),
    (re.compile(r"\b(envia|enviar|submit|submete|send)\b", re.I),     "submit"),
    (re.compile(r"\b(cancela|cancel)\b", re.I),                       "cancel"),
    (re.compile(r"\b(calcula|compute|calculate)\b", re.I),            "calculate"),
    (re.compile(r"\b(valida|validate|verifica|verify)\b", re.I),      "validate"),
    (re.compile(r"\b(paga|pagamento|pay|efetua pagamento)\b", re.I),  "pay"),
    (re.compile(r"\b(altera senha|muda senha|reset password|change password)\b", re.I), "changePassword"),
    (re.compile(r"\b(solicita|request|pede)\b", re.I),                "request"),
    (re.compile(r"\b(filtra|filter)\b", re.I),                        "filter"),
    (re.compile(r"\b(lista|listar|list)\b", re.I),                    "list"),
    (re.compile(r"\b(obtém|obtem|busca por|get|fetch|recupera)\b", re.I), "getById"),
    (re.compile(r"\b(acessa|access|abre|open|navega)\b", re.I),       "access"),
    (re.compile(r"\b(preenche|fill|digita|insere)\b", re.I),          "submit"),
    (re.compile(r"\b(clica|click|pressiona)\b", re.I),                "submit"),
    (re.compile(r"\b(transfere|transfer)\b", re.I),                   "transfer"),
    (re.compile(r"\b(saca|withdraw)\b", re.I),                        "withdraw"),
    (re.compile(r"\b(deposita|deposit)\b", re.I),                     "deposit"),
    (re.compile(r"\b(aplica desconto|apply discount)\b", re.I),       "applyDiscount"),
    (re.compile(r"\b(gera relatório|generate report)\b", re.I),       "generateReport"),
]

# Exception class inference from Then error steps
_EXCEPTION_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(credenciais inválidas|senha incorreta|invalid credentials|wrong password)\b", re.I), "InvalidCredentialsException"),
    (re.compile(r"\b(conta bloqueada|account blocked|muitas tentativas)\b", re.I),                       "AccountBlockedException"),
    (re.compile(r"\b(acesso negado|access denied|sem permissão|unauthorized|forbidden)\b", re.I),        "AccessDeniedException"),
    (re.compile(r"\b(não encontrado|not found|inexistente)\b", re.I),                                    "NotFoundException"),
    (re.compile(r"\b(usuário não encontrado|user not found)\b", re.I),                                   "UserNotFoundException"),
    (re.compile(r"\b(produto não encontrado|product not found)\b", re.I),                                "ProductNotFoundException"),
    (re.compile(r"\b(estoque insuficiente|out of stock|sem estoque)\b", re.I),                           "InsufficientStockException"),
    (re.compile(r"\b(token expirado|token expired|sessão expirada)\b", re.I),                            "TokenExpiredException"),
    (re.compile(r"\b(pagamento recusado|payment declined|cartão recusado)\b", re.I),                     "PaymentDeclinedException"),
    (re.compile(r"\b(dados inválidos|invalid data|validação|validation)\b", re.I),                       "ValidationException"),
    (re.compile(r"\b(limite excedido|limit exceeded|quota)\b", re.I),                                    "LimitExceededException"),
    (re.compile(r"\b(email já cadastrado|email already|já existe|already exists)\b", re.I),             "DuplicateEntryException"),
    (re.compile(r"\b(saldo insuficiente|insufficient funds|sem saldo)\b", re.I),                        "InsufficientBalanceException"),
    (re.compile(r"\b(timeout|tempo esgotado)\b", re.I),                                                  "TimeoutException"),
]

# Data type patterns
_EMAIL_RE   = re.compile(r'\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b', re.I)
_URL_RE     = re.compile(r'https?://\S+')
_NUMBER_RE  = re.compile(r'\b\d+(?:[.,]\d+)?\b')
_BOOL_RE    = re.compile(r'\b(true|false|verdadeiro|falso|sim|não|nao)\b', re.I)
_QUOTED_RE  = re.compile(r'"([^"]+)"')


# ─────────────────────────────────────────────────────────────────────────────
# Extraction helpers
# ─────────────────────────────────────────────────────────────────────────────

def _extract_test_data(text: str, phase: str) -> list[TestDataPoint]:
    points: list[TestDataPoint] = []
    for m in _EMAIL_RE.finditer(text):
        points.append(TestDataPoint(f'"{m.group()}"', "email", phase, text))
    for m in _URL_RE.finditer(text):
        points.append(TestDataPoint(f'"{m.group()}"', "url", phase, text))
    for m in _BOOL_RE.finditer(text):
        points.append(TestDataPoint(m.group().lower(), "boolean", phase, text))
    for m in _QUOTED_RE.finditer(text):
        val = m.group(1)
        if not _EMAIL_RE.match(val) and not _URL_RE.match(val):
            dtype = "number" if _NUMBER_RE.fullmatch(val.replace(",", ".")) else "string"
            points.append(TestDataPoint(f'"{val}"', dtype, phase, text))
    return points


def _first_quoted(text: str) -> str | None:
    m = _QUOTED_RE.search(text)
    return f'"{m.group(1)}"' if m else None


def _infer_sut(feature_name: str) -> tuple[str, str, str]:
    """Return (ClassName, variable_name, module_name)."""
    for pattern, triple in _SUT_DOMAIN:
        if pattern.search(feature_name):
            return triple
    # Fallback: PascalCase + Service
    words = re.sub(r"[^a-zA-ZÀ-ú0-9 ]", "", feature_name).split()
    class_name = "".join(w.capitalize() for w in words) + "Service" if words else "FeatureService"
    var_name   = "_".join(w.lower() for w in words) + "_service" if words else "feature_service"
    module     = "_".join(w.lower() for w in words) if words else "feature"
    return class_name, var_name, module


def _infer_dependencies(steps: list[GherkinStep]) -> list[tuple[str, str]]:
    """Returns unique (ClassName, variable_name) pairs inferred from step text."""
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for step in steps:
        for pattern, (cls, var) in _DEPENDENCY_SIGNALS:
            if pattern.search(step.text) and cls not in seen:
                seen.add(cls)
                result.append((cls, var))
    return result


def _infer_method(when_steps: list[GherkinStep]) -> str:
    text = " ".join(s.text for s in when_steps)
    for pattern, method in _METHOD_SIGNALS:
        if pattern.search(text):
            return method
    # Fallback: first verb-like word
    words = re.sub(r"[^a-zA-ZÀ-ú ]", "", text).split()
    return words[0].lower() if words else "execute"


def _infer_method_args(when_steps: list[GherkinStep], test_data: list[TestDataPoint]) -> list[str]:
    """Extract literal argument values from When step data points."""
    args = [d.value for d in test_data if d.phase == "act" and d.dtype in ("email", "string", "number")]
    return args[:4]  # cap at 4 args to stay realistic


def _infer_arrange_hints(
    given_steps: list[GherkinStep],
    deps: list[tuple[str, str]],
    sut_variable: str,
    is_error: bool,
) -> list[ArrangeHint]:
    hints: list[ArrangeHint] = []
    used_deps: set[str] = set()

    for step in given_steps:
        data = _extract_test_data(step.text, "arrange")
        step_deps = [(cls, var) for (cls, var) in deps if not _SUT_DOMAIN or True]

        for cls, var in step_deps:
            if var in used_deps:
                continue
            # Guess the stub method from the dependency class name
            if "Repository" in cls or "Dao" in cls:
                method  = "findByEmail" if _EMAIL_RE.search(step.text) else "findById"
                args    = [d.value for d in data if d.dtype in ("email", "string")][:2]
                if is_error:
                    returns = "null" if "not found" in step.text.lower() else f"{cls.replace('Repository','').replace('Dao','')}(id=1, active=False)"
                else:
                    entity  = cls.replace("Repository", "").replace("Dao", "")
                    email_v = next((d.value for d in data if d.dtype == "email"), None)
                    email_p = f", email={email_v}" if email_v else ""
                    returns = f"{entity}(id=1{email_p}, active=True)"
            elif "Token" in cls or "Jwt" in cls:
                method  = "generate"
                args    = []
                returns = '"jwt-token-abc123"' if not is_error else 'throw TokenExpiredException()'
            elif "Password" in cls or "Encoder" in cls:
                method  = "matches"
                args    = []
                returns = "True" if not is_error else "False"
            elif "Notification" in cls or "Email" in cls:
                method  = "send"
                args    = []
                returns = "None"
            elif "Permission" in cls or "Acl" in cls:
                method  = "hasPermission"
                args    = []
                returns = "True" if not is_error else "False"
            elif "Stock" in cls or "Inventory" in cls:
                method  = "getAvailableQuantity"
                args    = []
                returns = "10" if not is_error else "0"
            elif "Payment" in cls or "Gateway" in cls:
                method  = "charge"
                args    = []
                returns = "PaymentResult(success=True)" if not is_error else 'throw PaymentDeclinedException()'
            elif "Cache" in cls:
                method  = "get"
                args    = []
                returns = "None"
            elif "Clock" in cls:
                method  = "now"
                args    = []
                returns = "LocalDateTime.now()"
            else:
                method  = "findById"
                args    = []
                returns = f"{cls.replace('Service','')}(id=1)"

            hints.append(ArrangeHint(
                dependency    = cls,
                variable      = var,
                method        = method,
                args          = args or ([d.value for d in data[:1]] if data else []),
                returns       = returns,
                is_error_path = is_error,
            ))
            used_deps.add(var)

    return hints


def _infer_assert_hints(
    then_steps: list[GherkinStep],
    stype: ScenarioType,
    act_hint: Optional[ActHint],
) -> list[AssertHint]:
    hints: list[AssertHint] = []

    for step in then_steps:
        text  = step.text
        data  = _extract_test_data(text, "assert")
        qval  = _first_quoted(text)

        if stype == ScenarioType.ERROR:
            # Infer exception class
            exc_cls = next(
                (exc for pat, exc in _EXCEPTION_MAP if pat.search(text)),
                "DomainException",
            )
            exc_msg = qval.strip('"') if qval else None
            hints.append(AssertHint(
                kind              = "exception",
                description       = f"deve lançar {exc_cls}",
                target            = "sut.method()",
                expected          = exc_cls,
                exception_class   = exc_cls,
                exception_message = exc_msg,
            ))

        elif re.search(r"\b(redirecionado|redirect|navega para|dashboard|pagina inicial)\b", text, re.I):
            path = qval or '"/dashboard"'
            hints.append(AssertHint("equality", "redirecionamento correto", "result.redirectUrl", path))

        elif re.search(r"\b(mensagem|message|texto|text|exibe|mostra|vê|ve|aparece)\b", text, re.I):
            msg = qval or '"mensagem esperada"'
            hints.append(AssertHint("contains", "mensagem exibida ao usuário", "result.message", msg))

        elif re.search(r"\b(sucesso|success|bem.sucedido|confirmed|aprovado|created)\b", text, re.I):
            hints.append(AssertHint("boolean", "operação bem-sucedida", "result.success", "True"))

        elif re.search(r"\b(token|jwt|chave|key)\b", text, re.I):
            token_val = qval or '"<token>"'
            hints.append(AssertHint("equality", "token retornado", "result.token", token_val))

        elif re.search(r"\b(id|identificador|criado com|created with)\b", text, re.I):
            id_val = next((d.value for d in data if d.dtype == "number"), '"<id>"')
            hints.append(AssertHint("equality", "ID do recurso criado", "result.id", id_val))

        elif re.search(r"\b(quantidade|count|total|numero de|número de)\b", text, re.I):
            n = next((d.value for d in data if d.dtype == "number"), "1")
            hints.append(AssertHint("equality", "quantidade correta", "result.count", n))

        elif re.search(r"\b(lista|list|array|collection)\b", text, re.I):
            hints.append(AssertHint("boolean", "lista não vazia", "len(result) > 0", "True"))

        elif re.search(r"\b(bloqueado|blocked|desabilitado|disabled|inativo|inactive)\b", text, re.I):
            dep_var = "user_repository"  # best-effort
            hints.append(AssertHint("mock_called", "conta bloqueada/desabilitada", f"{dep_var}.blockAccount", "True"))

        elif re.search(r"\b(enviado|sent|notificado|notified|email enviado)\b", text, re.I):
            hints.append(AssertHint("mock_called", "notificação enviada", "notification_service.send", "True"))

        elif re.search(r"\b(salvo|saved|persistido|persisted|gravado)\b", text, re.I):
            hints.append(AssertHint("mock_called", "entidade persistida", "repository.save", "True"))

        elif qval:
            hints.append(AssertHint("equality", f"valor retornado: {qval}", "result.value", qval))

        else:
            hints.append(AssertHint("boolean", text[:60], "result.success", "True"))

    return hints


def _build_outline_rows(scenario: GherkinScenario) -> list[dict[str, str]]:
    if not scenario.examples or len(scenario.examples) < 2:
        return []
    headers = scenario.examples[0]
    return [dict(zip(headers, row)) for row in scenario.examples[1:]]


# ─────────────────────────────────────────────────────────────────────────────
# Main analyser
# ─────────────────────────────────────────────────────────────────────────────

class ScenarioAnalyzer:
    """
    Transforms a GherkinFeature into a FeatureAnalysis filled with
    structural hints for the LLM to produce precise, high-quality tests.
    """

    def analyze(self, feature: GherkinFeature) -> FeatureAnalysis:
        sut_class, sut_var, sut_module = _infer_sut(feature.name)

        # Background analysis
        bg_deps  = _infer_dependencies(feature.background_steps)
        bg_data  = [dp for s in feature.background_steps for dp in _extract_test_data(s.text, "arrange")]

        scenario_analyses = [
            self._analyze_scenario(sc, sut_class, sut_var, bg_deps)
            for sc in feature.scenarios
        ]

        return FeatureAnalysis(
            feature_name     = feature.name,
            sut_class        = sut_class,
            sut_variable     = sut_var,
            sut_module       = sut_module,
            background_deps  = bg_deps,
            background_data  = bg_data,
            scenarios        = scenario_analyses,
        )

    def _analyze_scenario(
        self,
        scenario: GherkinScenario,
        sut_class: str,
        sut_var: str,
        bg_deps: list[tuple[str, str]],
    ) -> ScenarioAnalysis:

        # Collect test data per phase
        arrange_data = [dp for s in scenario.given_steps for dp in _extract_test_data(s.text, "arrange")]
        act_data     = [dp for s in scenario.when_steps  for dp in _extract_test_data(s.text, "act")]
        assert_data  = [dp for s in scenario.then_steps  for dp in _extract_test_data(s.text, "assert")]
        all_data     = arrange_data + act_data + assert_data

        # Classify
        all_text = " ".join(s.text for s in scenario.steps)
        if scenario.is_outline:
            stype = ScenarioType.PARAMETRIZED
        elif _AUTH_KEYWORDS.search(all_text):
            stype = ScenarioType.AUTH
        elif _ERROR_KEYWORDS.search(all_text):
            stype = ScenarioType.ERROR
        elif _BOUNDARY_KEYWORDS.search(all_text):
            stype = ScenarioType.BOUNDARY
        else:
            stype = ScenarioType.HAPPY_PATH

        is_error = stype in (ScenarioType.ERROR, ScenarioType.AUTH)

        # Dependencies (bg + scenario-specific)
        sc_deps   = _infer_dependencies(scenario.given_steps)
        all_deps_dict: dict[str, tuple[str, str]] = {v: (c, v) for c, v in bg_deps}
        for cls, var in sc_deps:
            all_deps_dict[var] = (cls, var)
        all_deps = list(all_deps_dict.values())

        # Method
        method     = _infer_method(scenario.when_steps)
        method_args = _infer_method_args(scenario.when_steps, act_data + arrange_data)

        act_hint = ActHint(
            sut_variable = sut_var,
            method       = method,
            args         = method_args,
            is_async     = bool(re.search(r"\b(async|await|assíncrono)\b", all_text, re.I)),
            raw_steps    = [s.text for s in scenario.when_steps],
        ) if scenario.when_steps else None

        arrange_hints = _infer_arrange_hints(
            given_steps  = scenario.given_steps,
            deps         = all_deps,
            sut_variable = sut_var,
            is_error     = is_error,
        )

        assert_hints = _infer_assert_hints(
            then_steps = scenario.then_steps,
            stype      = stype,
            act_hint   = act_hint,
        )

        outline_rows = _build_outline_rows(scenario) if stype == ScenarioType.PARAMETRIZED else []

        return ScenarioAnalysis(
            name          = scenario.name,
            stype         = stype,
            arrange_hints = arrange_hints,
            act_hint      = act_hint,
            assert_hints  = assert_hints,
            test_data     = all_data,
            outline_rows  = outline_rows,
        )
