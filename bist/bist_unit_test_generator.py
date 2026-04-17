"""
BIST Unit Test Generator
Gera testes unitários automaticamente usando Claude AI

Suporta:
- Python (pytest, unittest)
- JavaScript/TypeScript (Jest, Vitest)
- Java (JUnit)
- C# (xUnit, NUnit)
- Go (testing)
"""

from anthropic import Anthropic
from typing import List, Dict, Optional
from pathlib import Path
import json
from dataclasses import dataclass


@dataclass
class TestCase:
    """Representa um caso de teste unitário"""
    name: str
    description: str
    test_code: str
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None


@dataclass
class TestSuite:
    """Suite completa de testes unitários"""
    file_path: str
    language: str
    framework: str
    imports: List[str]
    test_cases: List[TestCase]
    fixtures: Optional[str] = None


class BISTUnitTestGenerator:
    """
    Gera testes unitários usando Claude AI
    
    Estratégias:
    1. Análise de código fonte
    2. Identificação de edge cases
    3. Cobertura de branches
    4. Mocking/stubbing automático
    """
    
    def __init__(self, anthropic_api_key: str):
        self.anthropic = Anthropic(api_key=anthropic_api_key)
    
    def generate_tests_from_code(
        self,
        source_code: str,
        language: str,
        framework: str = "auto",
        coverage_threshold: float = 0.9
    ) -> TestSuite:
        """
        Gera testes unitários a partir do código fonte
        
        Args:
            source_code: Código fonte da função/classe
            language: python, javascript, typescript, java, csharp, go
            framework: pytest, jest, junit, xunit, vitest, auto
            coverage_threshold: Cobertura desejada (0.0-1.0)
            
        Returns:
            TestSuite com testes gerados
        """
        
        # Auto-detect framework se não especificado
        if framework == "auto":
            framework = self._detect_framework(language)
        
        # System prompt específico por linguagem
        system_prompt = self._get_system_prompt(language, framework)
        
        user_prompt = f"""
        Analise o código abaixo e gere uma suite COMPLETA de testes unitários.
        
        REQUISITOS:
        1. Cobertura de {coverage_threshold*100}% ou mais
        2. Testes para casos positivos e negativos
        3. Edge cases (null, empty, boundary values)
        4. Testes de exceções/erros
        5. Mocks quando necessário (APIs, DB, filesystem)
        6. Arrange-Act-Assert pattern
        7. Nomes descritivos (test_should_...)
        
        CÓDIGO A TESTAR:
        ```{language}
        {source_code}
        ```
        
        Retorne APENAS JSON no formato:
        {{
            "imports": ["import statement 1", "import statement 2"],
            "fixtures": "fixture code if needed",
            "test_cases": [
                {{
                    "name": "test_should_return_sum_of_two_numbers",
                    "description": "Tests that add() correctly sums two positive integers",
                    "setup_code": "setup code if needed",
                    "test_code": "actual test code",
                    "teardown_code": "cleanup if needed"
                }}
            ]
        }}
        """
        
        # Chama Claude
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        # Parse response
        content = response.content[0].text
        
        # Remove markdown se tiver
        content = content.replace('```json', '').replace('```', '').strip()
        
        test_data = json.loads(content)
        
        # Monta TestSuite
        test_suite = TestSuite(
            file_path=self._generate_test_filename(language, framework),
            language=language,
            framework=framework,
            imports=test_data.get('imports', []),
            fixtures=test_data.get('fixtures'),
            test_cases=[
                TestCase(
                    name=tc['name'],
                    description=tc['description'],
                    test_code=tc['test_code'],
                    setup_code=tc.get('setup_code'),
                    teardown_code=tc.get('teardown_code')
                )
                for tc in test_data['test_cases']
            ]
        )
        
        return test_suite
    
    def generate_tests_from_specs(
        self,
        function_spec: str,
        language: str,
        framework: str = "auto"
    ) -> TestSuite:
        """
        Gera testes a partir de specs/documentação (sem código ainda)
        Útil para TDD!
        
        Args:
            function_spec: Especificação da função
            language: Linguagem alvo
            framework: Framework de testes
            
        Example:
            spec = '''
            Function: calculate_discount(price, discount_percent)
            - Returns discounted price
            - discount_percent must be 0-100
            - Raises ValueError if price < 0
            - Raises ValueError if discount > 100
            '''
        """
        
        if framework == "auto":
            framework = self._detect_framework(language)
        
        system_prompt = self._get_system_prompt(language, framework)
        
        user_prompt = f"""
        A partir da especificação abaixo, gere:
        1. Implementação stub/mock da função
        2. Suite completa de testes unitários
        
        ESPECIFICAÇÃO:
        {function_spec}
        
        Retorne JSON com:
        {{
            "stub_implementation": "código stub",
            "imports": [...],
            "test_cases": [...]
        }}
        """
        
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        content = response.content[0].text.replace('```json', '').replace('```', '').strip()
        test_data = json.loads(content)
        
        # Similar ao método anterior
        test_suite = TestSuite(
            file_path=self._generate_test_filename(language, framework),
            language=language,
            framework=framework,
            imports=test_data.get('imports', []),
            fixtures=test_data.get('stub_implementation'),
            test_cases=[
                TestCase(
                    name=tc['name'],
                    description=tc['description'],
                    test_code=tc['test_code'],
                    setup_code=tc.get('setup_code')
                )
                for tc in test_data['test_cases']
            ]
        )
        
        return test_suite
    
    def improve_existing_tests(
        self,
        existing_test_code: str,
        source_code: str,
        language: str
    ) -> Dict:
        """
        Analisa testes existentes e sugere melhorias
        
        Returns:
            {
                'coverage_gaps': [...],
                'missing_edge_cases': [...],
                'suggested_tests': [TestCase, ...]
            }
        """
        
        user_prompt = f"""
        Analise os testes existentes e identifique:
        1. Gaps de cobertura
        2. Edge cases não testados
        3. Testes faltando (exceções, boundary values)
        
        CÓDIGO FONTE:
        ```{language}
        {source_code}
        ```
        
        TESTES EXISTENTES:
        ```{language}
        {existing_test_code}
        ```
        
        Retorne JSON:
        {{
            "coverage_analysis": "descrição da cobertura atual",
            "coverage_gaps": ["gap 1", "gap 2"],
            "missing_edge_cases": ["case 1", "case 2"],
            "suggested_tests": [
                {{
                    "name": "test_name",
                    "description": "why this is needed",
                    "test_code": "code"
                }}
            ]
        }}
        """
        
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=6000,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        content = response.content[0].text.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    
    def write_test_file(
        self,
        test_suite: TestSuite,
        output_path: str
    ):
        """Escreve suite de testes em arquivo"""
        
        # Template por framework
        if test_suite.framework == "pytest":
            content = self._generate_pytest_file(test_suite)
        elif test_suite.framework == "jest":
            content = self._generate_jest_file(test_suite)
        elif test_suite.framework == "junit":
            content = self._generate_junit_file(test_suite)
        else:
            content = self._generate_generic_file(test_suite)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(content)
        
        print(f"✅ Tests written to: {output_path}")
        print(f"   Framework: {test_suite.framework}")
        print(f"   Test cases: {len(test_suite.test_cases)}")
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _detect_framework(self, language: str) -> str:
        """Auto-detecta framework baseado na linguagem"""
        frameworks = {
            'python': 'pytest',
            'javascript': 'jest',
            'typescript': 'jest',
            'java': 'junit',
            'csharp': 'xunit',
            'go': 'testing'
        }
        return frameworks.get(language.lower(), 'pytest')
    
    def _get_system_prompt(self, language: str, framework: str) -> str:
        """Retorna system prompt específico por framework"""
        
        base_prompt = f"""
        Você é um especialista em testes unitários para {language} usando {framework}.
        
        PRINCÍPIOS:
        1. Testes devem ser isolados (não dependem uns dos outros)
        2. Arrange-Act-Assert pattern
        3. Nomes descritivos (test_should_do_something_when_condition)
        4. Um assert por teste (quando possível)
        5. Use mocks/stubs para dependências externas
        6. Teste edge cases e boundary values
        7. Teste exceções e error handling
        
        OUTPUT:
        - Retorne APENAS JSON válido
        - Sem comentários, sem explicações
        - Código pronto para rodar
        """
        
        # Adiciona especificidades por framework
        if framework == "pytest":
            base_prompt += """
            
            PYTEST ESPECÍFICO:
            - Use fixtures quando apropriado
            - Use pytest.raises() para exceções
            - Use parametrize para testes data-driven
            - Use monkeypatch/mocker para mocking
            """
        
        elif framework == "jest":
            base_prompt += """
            
            JEST ESPECÍFICO:
            - Use describe/it structure
            - Use beforeEach/afterEach quando necessário
            - Use jest.mock() para módulos
            - Use expect().toBe() matchers
            """
        
        elif framework == "junit":
            base_prompt += """
            
            JUNIT ESPECÍFICO:
            - Use @Test annotations
            - Use @BeforeEach/@AfterEach
            - Use Mockito para mocking
            - Use assertEquals, assertThrows, etc
            """
        
        return base_prompt
    
    def _generate_test_filename(self, language: str, framework: str) -> str:
        """Gera nome de arquivo de teste"""
        extensions = {
            'python': '.py',
            'javascript': '.test.js',
            'typescript': '.test.ts',
            'java': 'Test.java',
            'csharp': 'Tests.cs',
            'go': '_test.go'
        }
        
        if framework == "pytest":
            return "test_generated.py"
        elif framework == "jest":
            return "generated.test.js"
        else:
            return f"GeneratedTest{extensions.get(language, '.test')}"
    
    def _generate_pytest_file(self, suite: TestSuite) -> str:
        """Gera arquivo pytest completo"""
        
        content = []
        
        # Imports
        content.append("# Auto-generated by BIST")
        content.append("# Framework: pytest\n")
        for imp in suite.imports:
            content.append(imp)
        content.append("")
        
        # Fixtures (se houver)
        if suite.fixtures:
            content.append(suite.fixtures)
            content.append("")
        
        # Test cases
        for tc in suite.test_cases:
            # Docstring
            content.append(f"def {tc.name}():")
            content.append(f'    """{tc.description}"""')
            
            # Setup
            if tc.setup_code:
                content.append(f"    # Setup")
                for line in tc.setup_code.split('\n'):
                    content.append(f"    {line}")
            
            # Test body
            content.append(f"    # Test")
            for line in tc.test_code.split('\n'):
                content.append(f"    {line}")
            
            # Teardown
            if tc.teardown_code:
                content.append(f"    # Teardown")
                for line in tc.teardown_code.split('\n'):
                    content.append(f"    {line}")
            
            content.append("")
        
        return '\n'.join(content)
    
    def _generate_jest_file(self, suite: TestSuite) -> str:
        """Gera arquivo Jest/Vitest completo"""
        
        content = []
        
        # Imports
        content.append("// Auto-generated by BIST")
        content.append("// Framework: jest\n")
        for imp in suite.imports:
            content.append(imp)
        content.append("")
        
        # Describe block
        content.append("describe('Generated Test Suite', () => {")
        
        # Fixtures
        if suite.fixtures:
            content.append(f"  {suite.fixtures}")
            content.append("")
        
        # Test cases
        for tc in suite.test_cases:
            content.append(f"  it('{tc.description}', () => {{")
            
            if tc.setup_code:
                for line in tc.setup_code.split('\n'):
                    content.append(f"    {line}")
            
            for line in tc.test_code.split('\n'):
                content.append(f"    {line}")
            
            if tc.teardown_code:
                for line in tc.teardown_code.split('\n'):
                    content.append(f"    {line}")
            
            content.append("  });")
            content.append("")
        
        content.append("});")
        
        return '\n'.join(content)
    
    def _generate_junit_file(self, suite: TestSuite) -> str:
        """Gera arquivo JUnit completo"""
        
        content = []
        
        content.append("// Auto-generated by BIST")
        content.append("// Framework: JUnit 5\n")
        
        for imp in suite.imports:
            content.append(imp)
        content.append("")
        
        content.append("public class GeneratedTest {")
        content.append("")
        
        if suite.fixtures:
            content.append(f"    {suite.fixtures}")
            content.append("")
        
        for tc in suite.test_cases:
            content.append("    @Test")
            content.append(f"    public void {tc.name}() {{")
            content.append(f"        // {tc.description}")
            
            if tc.setup_code:
                for line in tc.setup_code.split('\n'):
                    content.append(f"        {line}")
            
            for line in tc.test_code.split('\n'):
                content.append(f"        {line}")
            
            content.append("    }")
            content.append("")
        
        content.append("}")
        
        return '\n'.join(content)
    
    def _generate_generic_file(self, suite: TestSuite) -> str:
        """Fallback genérico"""
        return f"// Tests for {suite.language}\n// Framework: {suite.framework}\n\n" + \
               '\n\n'.join([tc.test_code for tc in suite.test_cases])


