from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class Framework:
    id: str
    label: str
    file_extension: str
    # hint shown in the UI alongside the framework name
    hint: str = ""


@dataclass(frozen=True)
class Language:
    id: str
    label: str
    default_framework: str
    frameworks: List[Framework] = field(default_factory=list)


LANGUAGE_CATALOG: Dict[str, Language] = {
    "python": Language(
        id="python",
        label="Python",
        default_framework="pytest",
        frameworks=[
            Framework("pytest", "pytest", ".py", "pip install pytest"),
            Framework("unittest", "unittest", ".py", "stdlib — sem instalação"),
        ],
    ),
    "javascript": Language(
        id="javascript",
        label="JavaScript",
        default_framework="jest",
        frameworks=[
            Framework("jest", "Jest", ".test.js", "npm install --save-dev jest"),
            Framework("vitest", "Vitest", ".test.js", "npm install --save-dev vitest"),
            Framework("mocha", "Mocha + Chai", ".test.js", "npm install --save-dev mocha chai"),
        ],
    ),
    "typescript": Language(
        id="typescript",
        label="TypeScript",
        default_framework="jest",
        frameworks=[
            Framework("jest", "Jest + ts-jest", ".test.ts", "npm install --save-dev jest ts-jest @types/jest"),
            Framework("vitest", "Vitest", ".test.ts", "npm install --save-dev vitest"),
        ],
    ),
    "java": Language(
        id="java",
        label="Java",
        default_framework="junit5",
        frameworks=[
            Framework("junit5", "JUnit 5", "Test.java", "org.junit.jupiter:junit-jupiter:5.x"),
            Framework("testng", "TestNG", "Test.java", "org.testng:testng:7.x"),
        ],
    ),
    "csharp": Language(
        id="csharp",
        label="C#",
        default_framework="nunit",
        frameworks=[
            Framework("nunit", "NUnit", "Tests.cs", "dotnet add package NUnit"),
            Framework("xunit", "xUnit", "Tests.cs", "dotnet add package xunit"),
            Framework("mstest", "MSTest", "Tests.cs", "dotnet add package MSTest.TestFramework"),
        ],
    ),
    "go": Language(
        id="go",
        label="Go",
        default_framework="testing",
        frameworks=[
            Framework("testing", "testing (stdlib)", "_test.go", "stdlib — sem instalação"),
            Framework("testify", "Testify", "_test.go", "go get github.com/stretchr/testify"),
        ],
    ),
    "ruby": Language(
        id="ruby",
        label="Ruby",
        default_framework="rspec",
        frameworks=[
            Framework("rspec", "RSpec", "_spec.rb", "gem install rspec"),
            Framework("minitest", "Minitest", "_test.rb", "stdlib — sem instalação"),
        ],
    ),
    "kotlin": Language(
        id="kotlin",
        label="Kotlin",
        default_framework="junit5",
        frameworks=[
            Framework("junit5", "JUnit 5", "Test.kt", "org.junit.jupiter:junit-jupiter:5.x"),
            Framework("kotest", "Kotest", "Test.kt", "io.kotest:kotest-runner-junit5:5.x"),
        ],
    ),
}


def get_catalog_dict() -> Dict:
    """Returns a JSON-serialisable representation of the catalog for API responses."""
    return {
        lang_id: {
            "id": lang.id,
            "label": lang.label,
            "default_framework": lang.default_framework,
            "frameworks": [
                {
                    "id": fw.id,
                    "label": fw.label,
                    "file_extension": fw.file_extension,
                    "hint": fw.hint,
                }
                for fw in lang.frameworks
            ],
        }
        for lang_id, lang in LANGUAGE_CATALOG.items()
    }


def get_default_framework(language_id: str) -> str:
    """Returns the default framework id for a given language, or empty string if unknown."""
    lang = LANGUAGE_CATALOG.get(language_id)
    return lang.default_framework if lang else ""


def validate_language_framework(language_id: str, framework_id: str) -> bool:
    """Returns True if the (language, framework) combination is supported."""
    lang = LANGUAGE_CATALOG.get(language_id)
    if not lang:
        return False
    return any(fw.id == framework_id for fw in lang.frameworks)
