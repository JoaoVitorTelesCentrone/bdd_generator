from __future__ import annotations

import re
from typing import Dict, Tuple

from .gherkin_parser import GherkinFeature, GherkinScenario, GherkinStep
from .scenario_analyzer import ScenarioAnalyzer


# ---------------------------------------------------------------------------
# AAA mapping injected into every prompt — language-agnostic
# ---------------------------------------------------------------------------

_AAA_MAPPING = """
MAPEAMENTO BDD → PADRÃO AAA (ARRANGE-ACT-ASSERT)
══════════════════════════════════════════════════
│ BDD keyword │ AAA fase  │ O que gerar no código                              │
│─────────────│───────────│────────────────────────────────────────────────────│
│ Given       │ Arrange   │ Instanciar SUT, criar mocks/fakes, configurar estado│
│ When        │ Act       │ Chamar o método/função real do SUT                  │
│ Then        │ Assert    │ Assertion real sobre o resultado ou efeito colateral │
│ And / But   │ mesma fase│ Continua o bloco anterior                           │
══════════════════════════════════════════════════

REGRAS OBRIGATÓRIAS DE QUALIDADE:
1. NUNCA use stubs vazios (assert False, fail, TODO). Cada teste deve ter assertions reais.
2. Derive o nome da classe/módulo sob teste (SUT) a partir do nome da Feature.
3. Crie mocks/fakes para TODAS as dependências mencionadas nos steps Given.
4. O step When contém o método a ser chamado — infira o nome e argumentos a partir do texto.
5. O step Then contém o resultado esperado — gere a assertion exata (assertEqual, expect().toBe(), etc.).
6. Cenários com "erro", "inválido", "bloqueado", "negado", "falha" → use assertRaises/assertThrows/expect().toThrow().
7. Strings entre aspas nos steps → use como valores literais de teste.
8. Scenario Outline → um teste por linha da tabela Examples, com os valores reais interpolados.
9. Background steps → inicialização compartilhada (fixture / setUp / beforeEach).
10. Importe APENAS o que for necessário. Não deixe imports fantasma.
"""

# ---------------------------------------------------------------------------
# Framework-specific rules with realistic examples
# ---------------------------------------------------------------------------