# ============================================================================
# CLI Integration
# ============================================================================

def generate_unit_tests_cli(
    source_file: str,
    output_file: str,
    language: str = "auto",
    framework: str = "auto",
    anthropic_key: str = None
):
    """
    CLI wrapper para geração de unit tests
    
    Usage:
        bist unit-gen --source mycode.py --output test_mycode.py
    """
    
    import os
    
    # Lê código fonte
    source_code = Path(source_file).read_text()
    
    # Auto-detect language
    if language == "auto":
        ext = Path(source_file).suffix
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cs': 'csharp',
            '.go': 'go'
        }
        language = language_map.get(ext, 'python')
    
    # Gera testes
    api_key = anthropic_key or os.getenv('ANTHROPIC_API_KEY')
    generator = BISTUnitTestGenerator(api_key)
    
    print(f"🧪 Generating unit tests...")
    print(f"   Source: {source_file}")
    print(f"   Language: {language}")
    print(f"   Framework: {framework}\n")
    
    test_suite = generator.generate_tests_from_code(
        source_code,
        language,
        framework
    )
    
    # Escreve arquivo
    generator.write_test_file(test_suite, output_file)
    
    print(f"\n✅ Done! Generated {len(test_suite.test_cases)} test cases")


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Exemplo: gerar testes para uma função Python
    
    source_code = '''
def calculate_discount(price: float, discount_percent: float) -> float:
    """
    Calcula preço com desconto
    
    Args:
        price: Preço original
        discount_percent: Percentual de desconto (0-100)
        
    Returns:
        Preço com desconto aplicado
        
    Raises:
        ValueError: Se price < 0 ou discount_percent fora de 0-100
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    
    discount_amount = price * (discount_percent / 100)
    return price - discount_amount
    '''
    
    generator = BISTUnitTestGenerator(anthropic_api_key="sk-ant-...")
    
    # Gera testes
    test_suite = generator.generate_tests_from_code(
        source_code=source_code,
        language="python",
        framework="pytest",
        coverage_threshold=0.95
    )
    
    # Escreve arquivo
    generator.write_test_file(test_suite, "test_discount.py")
    
    # Output esperado:
    """
    ✅ Tests written to: test_discount.py
       Framework: pytest
       Test cases: 8
       
    # test_discount.py conterá:
    - test_should_calculate_discount_for_valid_inputs()
    - test_should_return_original_price_when_discount_is_zero()
    - test_should_return_zero_when_discount_is_100_percent()
    - test_should_raise_error_for_negative_price()
    - test_should_raise_error_for_negative_discount()
    - test_should_raise_error_for_discount_over_100()
    - test_should_handle_float_precision()
    - test_should_handle_boundary_values()
    """