_FRAMEWORK_RULES: Dict[str, Dict[str, str]] = {
    "python": {
        "pytest": """LINGUAGEM: Python 3.10+ | FRAMEWORK: pytest + unittest.mock

IMPORTS OBRIGATÓRIOS:
```python
import pytest
from unittest.mock import MagicMock, patch, call
```

ESTRUTURA DO ARQUIVO:
```python
import pytest
from unittest.mock import MagicMock, patch

# SUT — substitua pelo import real quando disponível
# from app.auth import AuthService

class TestLoginDeUsuario:

    @pytest.fixture(autouse=True)
    def _setup(self):
        # Arrange (Background) — dependências mockadas
        self.user_repository = MagicMock()
        self.token_service    = MagicMock()
        self.sut              = AuthService(
            user_repo=self.user_repository,
            token_svc=self.token_service,
        )

    def test_login_com_credenciais_validas(self):
        # Arrange — Given: usuário existe no repositório com senha válida
        self.user_repository.find_by_email.return_value = {
            "id": 1, "email": "user@example.com", "active": True
        }
        self.token_service.generate.return_value = "jwt-token-abc123"

        # Act — When: usuário tenta fazer login
        result = self.sut.login(email="user@example.com", password="Senha@123")

        # Assert — Then: autenticação bem-sucedida, token retornado
        assert result["success"] is True
        assert result["token"] == "jwt-token-abc123"
        self.user_repository.find_by_email.assert_called_once_with("user@example.com")

    def test_login_com_senha_incorreta(self):
        # Arrange — Given: usuário existe mas senha não confere
        self.user_repository.find_by_email.return_value = {
            "id": 1, "email": "user@example.com", "active": True
        }
        self.user_repository.check_password.return_value = False

        # Act + Assert — When/Then: deve lançar exceção de autenticação
        with pytest.raises(AuthenticationError) as exc_info:
            self.sut.login(email="user@example.com", password="senhaErrada")

        assert "Credenciais inválidas" in str(exc_info.value)

    def test_login_apos_tres_tentativas_falhas(self):
        # Arrange — Given: conta com 2 falhas registradas
        self.user_repository.get_failed_attempts.return_value = 2

        # Act + Assert — When/Then: terceira falha deve bloquear conta
        with pytest.raises(AccountBlockedError):
            self.sut.login(email="user@example.com", password="errada")

        self.user_repository.block_account.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

PADRÕES OBRIGATÓRIOS:
- `MagicMock()` para cada dependência do SUT
- `.return_value` para configurar o retorno de mocks
- `assert_called_once_with(...)` para verificar chamadas ao mock
- `with pytest.raises(ExceptionType)` para cenários de erro
- `assert result["campo"] == valor_esperado` como assertion mínima por teste
- Scenario Outline → `@pytest.mark.parametrize` ou um método por linha de Examples""",

        "unittest": """LINGUAGEM: Python 3.10+ | FRAMEWORK: unittest + unittest.mock

ESTRUTURA DO ARQUIVO:
```python
import unittest
from unittest.mock import MagicMock, patch, call

# from app.auth import AuthService, AuthenticationError

class TestLoginDeUsuario(unittest.TestCase):

    def setUp(self):
        # Arrange (Background) — dependências mockadas
        self.user_repository = MagicMock()
        self.token_service    = MagicMock()
        self.sut              = AuthService(
            user_repo=self.user_repository,
            token_svc=self.token_service,
        )

    def test_login_com_credenciais_validas(self):
        # Arrange — Given
        self.user_repository.find_by_email.return_value = {
            "id": 1, "email": "user@example.com"
        }
        self.token_service.generate.return_value = "jwt-token-abc123"

        # Act — When
        result = self.sut.login(email="user@example.com", password="Senha@123")

        # Assert — Then
        self.assertTrue(result["success"])
        self.assertEqual(result["token"], "jwt-token-abc123")
        self.user_repository.find_by_email.assert_called_once_with("user@example.com")

    def test_login_com_senha_incorreta(self):
        # Arrange
        self.user_repository.find_by_email.return_value = {"id": 1}
        self.user_repository.check_password.return_value = False

        # Act + Assert
        with self.assertRaises(AuthenticationError) as ctx:
            self.sut.login(email="user@example.com", password="senhaErrada")

        self.assertIn("Credenciais inválidas", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
```

PADRÕES OBRIGATÓRIOS:
- `setUp(self)` para Background; `tearDown` se houver cleanup
- `self.assertEqual`, `self.assertTrue`, `self.assertIn` como assertions reais
- `self.assertRaises(ExceptionType)` para cenários de erro
- `mock.assert_called_once_with(...)` para verificar interações""",
    },

    "javascript": {
        "jest": """LINGUAGEM: JavaScript (ES2022) | FRAMEWORK: Jest 29+

ESTRUTURA DO ARQUIVO:
```javascript
// SUT — substitua pelo caminho real
// const { AuthService } = require('./authService');

describe('Login de Usuário', () => {

    let authService;
    let userRepository;
    let tokenService;

    beforeEach(() => {
        // Arrange (Background) — mocks das dependências
        userRepository = {
            findByEmail:     jest.fn(),
            checkPassword:   jest.fn(),
            getFailedAttempts: jest.fn(),
            blockAccount:    jest.fn(),
        };
        tokenService = { generate: jest.fn() };
        authService  = new AuthService({ userRepository, tokenService });
    });

    afterEach(() => jest.clearAllMocks());

    test('login com credenciais válidas', async () => {
        // Arrange — Given
        userRepository.findByEmail.mockResolvedValue({ id: 1, email: 'user@example.com', active: true });
        tokenService.generate.mockReturnValue('jwt-token-abc123');

        // Act — When
        const result = await authService.login('user@example.com', 'Senha@123');

        // Assert — Then
        expect(result.success).toBe(true);
        expect(result.token).toBe('jwt-token-abc123');
        expect(userRepository.findByEmail).toHaveBeenCalledWith('user@example.com');
    });

    test('login com senha incorreta lança erro', async () => {
        // Arrange — Given
        userRepository.findByEmail.mockResolvedValue({ id: 1 });
        userRepository.checkPassword.mockResolvedValue(false);

        // Act + Assert — When / Then
        await expect(
            authService.login('user@example.com', 'senhaErrada')
        ).rejects.toThrow('Credenciais inválidas');
    });

    test('bloqueio após 3 tentativas', async () => {
        // Arrange
        userRepository.getFailedAttempts.mockResolvedValue(2);

        // Act + Assert
        await expect(
            authService.login('user@example.com', 'errada')
        ).rejects.toThrow('Conta bloqueada');

        expect(userRepository.blockAccount).toHaveBeenCalledTimes(1);
    });
});
```

PADRÕES OBRIGATÓRIOS:
- `jest.fn()` para cada método mockado
- `.mockResolvedValue(...)` / `.mockReturnValue(...)` para configurar retornos
- `expect(fn).toHaveBeenCalledWith(...)` para verificar chamadas
- `await expect(promise).rejects.toThrow(...)` para erros async
- `afterEach(() => jest.clearAllMocks())` sempre presente
- Scenario Outline → `test.each([...])` com os dados da tabela""",

        "vitest": """LINGUAGEM: JavaScript (ES2022) | FRAMEWORK: Vitest 1+

ESTRUTURA DO ARQUIVO:
```javascript
import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';
// import { AuthService } from './authService.js';

describe('Login de Usuário', () => {

    let authService;
    let userRepository;
    let tokenService;

    beforeEach(() => {
        userRepository = {
            findByEmail:     vi.fn(),
            checkPassword:   vi.fn(),
            getFailedAttempts: vi.fn(),
            blockAccount:    vi.fn(),
        };
        tokenService  = { generate: vi.fn() };
        authService   = new AuthService({ userRepository, tokenService });
    });

    afterEach(() => vi.clearAllMocks());

    test('login com credenciais válidas', async () => {
        userRepository.findByEmail.mockResolvedValue({ id: 1, active: true });
        tokenService.generate.mockReturnValue('jwt-token-abc123');

        const result = await authService.login('user@example.com', 'Senha@123');

        expect(result.success).toBe(true);
        expect(result.token).toBe('jwt-token-abc123');
        expect(userRepository.findByEmail).toHaveBeenCalledWith('user@example.com');
    });

    test('login com senha incorreta lança erro', async () => {
        userRepository.findByEmail.mockResolvedValue({ id: 1 });
        userRepository.checkPassword.mockResolvedValue(false);

        await expect(
            authService.login('user@example.com', 'senhaErrada')
        ).rejects.toThrow('Credenciais inválidas');
    });
});
```

PADRÕES OBRIGATÓRIOS:
- `vi.fn()` em vez de `jest.fn()`
- Estrutura idêntica ao Jest, apenas com imports do `vitest`
- `vi.clearAllMocks()` no afterEach
- Scenario Outline → `test.each([...])`""",

        "mocha": """LINGUAGEM: JavaScript (ES2022) | FRAMEWORK: Mocha 10+ + Chai + Sinon

ESTRUTURA DO ARQUIVO:
```javascript
const { expect } = require('chai');
const sinon      = require('sinon');
// const { AuthService } = require('./authService');

describe('Login de Usuário', function () {

    let authService, userRepository, tokenService;

    beforeEach(function () {
        userRepository = {
            findByEmail:      sinon.stub(),
            checkPassword:    sinon.stub(),
            getFailedAttempts: sinon.stub(),
            blockAccount:     sinon.stub(),
        };
        tokenService  = { generate: sinon.stub() };
        authService   = new AuthService({ userRepository, tokenService });
    });

    afterEach(function () { sinon.restore(); });

    it('deve autenticar com credenciais válidas', async function () {
        userRepository.findByEmail.resolves({ id: 1, active: true });
        tokenService.generate.returns('jwt-token-abc123');

        const result = await authService.login('user@example.com', 'Senha@123');

        expect(result).to.have.property('success', true);
        expect(result).to.have.property('token', 'jwt-token-abc123');
        expect(userRepository.findByEmail.calledOnceWith('user@example.com')).to.be.true;
    });

    it('deve rejeitar senha incorreta', async function () {
        userRepository.findByEmail.resolves({ id: 1 });
        userRepository.checkPassword.resolves(false);

        await expect(
            authService.login('user@example.com', 'senhaErrada')
        ).to.be.rejectedWith('Credenciais inválidas');
    });
});
```

PADRÕES OBRIGATÓRIOS:
- `sinon.stub()` para mocks; `sinon.restore()` no afterEach
- `.resolves(...)` / `.returns(...)` para retornos assíncronos/síncronos
- `expect(...).to.equal(...)` / `expect(...).to.have.property(...)` como assertions
- `expect(promise).to.be.rejectedWith(...)` para erros (requer chai-as-promised)""",
    },

    "typescript": {
        "jest": """LINGUAGEM: TypeScript 5+ | FRAMEWORK: Jest 29+ (ts-jest)

ESTRUTURA DO ARQUIVO:
```typescript
import { describe, test, expect, beforeEach, afterEach, jest } from '@jest/globals';
// import { AuthService, AuthenticationError } from './authService';

interface UserRepository {
    findByEmail(email: string): Promise<User | null>;
    checkPassword(userId: number, password: string): Promise<boolean>;
    getFailedAttempts(email: string): Promise<number>;
    blockAccount(email: string): Promise<void>;
}

interface TokenService {
    generate(userId: number): string;
}

describe('Login de Usuário', () => {

    let authService: AuthService;
    let userRepository: jest.Mocked<UserRepository>;
    let tokenService: jest.Mocked<TokenService>;

    beforeEach(() => {
        userRepository = {
            findByEmail:       jest.fn(),
            checkPassword:     jest.fn(),
            getFailedAttempts: jest.fn(),
            blockAccount:      jest.fn(),
        } as jest.Mocked<UserRepository>;

        tokenService = { generate: jest.fn() } as jest.Mocked<TokenService>;
        authService  = new AuthService({ userRepository, tokenService });
    });

    afterEach(() => jest.clearAllMocks());

    test('login com credenciais válidas retorna token', async () => {
        // Arrange
        userRepository.findByEmail.mockResolvedValue({ id: 1, email: 'user@example.com', active: true });
        tokenService.generate.mockReturnValue('jwt-token-abc123');

        // Act
        const result = await authService.login('user@example.com', 'Senha@123');

        // Assert
        expect(result.success).toBe(true);
        expect(result.token).toBe('jwt-token-abc123');
        expect(userRepository.findByEmail).toHaveBeenCalledWith('user@example.com');
    });

    test('login com senha incorreta lança AuthenticationError', async () => {
        userRepository.findByEmail.mockResolvedValue({ id: 1, email: 'user@example.com', active: true });
        userRepository.checkPassword.mockResolvedValue(false);

        await expect(
            authService.login('user@example.com', 'senhaErrada')
        ).rejects.toThrow(AuthenticationError);
    });

    test.each([
        ['admin@empresa.com', 'Admin@123', true],
        ['user@empresa.com',  'User@456',  true],
    ])('login parametrizado: %s', async (email, password, expectedSuccess) => {
        userRepository.findByEmail.mockResolvedValue({ id: 1, active: true });
        tokenService.generate.mockReturnValue('token');

        const result = await authService.login(email, password);
        expect(result.success).toBe(expectedSuccess);
    });
});
```

PADRÕES OBRIGATÓRIOS:
- `jest.Mocked<InterfaceType>` para typing dos mocks
- Defina interfaces para dependências no arquivo de teste (ou importe)
- `.mockResolvedValue` / `.mockReturnValue` para configurar stubs tipados
- `rejects.toThrow(ConcreteErrorClass)` para erros com tipagem
- `test.each([...])` para Scenario Outline""",

        "vitest": """LINGUAGEM: TypeScript 5+ | FRAMEWORK: Vitest 1+

ESTRUTURA DO ARQUIVO:
```typescript
import { describe, test, expect, beforeEach, afterEach, vi, type MockedFunction } from 'vitest';
// import { AuthService, type UserRepository, type TokenService } from './authService';

describe('Login de Usuário', () => {

    let authService: AuthService;
    let findByEmail: MockedFunction<UserRepository['findByEmail']>;
    let checkPassword: MockedFunction<UserRepository['checkPassword']>;
    let generateToken: MockedFunction<TokenService['generate']>;

    beforeEach(() => {
        findByEmail   = vi.fn();
        checkPassword = vi.fn();
        generateToken = vi.fn();

        authService = new AuthService({
            userRepository: { findByEmail, checkPassword, getFailedAttempts: vi.fn(), blockAccount: vi.fn() },
            tokenService:   { generate: generateToken },
        });
    });

    afterEach(() => vi.clearAllMocks());

    test('login com credenciais válidas', async () => {
        findByEmail.mockResolvedValue({ id: 1, email: 'user@example.com', active: true });
        generateToken.mockReturnValue('jwt-token-abc123');

        const result = await authService.login('user@example.com', 'Senha@123');

        expect(result.success).toBe(true);
        expect(result.token).toBe('jwt-token-abc123');
        expect(findByEmail).toHaveBeenCalledWith('user@example.com');
    });

    test('login com senha incorreta lança erro', async () => {
        findByEmail.mockResolvedValue({ id: 1, active: true });
        checkPassword.mockResolvedValue(false);

        await expect(authService.login('user@example.com', 'errada')).rejects.toThrow();
    });

    test.each([
        ['admin@empresa.com', 'Admin@123', 'token-admin'],
        ['user@empresa.com',  'User@456',  'token-user'],
    ])('login para %s retorna %s', async (email, password, expectedToken) => {
        findByEmail.mockResolvedValue({ id: 1, active: true });
        generateToken.mockReturnValue(expectedToken);

        const result = await authService.login(email, password);
        expect(result.token).toBe(expectedToken);
    });
});
```""",
    },

    "java": {
        "junit5": """LINGUAGEM: Java 17+ | FRAMEWORK: JUnit 5 + Mockito 5

ESTRUTURA DO ARQUIVO:
```java
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoExtension;
import org.junit.jupiter.api.extension.ExtendWith;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("Login de Usuário")
class LoginDeUsuarioTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private TokenService tokenService;

    @InjectMocks
    private AuthService authService;

    @BeforeEach
    void setUp() {
        // Background: sistema de autenticação disponível — mocks inicializados via @Mock
    }

    @Test
    @DisplayName("login com credenciais válidas retorna token")
    void loginComCredenciaisValidas() {
        // Arrange — Given
        User user = new User(1L, "user@example.com", true);
        when(userRepository.findByEmail("user@example.com")).thenReturn(Optional.of(user));
        when(tokenService.generate(user)).thenReturn("jwt-token-abc123");

        // Act — When
        AuthResult result = authService.login("user@example.com", "Senha@123");

        // Assert — Then
        assertTrue(result.isSuccess());
        assertEquals("jwt-token-abc123", result.getToken());
        verify(userRepository, times(1)).findByEmail("user@example.com");
    }

    @Test
    @DisplayName("login com senha incorreta lança AuthenticationException")
    void loginComSenhaIncorreta() {
        // Arrange — Given
        User user = new User(1L, "user@example.com", true);
        when(userRepository.findByEmail("user@example.com")).thenReturn(Optional.of(user));
        when(userRepository.checkPassword(user, "senhaErrada")).thenReturn(false);

        // Act + Assert — When / Then
        AuthenticationException ex = assertThrows(
            AuthenticationException.class,
            () -> authService.login("user@example.com", "senhaErrada")
        );
        assertThat(ex.getMessage(), containsString("Credenciais inválidas"));
    }

    @Test
    @DisplayName("conta bloqueada após 3 tentativas")
    void bloqueioAposTresTentativas() {
        // Arrange
        when(userRepository.getFailedAttempts("user@example.com")).thenReturn(2);

        // Act + Assert
        assertThrows(AccountBlockedException.class,
            () -> authService.login("user@example.com", "errada"));

        verify(userRepository).blockAccount("user@example.com");
    }

    @ParameterizedTest
    @CsvSource({
        "admin@empresa.com, Admin@123, ROLE_ADMIN",
        "user@empresa.com,  User@456,  ROLE_USER",
    })
    @DisplayName("login parametrizado por perfil")
    void loginParametrizadoPorPerfil(String email, String password, String expectedRole) {
        User user = new User(1L, email, true, Role.valueOf(expectedRole));
        when(userRepository.findByEmail(email)).thenReturn(Optional.of(user));
        when(tokenService.generate(user)).thenReturn("token-" + expectedRole.toLowerCase());

        AuthResult result = authService.login(email, password);

        assertEquals(expectedRole, result.getRole());
    }
}
```

PADRÕES OBRIGATÓRIOS:
- `@ExtendWith(MockitoExtension.class)` + `@Mock` + `@InjectMocks`
- `when(...).thenReturn(...)` para configurar mocks
- `verify(mock, times(N)).metodo(...)` para verificar interações
- `assertThrows(ExceptionClass.class, () -> ...)` para erros
- `@ParameterizedTest` + `@CsvSource` para Scenario Outline""",

        "testng": """LINGUAGEM: Java 17+ | FRAMEWORK: TestNG 7+ + Mockito 5

ESTRUTURA DO ARQUIVO:
```java
import org.testng.annotations.*;
import org.mockito.Mock;
import org.mockito.InjectMocks;
import org.mockito.MockitoAnnotations;

import static org.testng.Assert.*;
import static org.mockito.Mockito.*;

public class LoginDeUsuarioTest {

    @Mock private UserRepository userRepository;
    @Mock private TokenService   tokenService;

    @InjectMocks private AuthService authService;

    private AutoCloseable mocks;

    @BeforeMethod
    public void setUp() {
        mocks = MockitoAnnotations.openMocks(this);
    }

    @AfterMethod
    public void tearDown() throws Exception { mocks.close(); }

    @Test(description = "login com credenciais válidas retorna token")
    public void loginComCredenciaisValidas() {
        // Arrange
        User user = new User(1L, "user@example.com", true);
        when(userRepository.findByEmail("user@example.com")).thenReturn(Optional.of(user));
        when(tokenService.generate(user)).thenReturn("jwt-token-abc123");

        // Act
        AuthResult result = authService.login("user@example.com", "Senha@123");

        // Assert
        assertTrue(result.isSuccess());
        assertEquals(result.getToken(), "jwt-token-abc123");
        verify(userRepository).findByEmail("user@example.com");
    }

    @Test(description = "login com senha incorreta lança exceção",
          expectedExceptions = AuthenticationException.class,
          expectedExceptionsMessageRegExp = ".*Credenciais inválidas.*")
    public void loginComSenhaIncorreta() {
        when(userRepository.findByEmail(anyString())).thenReturn(Optional.of(new User()));
        when(userRepository.checkPassword(any(), eq("senhaErrada"))).thenReturn(false);

        authService.login("user@example.com", "senhaErrada");
    }

    @DataProvider(name = "perfisDeAcesso")
    public Object[][] perfisDeAcesso() {
        return new Object[][] {
            { "admin@empresa.com", "Admin@123", "ROLE_ADMIN" },
            { "user@empresa.com",  "User@456",  "ROLE_USER"  },
        };
    }

    @Test(dataProvider = "perfisDeAcesso")
    public void loginParametrizado(String email, String password, String expectedRole) {
        User user = new User(1L, email, true, Role.valueOf(expectedRole));
        when(userRepository.findByEmail(email)).thenReturn(Optional.of(user));
        when(tokenService.generate(user)).thenReturn("token");

        AuthResult result = authService.login(email, password);
        assertEquals(result.getRole(), expectedRole);
    }
}
```""",
    },

    "csharp": {
        "nunit": """LINGUAGEM: C# 12 / .NET 8 | FRAMEWORK: NUnit 4 + NSubstitute

ESTRUTURA DO ARQUIVO:
```csharp
using NUnit.Framework;
using NSubstitute;
using FluentAssertions;

// using YourApp.Auth;

[TestFixture]
[Description("Login de Usuário")]
public class LoginDeUsuarioTests
{
    private IUserRepository _userRepository;
    private ITokenService   _tokenService;
    private AuthService     _sut;

    [SetUp]
    public void SetUp()
    {
        // Background — dependências substituídas por fakes
        _userRepository = Substitute.For<IUserRepository>();
        _tokenService   = Substitute.For<ITokenService>();
        _sut            = new AuthService(_userRepository, _tokenService);
    }

    [Test]
    [Description("login com credenciais válidas retorna token")]
    public async Task Login_ComCredenciaisValidas_RetornaToken()
    {
        // Arrange — Given
        var user = new User { Id = 1, Email = "user@example.com", IsActive = true };
        _userRepository.FindByEmailAsync("user@example.com").Returns(user);
        _tokenService.Generate(user).Returns("jwt-token-abc123");

        // Act — When
        var result = await _sut.LoginAsync("user@example.com", "Senha@123");

        // Assert — Then
        result.Success.Should().BeTrue();
        result.Token.Should().Be("jwt-token-abc123");
        await _userRepository.Received(1).FindByEmailAsync("user@example.com");
    }

    [Test]
    [Description("login com senha incorreta lança AuthenticationException")]
    public void Login_ComSenhaIncorreta_LancaExcecao()
    {
        // Arrange
        _userRepository.FindByEmailAsync(Arg.Any<string>()).Returns(new User { Id = 1 });
        _userRepository.CheckPasswordAsync(Arg.Any<User>(), "senhaErrada").Returns(false);

        // Act + Assert
        var act = async () => await _sut.LoginAsync("user@example.com", "senhaErrada");
        act.Should().ThrowAsync<AuthenticationException>()
           .WithMessage("*Credenciais inválidas*");
    }

    [TestCase("admin@empresa.com", "Admin@123", "ROLE_ADMIN")]
    [TestCase("user@empresa.com",  "User@456",  "ROLE_USER")]
    [Description("login parametrizado por perfil")]
    public async Task Login_Parametrizado(string email, string password, string expectedRole)
    {
        var user = new User { Id = 1, Email = email, Role = expectedRole };
        _userRepository.FindByEmailAsync(email).Returns(user);
        _tokenService.Generate(user).Returns("token");

        var result = await _sut.LoginAsync(email, password);

        result.Role.Should().Be(expectedRole);
    }
}
```

PADRÕES OBRIGATÓRIOS:
- `NSubstitute.Substitute.For<IInterface>()` para mocks
- `.Returns(...)` para configurar retornos; `.Received(N)` para verificar chamadas
- `FluentAssertions`: `.Should().Be(...)`, `.Should().BeTrue()`, `.Should().ThrowAsync<>()`
- `[TestCase(...)]` para Scenario Outline""",

        "xunit": """LINGUAGEM: C# 12 / .NET 8 | FRAMEWORK: xUnit 2+ + NSubstitute + FluentAssertions

ESTRUTURA DO ARQUIVO:
```csharp
using Xunit;
using NSubstitute;
using FluentAssertions;

// using YourApp.Auth;

public class LoginDeUsuarioTests
{
    private readonly IUserRepository _userRepository;
    private readonly ITokenService   _tokenService;
    private readonly AuthService     _sut;

    public LoginDeUsuarioTests()
    {
        // Background — injeção via construtor (estilo xUnit)
        _userRepository = Substitute.For<IUserRepository>();
        _tokenService   = Substitute.For<ITokenService>();
        _sut            = new AuthService(_userRepository, _tokenService);
    }

    [Fact]
    [Trait("Feature", "Login de Usuário")]
    public async Task Login_ComCredenciaisValidas_RetornaToken()
    {
        // Arrange
        var user = new User { Id = 1, Email = "user@example.com", IsActive = true };
        _userRepository.FindByEmailAsync("user@example.com").Returns(user);
        _tokenService.Generate(user).Returns("jwt-token-abc123");

        // Act
        var result = await _sut.LoginAsync("user@example.com", "Senha@123");

        // Assert
        result.Success.Should().BeTrue();
        result.Token.Should().Be("jwt-token-abc123");
        await _userRepository.Received(1).FindByEmailAsync("user@example.com");
    }

    [Fact]
    public async Task Login_ComSenhaIncorreta_LancaAuthenticationException()
    {
        _userRepository.FindByEmailAsync(Arg.Any<string>()).Returns(new User { Id = 1 });
        _userRepository.CheckPasswordAsync(Arg.Any<User>(), "senhaErrada").Returns(false);

        var act = () => _sut.LoginAsync("user@example.com", "senhaErrada");
        await act.Should().ThrowAsync<AuthenticationException>()
                 .WithMessage("*Credenciais inválidas*");
    }

    [Theory]
    [InlineData("admin@empresa.com", "Admin@123", "ROLE_ADMIN")]
    [InlineData("user@empresa.com",  "User@456",  "ROLE_USER")]
    public async Task Login_Parametrizado(string email, string password, string expectedRole)
    {
        var user = new User { Id = 1, Email = email, Role = expectedRole };
        _userRepository.FindByEmailAsync(email).Returns(user);
        _tokenService.Generate(user).Returns("token");

        var result = await _sut.LoginAsync(email, password);
        result.Role.Should().Be(expectedRole);
    }
}
```

PADRÕES OBRIGATÓRIOS:
- `[Fact]` para testes simples; `[Theory]` + `[InlineData]` para Scenario Outline
- Construtor para setup (sem `[SetUp]`)
- FluentAssertions para assertions expressivas""",

        "mstest": """LINGUAGEM: C# 12 / .NET 8 | FRAMEWORK: MSTest v3 + NSubstitute + FluentAssertions

ESTRUTURA DO ARQUIVO:
```csharp
using Microsoft.VisualStudio.TestTools.UnitTesting;
using NSubstitute;
using FluentAssertions;

[TestClass]
public class LoginDeUsuarioTests
{
    private IUserRepository _userRepository;
    private ITokenService   _tokenService;
    private AuthService     _sut;

    [TestInitialize]
    public void Initialize()
    {
        _userRepository = Substitute.For<IUserRepository>();
        _tokenService   = Substitute.For<ITokenService>();
        _sut            = new AuthService(_userRepository, _tokenService);
    }

    [TestMethod]
    [Description("login com credenciais válidas retorna token")]
    public async Task Login_ComCredenciaisValidas_RetornaToken()
    {
        var user = new User { Id = 1, Email = "user@example.com", IsActive = true };
        _userRepository.FindByEmailAsync("user@example.com").Returns(user);
        _tokenService.Generate(user).Returns("jwt-token-abc123");

        var result = await _sut.LoginAsync("user@example.com", "Senha@123");

        result.Success.Should().BeTrue();
        result.Token.Should().Be("jwt-token-abc123");
    }

    [DataTestMethod]
    [DataRow("admin@empresa.com", "Admin@123", "ROLE_ADMIN")]
    [DataRow("user@empresa.com",  "User@456",  "ROLE_USER")]
    public async Task Login_Parametrizado(string email, string password, string expectedRole)
    {
        var user = new User { Id = 1, Email = email, Role = expectedRole };
        _userRepository.FindByEmailAsync(email).Returns(user);
        _tokenService.Generate(user).Returns("token");

        var result = await _sut.LoginAsync(email, password);
        result.Role.Should().Be(expectedRole);
    }
}
```""",
    },

    "go": {
        "testing": """LINGUAGEM: Go 1.22+ | FRAMEWORK: testing (stdlib) + testify/mock

ESTRUTURA DO ARQUIVO:
```go
package auth_test

import (
    "errors"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
)

// --- Mocks ---

type MockUserRepository struct{ mock.Mock }

func (m *MockUserRepository) FindByEmail(email string) (*User, error) {
    args := m.Called(email)
    if args.Get(0) == nil { return nil, args.Error(1) }
    return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserRepository) CheckPassword(user *User, password string) bool {
    return m.Called(user, password).Bool(0)
}

func (m *MockUserRepository) GetFailedAttempts(email string) int {
    return m.Called(email).Int(0)
}

func (m *MockUserRepository) BlockAccount(email string) {
    m.Called(email)
}

type MockTokenService struct{ mock.Mock }

func (m *MockTokenService) Generate(user *User) string {
    return m.Called(user).String(0)
}

// --- Fixture helper ---

func newAuthService(t *testing.T) (*AuthService, *MockUserRepository, *MockTokenService) {
    t.Helper()
    repo  := new(MockUserRepository)
    token := new(MockTokenService)
    svc   := NewAuthService(repo, token)
    return svc, repo, token
}

// --- Tests ---

func TestLoginDeUsuario_LoginComCredenciaisValidas(t *testing.T) {
    // Arrange
    svc, repo, token := newAuthService(t)
    user := &User{ID: 1, Email: "user@example.com", Active: true}
    repo.On("FindByEmail", "user@example.com").Return(user, nil)
    token.On("Generate", user).Return("jwt-token-abc123")

    // Act
    result, err := svc.Login("user@example.com", "Senha@123")

    // Assert
    assert.NoError(t, err)
    assert.True(t, result.Success)
    assert.Equal(t, "jwt-token-abc123", result.Token)
    repo.AssertCalled(t, "FindByEmail", "user@example.com")
}

func TestLoginDeUsuario_LoginComSenhaIncorreta(t *testing.T) {
    svc, repo, _ := newAuthService(t)
    user := &User{ID: 1, Email: "user@example.com", Active: true}
    repo.On("FindByEmail", "user@example.com").Return(user, nil)
    repo.On("CheckPassword", user, "senhaErrada").Return(false)

    _, err := svc.Login("user@example.com", "senhaErrada")

    assert.Error(t, err)
    assert.True(t, errors.Is(err, ErrInvalidCredentials))
}

func TestLoginDeUsuario_BloqueioAposTresTentativas(t *testing.T) {
    svc, repo, _ := newAuthService(t)
    repo.On("GetFailedAttempts", "user@example.com").Return(2)
    repo.On("BlockAccount", "user@example.com").Return()

    _, err := svc.Login("user@example.com", "errada")

    assert.ErrorIs(t, err, ErrAccountBlocked)
    repo.AssertCalled(t, "BlockAccount", "user@example.com")
}
```

PADRÕES OBRIGATÓRIOS:
- Interfaces para dependências + structs Mock que embarcam `mock.Mock`
- `.On("Metodo", args...).Return(values...)` para configurar mocks
- `assert.Equal`, `assert.NoError`, `assert.ErrorIs` como assertions
- `mock.AssertCalled` para verificar interações
- Helper `newXxxService(t)` para evitar repetição de setup""",

        "testify": """LINGUAGEM: Go 1.22+ | FRAMEWORK: testify/suite + testify/mock

ESTRUTURA DO ARQUIVO:
```go
package auth_test

import (
    "errors"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "github.com/stretchr/testify/suite"
)

// --- Mock ---

type MockUserRepository struct{ mock.Mock }

func (m *MockUserRepository) FindByEmail(email string) (*User, error) {
    args := m.Called(email)
    if args.Get(0) == nil { return nil, args.Error(1) }
    return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserRepository) CheckPassword(u *User, pwd string) bool {
    return m.Called(u, pwd).Bool(0)
}

func (m *MockUserRepository) BlockAccount(email string) { m.Called(email) }

// --- Suite ---

type LoginDeUsuarioSuite struct {
    suite.Suite
    svc  *AuthService
    repo *MockUserRepository
    tok  *MockTokenService
}

func (s *LoginDeUsuarioSuite) SetupTest() {
    // Background — reinicia mocks antes de cada teste
    s.repo = new(MockUserRepository)
    s.tok  = new(MockTokenService)
    s.svc  = NewAuthService(s.repo, s.tok)
}

func (s *LoginDeUsuarioSuite) TestLoginComCredenciaisValidas() {
    // Arrange
    user := &User{ID: 1, Email: "user@example.com", Active: true}
    s.repo.On("FindByEmail", "user@example.com").Return(user, nil)
    s.tok.On("Generate", user).Return("jwt-token-abc123")

    // Act
    result, err := s.svc.Login("user@example.com", "Senha@123")

    // Assert
    s.NoError(err)
    s.True(result.Success)
    s.Equal("jwt-token-abc123", result.Token)
    s.repo.AssertCalled(s.T(), "FindByEmail", "user@example.com")
}

func (s *LoginDeUsuarioSuite) TestLoginComSenhaIncorreta() {
    user := &User{ID: 1}
    s.repo.On("FindByEmail", mock.AnythingOfType("string")).Return(user, nil)
    s.repo.On("CheckPassword", user, "senhaErrada").Return(false)

    _, err := s.svc.Login("user@example.com", "senhaErrada")

    s.ErrorIs(err, ErrInvalidCredentials)
}

func TestLoginDeUsuarioSuite(t *testing.T) {
    suite.Run(t, new(LoginDeUsuarioSuite))
}
```""",
    },

    "ruby": {
        "rspec": """LINGUAGEM: Ruby 3.2+ | FRAMEWORK: RSpec 3+ (rspec-mocks integrado)

ESTRUTURA DO ARQUIVO:
```ruby
# frozen_string_literal: true
require 'rspec'
# require_relative '../lib/auth_service'

RSpec.describe 'Login de Usuário' do

  let(:user_repository) { instance_double('UserRepository') }
  let(:token_service)   { instance_double('TokenService')   }
  let(:auth_service)    { AuthService.new(user_repository:, token_service:) }

  before do
    # Background — sistema de autenticação disponível
    allow(user_repository).to receive(:find_by_email)
    allow(user_repository).to receive(:check_password)
    allow(user_repository).to receive(:get_failed_attempts).and_return(0)
    allow(user_repository).to receive(:block_account)
    allow(token_service).to   receive(:generate)
  end

  describe 'login com credenciais válidas' do
    it 'retorna token JWT e marca sucesso' do
      # Arrange
      user = double('User', id: 1, email: 'user@example.com', active?: true)
      allow(user_repository).to receive(:find_by_email).with('user@example.com').and_return(user)
      allow(token_service).to   receive(:generate).with(user).and_return('jwt-token-abc123')

      # Act
      result = auth_service.login(email: 'user@example.com', password: 'Senha@123')

      # Assert
      expect(result.success?).to be true
      expect(result.token).to eq 'jwt-token-abc123'
      expect(user_repository).to have_received(:find_by_email).with('user@example.com').once
    end
  end

  describe 'login com senha incorreta' do
    it 'lança AuthenticationError com mensagem adequada' do
      user = double('User', id: 1, active?: true)
      allow(user_repository).to receive(:find_by_email).and_return(user)
      allow(user_repository).to receive(:check_password).and_return(false)

      expect {
        auth_service.login(email: 'user@example.com', password: 'senhaErrada')
      }.to raise_error(AuthenticationError, /Credenciais inválidas/)
    end
  end

  describe 'bloqueio após 3 tentativas' do
    it 'bloqueia conta e lança AccountBlockedError' do
      allow(user_repository).to receive(:get_failed_attempts).and_return(2)

      expect {
        auth_service.login(email: 'user@example.com', password: 'errada')
      }.to raise_error(AccountBlockedError)

      expect(user_repository).to have_received(:block_account).once
    end
  end

  describe 'login parametrizado por perfil' do
    [
      ['admin@empresa.com', 'Admin@123', 'ROLE_ADMIN'],
      ['user@empresa.com',  'User@456',  'ROLE_USER'],
    ].each do |email, password, expected_role|
      it "#{email} recebe role #{expected_role}" do
        user = double('User', id: 1, email:, role: expected_role, active?: true)
        allow(user_repository).to receive(:find_by_email).with(email).and_return(user)
        allow(token_service).to   receive(:generate).and_return('token')

        result = auth_service.login(email:, password:)
        expect(result.role).to eq expected_role
      end
    end
  end
end
```

PADRÕES OBRIGATÓRIOS:
- `instance_double` ou `double` para mocks verificados
- `allow(...).to receive(...).and_return(...)` para stubs
- `expect(...).to have_received(...).once` para verificação de chamadas
- `expect { ... }.to raise_error(ErrorClass, /mensagem/)` para erros
- Loop `each` para Scenario Outline""",

        "minitest": """LINGUAGEM: Ruby 3.2+ | FRAMEWORK: Minitest 5+ + Minitest::Mock

ESTRUTURA DO ARQUIVO:
```ruby
# frozen_string_literal: true
require 'minitest/autorun'
require 'minitest/mock'
# require_relative '../lib/auth_service'

class LoginDeUsuarioTest < Minitest::Test

  def setup
    # Background — mocks inicializados antes de cada teste
    @user_repository = Minitest::Mock.new
    @token_service   = Minitest::Mock.new
    @auth_service    = AuthService.new(
      user_repository: @user_repository,
      token_service:   @token_service
    )
  end

  def test_login_com_credenciais_validas
    # Arrange
    user = OpenStruct.new(id: 1, email: 'user@example.com', active?: true)
    @user_repository.expect :find_by_email, user,   ['user@example.com']
    @token_service.expect   :generate,      'jwt-token-abc123', [user]

    # Act
    result = @auth_service.login(email: 'user@example.com', password: 'Senha@123')

    # Assert
    assert result.success?,           'deve retornar sucesso'
    assert_equal 'jwt-token-abc123',  result.token
    @user_repository.verify
    @token_service.verify
  end

  def test_login_com_senha_incorreta_lanca_excecao
    user = OpenStruct.new(id: 1, active?: true)
    @user_repository.expect :find_by_email,  user,  ['user@example.com']
    @user_repository.expect :check_password, false, [user, 'senhaErrada']

    assert_raises(AuthenticationError) do
      @auth_service.login(email: 'user@example.com', password: 'senhaErrada')
    end
  end

  def test_bloqueio_apos_tres_tentativas
    @user_repository.expect :get_failed_attempts, 2, ['user@example.com']
    @user_repository.expect :block_account, nil, ['user@example.com']

    assert_raises(AccountBlockedError) do
      @auth_service.login(email: 'user@example.com', password: 'errada')
    end

    @user_repository.verify
  end
end
```

PADRÕES OBRIGATÓRIOS:
- `Minitest::Mock.new` + `.expect :metodo, retorno, [args]`
- `.verify` no final de cada teste que usa mocks
- `assert_raises(ErrorClass) { ... }` para erros
- `assert_equal valor_esperado, valor_real` (ordem: esperado primeiro)""",
    },

    "kotlin": {
        "junit5": """LINGUAGEM: Kotlin 1.9+ | FRAMEWORK: JUnit 5 + MockK 1.13+

ESTRUTURA DO ARQUIVO:
```kotlin
import io.mockk.*
import org.junit.jupiter.api.*
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import kotlin.test.assertEquals
import kotlin.test.assertTrue

@DisplayName("Login de Usuário")
class LoginDeUsuarioTest {

    private lateinit var userRepository: UserRepository
    private lateinit var tokenService:   TokenService
    private lateinit var authService:    AuthService

    @BeforeEach
    fun setUp() {
        // Background — mocks inicializados via MockK
        userRepository = mockk()
        tokenService   = mockk()
        authService    = AuthService(userRepository, tokenService)
    }

    @AfterEach
    fun tearDown() = clearAllMocks()

    @Test
    @DisplayName("login com credenciais válidas retorna token")
    fun `login com credenciais validas retorna token`() {
        // Arrange
        val user = User(id = 1L, email = "user@example.com", active = true)
        every { userRepository.findByEmail("user@example.com") } returns user
        every { tokenService.generate(user) } returns "jwt-token-abc123"

        // Act
        val result = authService.login("user@example.com", "Senha@123")

        // Assert
        assertTrue(result.success)
        assertEquals("jwt-token-abc123", result.token)
        verify(exactly = 1) { userRepository.findByEmail("user@example.com") }
    }

    @Test
    @DisplayName("login com senha incorreta lança AuthenticationException")
    fun `login com senha incorreta lanca excecao`() {
        every { userRepository.findByEmail(any()) } returns User(id = 1L, active = true)
        every { userRepository.checkPassword(any(), "senhaErrada") } returns false

        assertThrows<AuthenticationException> {
            authService.login("user@example.com", "senhaErrada")
        }.also { ex ->
            assertTrue(ex.message!!.contains("Credenciais inválidas"))
        }
    }

    @ParameterizedTest
    @CsvSource(
        "admin@empresa.com, Admin@123, ROLE_ADMIN",
        "user@empresa.com,  User@456,  ROLE_USER",
    )
    @DisplayName("login parametrizado por perfil")
    fun `login parametrizado`(email: String, password: String, expectedRole: String) {
        val user = User(id = 1L, email = email, role = Role.valueOf(expectedRole), active = true)
        every { userRepository.findByEmail(email) } returns user
        every { tokenService.generate(user) } returns "token"

        val result = authService.login(email, password)
        assertEquals(expectedRole, result.role.name)
    }
}
```

PADRÕES OBRIGATÓRIOS:
- `mockk()` para criar mocks; `clearAllMocks()` no `@AfterEach`
- `every { mock.metodo(args) } returns valor` para configurar retornos
- `verify(exactly = N) { mock.metodo(args) }` para verificar chamadas
- `assertThrows<ExceptionClass> { ... }` para erros
- `@ParameterizedTest` + `@CsvSource` para Scenario Outline""",

        "kotest": """LINGUAGEM: Kotlin 1.9+ | FRAMEWORK: Kotest 5+ + MockK

ESTRUTURA DO ARQUIVO:
```kotlin
import io.kotest.assertions.throwables.shouldThrow
import io.kotest.core.spec.style.DescribeSpec
import io.kotest.matchers.shouldBe
import io.kotest.matchers.string.shouldContain
import io.mockk.*

class LoginDeUsuarioTest : DescribeSpec({

    val userRepository = mockk<UserRepository>()
    val tokenService   = mockk<TokenService>()
    val authService    = AuthService(userRepository, tokenService)

    beforeEach { clearAllMocks() }

    describe("Login de Usuário") {

        it("login com credenciais válidas retorna token") {
            // Arrange
            val user = User(id = 1L, email = "user@example.com", active = true)
            every { userRepository.findByEmail("user@example.com") } returns user
            every { tokenService.generate(user) } returns "jwt-token-abc123"

            // Act
            val result = authService.login("user@example.com", "Senha@123")

            // Assert
            result.success shouldBe true
            result.token   shouldBe "jwt-token-abc123"
            verify(exactly = 1) { userRepository.findByEmail("user@example.com") }
        }

        it("login com senha incorreta lança AuthenticationException") {
            every { userRepository.findByEmail(any()) } returns User(id = 1L, active = true)
            every { userRepository.checkPassword(any(), "senhaErrada") } returns false

            val ex = shouldThrow<AuthenticationException> {
                authService.login("user@example.com", "senhaErrada")
            }
            ex.message shouldContain "Credenciais inválidas"
        }

        context("Scenario Outline — login por perfil") {
            listOf(
                Triple("admin@empresa.com", "Admin@123", "ROLE_ADMIN"),
                Triple("user@empresa.com",  "User@456",  "ROLE_USER"),
            ).forEach { (email, password, expectedRole) ->
                it("$email recebe role $expectedRole") {
                    val user = User(id = 1L, email = email, role = Role.valueOf(expectedRole), active = true)
                    every { userRepository.findByEmail(email) } returns user
                    every { tokenService.generate(user) } returns "token"

                    val result = authService.login(email, password)
                    result.role.name shouldBe expectedRole
                }
            }
        }
    }
})
```""",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_class_name(text: str) -> str:
    words = re.sub(r"[^a-zA-ZÀ-ú0-9 ]", "", text).split()
    return "".join(w.capitalize() for w in words) if words else "Feature"


def _to_snake_name(text: str) -> str:
    text = re.sub(r"[^a-zA-ZÀ-ú0-9 ]", "", text).lower()
    return "_".join(text.split()) if text.strip() else "test"


def _render_scenario_summary(scenario: GherkinScenario, idx: int) -> str:
    header = f"Cenário {idx}: {scenario.name}"
    if scenario.is_outline:
        header += " [Outline — expanda um teste por linha de Examples]"
    if scenario.tags:
        header += f" @{' @'.join(scenario.tags)}"
    lines = [header]
    for step in scenario.steps:
        lines.append(f"  {step.keyword}: {step.text}")
    if scenario.examples:
        lines.append("  Examples:")
        for row in scenario.examples:
            lines.append(f"    | {' | '.join(row)} |")
    return "\n".join(lines)


def _extract_quoted_values(steps: list[GherkinStep]) -> list[str]:
    """Collect all quoted strings across steps — useful as concrete test data hints."""
    values = []
    for step in steps:
        values.extend(re.findall(r'"([^"]+)"', step.text))
    return values


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class PromptBuilder:
    """Builds (system_instruction, user_prompt) tuples for unit test generation."""

    SYSTEM_INSTRUCTION = (
        "Você é um engenheiro de QA sênior especialista em testes automatizados com 10 anos de experiência. "
        "Sua tarefa é gerar testes unitários REAIS e COMPLETOS a partir de cenários BDD (Gherkin). "
        "NÃO gere stubs vazios nem comentários 'TODO'. Cada teste deve ter: "
        "(1) mocks/fakes das dependências configurados no Arrange, "
        "(2) chamada real ao método do SUT no Act, "
        "(3) assertions concretas sobre o resultado no Assert. "
        "Derive o nome da classe/módulo sob teste (SUT) a partir do nome da Feature. "
        "Para cenários de erro (palavras como 'incorreta', 'inválida', 'bloqueado', 'negado', 'falha'), "
        "use os mecanismos de teste de exceção do framework (pytest.raises, assertThrows, rejects.toThrow, etc.). "
        "Scenario Outline → expanda em múltiplos testes com os valores reais da tabela Examples. "
        "CRÍTICO: Retorne APENAS o bloco de código. "
        "Não escreva nenhum texto antes nem depois do código. "
        "Não inclua frases como 'Aqui está o código' ou 'Espero que isso ajude'. "
        "Comece imediatamente com a primeira linha de código ou com o marcador de abertura de bloco (```)."
    )

    def build(
        self,
        feature: GherkinFeature,
        language_id: str,
        framework_id: str,
        original_bdd: str,
    ) -> tuple[str, str]:
        """Returns (system_instruction, user_prompt)."""
        framework_rules = self._get_framework_rules(language_id, framework_id)

        # Semantic analysis — converts raw Gherkin AST into structured AAA blueprints
        analysis     = ScenarioAnalyzer().analyze(feature)
        analysis_txt = analysis.format_for_prompt()

        # Collect concrete quoted values as a supplementary hint
        all_steps = [
            *feature.background_steps,
            *(s for sc in feature.scenarios for s in sc.steps),
        ]
        quoted_values = _extract_quoted_values(all_steps)
        values_hint = (
            "\nVALORES CONCRETOS adicionais dos steps (use como dados literais nos testes):\n"
            + ", ".join(f'"{v}"' for v in quoted_values[:20])
        ) if quoted_values else ""

        # SUT naming hints derived from semantic analysis
        sut_hint = (
            f"SUT: classe={analysis.sut_class}, variável={analysis.sut_variable}, "
            f"módulo/arquivo={analysis.sut_module}"
        )
        deps_hint = ""
        if analysis.background_deps:
            deps_hint = (
                "Dependências a mockar: "
                + ", ".join(f"{cls} ({var})" for cls, var in analysis.background_deps)
            )

        prompt = f"""Gere uma suíte de testes unitários COMPLETOS E REAIS a partir dos cenários BDD abaixo.

═══════════════════════════════════════════════
GHERKIN ORIGINAL
═══════════════════════════════════════════════
{original_bdd.strip()}

═══════════════════════════════════════════════
ANÁLISE SEMÂNTICA (BLUEPRINTS POR CENÁRIO)
═══════════════════════════════════════════════
{analysis_txt}
{sut_hint}
{deps_hint}{values_hint}

═══════════════════════════════════════════════
PADRÃO OBRIGATÓRIO
═══════════════════════════════════════════════
{_AAA_MAPPING}

═══════════════════════════════════════════════
LINGUAGEM, FRAMEWORK E EXEMPLO CANÔNICO
═══════════════════════════════════════════════
{framework_rules}

═══════════════════════════════════════════════
INSTRUÇÕES FINAIS
═══════════════════════════════════════════════
1. Use os blueprints ARRANGE/ACT/ASSERT acima como esqueleto de cada teste.
2. Use exatamente os nomes de classe, variável e método inferidos nos blueprints.
3. Adapte o exemplo canônico ao domínio da Feature "{feature.name}".
4. Cada cenário Gherkin → exatamente um teste (ou N testes para Outline) com AAA reais.
5. Cada step → comentário inline indicando a fase AAA e o texto original do step.
6. Background → setup/fixture compartilhado; mocks reinicializados a cada teste.
7. Cenários de erro → use o mecanismo de exceção do framework; assert sobre a mensagem.
8. Scenario Outline → um teste por linha de Examples com os valores reais interpolados.
9. NUNCA deixe assertion vazia, assert False, fail() ou TODO sem implementação real.
10. Retorne APENAS o código. Nenhum texto fora do bloco de código."""

        return self.SYSTEM_INSTRUCTION, prompt

    def _get_framework_rules(self, language_id: str, framework_id: str) -> str:
        lang_rules = _FRAMEWORK_RULES.get(language_id, {})
        rules = lang_rules.get(framework_id)
        if not rules:
            return (
                f"Linguagem: {language_id} | Framework: {framework_id}\n"
                "Gere testes com padrão AAA completo: mocks de dependências no Arrange, "
                "chamada real ao SUT no Act, assertions concretas no Assert."
            )
        return rules

    def _build_scenarios_summary(self, feature: GherkinFeature) -> str:
        if not feature.scenarios:
            return "(nenhum cenário encontrado)"
        return "\n\n".join(
            _render_scenario_summary(s, i)
            for i, s in enumerate(feature.scenarios, 1)
        )
