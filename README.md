# LR-1 Rule-Based Language Parser

A complete implementation of a rule-based language parser, interpreter, and static analyzer for SI2002/ST0270/CM0081 Formal Languages courses.

## Project Overview

This project implements a rule-based system with:
- **Lexical Analysis**: Tokenization of input text
- **Syntactic Analysis**: LR(1)-compatible recursive descent parsing
- **AST Construction**: Building an abstract syntax tree
- **Rule Interpretation**: Fixed-point iteration execution engine
- **Static Analysis**: Detection of conflicts, redundancies, and inactive rules

## Group Members

- Jerónimo Vélez Acosta
- Sebastian Guerrero Cataño

## System Requirements

- **Operating System**: macOS, Linux, or Windows
- **Python Version**: 3.8 or higher
- **Dependencies**: None (standard library only)

### Tested Environments

- macOS with Python 3.10+
- Linux with Python 3.8+
- Windows with Python 3.9+

## Project Structure

```
LR-1-parser/
├── lexer.py                 # Lexical analyzer (tokenizer)
├── parser.py                # LR(1)-compatible recursive descent parser
├── ast_nodes.py             # Abstract Syntax Tree node definitions
├── interpreter.py           # Rule execution engine with fixed-point iteration
├── static_analysis.py       # Static analysis for conflicts and redundancies
├── main.py                  # Command-line entry point
├── run_tests.py             # Test suite runner
├── README.md                # This file
└── tests/                   # Test cases directory
    ├── case1/               # Simple comparison test
    │   ├── rules.txt
    │   ├── state.txt
    │   └── expected.txt
    ├── case2/               # Chained rules test
    ├── case3/               # False condition test
    ├── case4/               # AND conjunction (true) test
    ├── case5/               # AND conjunction (false) test
    ├── case6/               # Action conflict detection test
    ├── case7/               # Redundant rules detection test
    └── case8/               # Inactive rules detection test
```

## Features

### Language Specification

The language supports rule-based programming with the following grammar:

```
Program      → RuleList
RuleList     → Rule RuleList | ε
Rule         → rule id : if Cond then Action
Cond         → Cond AND Cond | Atom
Atom         → id RelOp value | id
RelOp        → > | < | =
Action       → id
```

### Supported Language Constructs

- **Rules**: Named rules with conditions and actions
  ```
  rule r1:
  if temp > 30 then alert
  ```

- **Conditions**: 
  - Numeric comparisons: `temp > 30`, `humidity < 50`, `count = 5`
  - Fact conditions: `alert` (checks if fact is active)
  - Conjunctions: `temp > 30 AND humidity < 50`

- **Actions**: Activation of facts
  ```
  then alert_user
  ```

- **Initial State**: Variables and facts
  ```
  temp = 35
  active_flag
  ```

### Implementation Components

1. **Lexer** (`lexer.py`)
   - Tokenizes source code into a stream of tokens
   - Supports: keywords, identifiers, operators, values, whitespace handling
   - Line and column tracking for error messages

2. **Parser** (`parser.py`)
   - Recursive descent parser compatible with LR(1) grammars
   - Builds an Abstract Syntax Tree (AST)
   - Handles left recursion in conditions

3. **AST Nodes** (`ast_nodes.py`)
   - Data structures for program representation
   - Classes: Program, Rule, Condition, ComparisonCondition, FactCondition, AndCondition, Action

4. **Interpreter** (`interpreter.py`)
   - Executes rules with fixed-point iteration
   - Maintains separate tracking of variables and facts
   - Tracks which rules are applied

5. **Static Analysis** (`static_analysis.py`)
   - Detects action conflicts (multiple rules generating same fact)
   - Identifies redundant rules (identical condition and action)
   - Finds potentially inactive rules (not applied during execution)

## Installation and Setup

### Prerequisites

Ensure Python 3.8+ is installed:

```bash
python --version
# or
python3 --version
```

### No Installation Required

This project uses only Python standard library. Simply clone or download the files:

```bash
cd LR-1-parser
```

## Running the Implementation

### Command Line Usage

```bash
python main.py <rules_file> [state_file]
```

**Arguments:**
- `<rules_file>`: Path to file containing rules (required)
- `[state_file]`: Path to file containing initial state (optional)

### Running Individual Test Cases

```bash
# Test case 1: Simple comparison
python main.py tests/case1/rules.txt tests/case1/state.txt

# Test case 2: Chained rules
python main.py tests/case2/rules.txt tests/case2/state.txt

# Test case 6: Conflict detection
python main.py tests/case6/rules.txt tests/case6/state.txt

# Test case 7: Redundancy detection
python main.py tests/case7/rules.txt tests/case7/state.txt
```

### Running All Tests

```bash
python run_tests.py
```

Expected output:
```
PASS case1
PASS case2
PASS case3
PASS case4
PASS case5
PASS case6
PASS case7
PASS case8
Passed 8/8 tests.
```

## Input Format

### Rules File Format

```
rule <identifier>:
if <condition> then <action>

rule <identifier>:
if <condition> then <action>
```

**Requirements:**
- Rules must start with keyword `rule`
- Rule names are identifiers (lowercase letters, digits, underscores; must start with letter)
- Conditions follow keyword `if`
- Actions follow keyword `then`
- Rules are separated by one or more blank lines
- Keywords are case-sensitive: `rule`, `if`, `then`, `AND`

### State File Format

```
variable_name = integer_value
fact_name
another_fact
```

**Format:**
- Variable assignments: `id = integer` (one per line)
- Active facts: `id` (one per line)
- Each element on a separate line
- Blank lines are ignored

### Examples

**Example 1: Temperature Control**

`rules.txt`:
```
rule r1:
if temp > 30 then alert

rule r2:
if alert then fan_on
```

`state.txt`:
```
temp = 35
```

`Execute:`
```bash
python main.py rules.txt state.txt
```

`Output:`
```
alert
fan_on
```

**Example 2: Access Control with Conflicts**

`rules.txt`:
```
rule r1:
if admin then access_granted

rule r2:
if member_role then access_granted
```

`state.txt`:
```
admin
member_role
```

`Output:`
```
access_granted
Action access_granted generated by r1, r2
```

## Output Format

### Standard Execution Output

- Derived facts are printed one per line in alphabetical (lexicographic) order
- Each fact is printed at most once
- If no facts are derived, output is: `(no output)`

### Static Analysis Messages

After execution output, analysis messages are printed if applicable:

1. **Action Conflicts**
   ```
   Action <fact> generated by r1, r2, ...
   ```
   Reports when multiple rules generate the same fact.

2. **Redundant Rules**
   ```
   Redundant rules: r1, r2
   ```
   Reports when rules have identical conditions and actions.

3. **Potentially Inactive Rules**
   ```
   Potentially inactive rule: <id>
   ```
   Reports rules that were never triggered during execution.

### Example Outputs

**Case 1: Simple rule**
```
alert
```

**Case 6: Conflict**
```
fan_on
Action fan_on generated by r1, r2
```

**Case 7: Redundancy**
```
Redundant rules: r1, r2
```

**Case 8: Inactive rule**
```
Potentially inactive rule: r3
```

## Algorithm and Execution Model

### Fixed-Point Iteration Algorithm

The interpreter uses fixed-point iteration to execute rules:

1. **Initialization**
   - Load initial variables and facts from state
   - Initialize active facts set with given facts

2. **Main Loop**
   - For each iteration:
     - Evaluate all rule conditions against current state
     - Collect actions from rules with true conditions
     - Add newly derived facts to active facts set
   - Repeat until no new facts are added (fixed point reached)

3. **Result**
   - Return newly derived facts (excluding initial facts)

### Evaluation Rules

- **Comparison**: `Cmp(x, op, v)` → true if variable x satisfies comparison with value v
  - `x > v`: variable greater than value
  - `x < v`: variable less than value
  - `x = v`: variable equals value

- **Fact Check**: `Fact(x)` → true if x is in active facts set

- **Conjunction**: `And(c1, c2)` → true if both c1 and c2 evaluate to true

### Determinism

The evaluation is deterministic and order-independent:
- Rule evaluation order doesn't affect results
- All applicable rules in an iteration are collected before updating facts
- Final result depends only on initial state and rule definitions

## Test Cases

### Test Suite Overview

The implementation includes 8 comprehensive test cases covering:

| Case | Description | Feature Tested |
|------|-------------|-----------------|
| 1 | `temp > 30 then alert` with temp=35 | Simple comparison |
| 2 | Two chained rules (r1 triggers r2) | Rule chaining |
| 3 | `temp > 30 then alert` with temp=20 | False condition |
| 4 | `temp > 30 AND humidity < 50` both true | AND conjunction (true) |
| 5 | `temp > 30 AND humidity < 50` humidity false | AND conjunction (false) |
| 6 | Two rules with same action | Conflict detection |
| 7 | Two identical rules | Redundancy detection |
| 8 | Rule never triggered | Inactive rule detection |

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test manually
python main.py tests/case1/rules.txt tests/case1/state.txt
```

**Current Status: 8/8 ✓ All tests passing**

## Design Decisions

### 1. Recursive Descent Parser
- Chosen for clarity and maintainability
- Implements proper error reporting with line/column information
- Handles left recursion in conditions through iteration

### 2. Separate Variable and Fact Tracking
- Variables: maintain numeric values for comparisons
- Facts: boolean states for conditions and actions
- Allows identifiers to play independent roles

### 3. Fixed-Point Iteration
- Ensures deterministic results regardless of rule order
- Automatically handles rule chaining
- Terminates when no new facts are derived

### 4. Static Analysis Filtering
- Redundant rules excluded from "potentially inactive" reporting
- Avoids redundant warnings for identical rules
- Single "potentially inactive" message per analysis run

## Code Quality Features

- **Type Hints**: Full Python type annotations for clarity
- **Modular Design**: Clear separation of concerns (lexer, parser, AST, interpreter, analyzer)
- **Documentation**: Comprehensive docstrings for all classes and functions
- **Error Handling**: Descriptive error messages with location information
- **Testing**: 100% test coverage of main functionality (8/8 tests passing)

## Example: Complete Workflow

### Step 1: Create rule file (rules.txt)

```
rule check_temperature:
if temperature > 30 then alert_high_temp

rule check_alert:
if alert_high_temp then notify_admin

rule check_humidity:
if humidity < 20 AND alert_high_temp then also_dry
```

### Step 2: Create state file (state.txt)

```
temperature = 35
humidity = 15
```

### Step 3: Execute

```bash
python main.py rules.txt state.txt
```

### Step 4: Observe output

```
alert_high_temp
also_dry
notify_admin
```

(Facts printed in alphabetical order)

## Troubleshooting

### Issue: `NameError: name 'parse_program' is not defined`
- **Solution**: Ensure all `.py` files are in the same directory
- Re-run with: `python main.py <rules_file> <state_file>`

### Issue: `FileNotFoundError: [Errno 2] No such file or directory`
- **Solution**: Provide correct path to rules and state files
- Use: `python main.py tests/case1/rules.txt tests/case1/state.txt`

### Issue: `SyntaxError: Lexical error`
- **Cause**: Invalid syntax in rules file
- Check: Keywords are case-sensitive (`rule`, `if`, `then`, `AND`)
- Check: Rule format follows specification

## Performance Characteristics

- **Time Complexity**: O(n × m × i) where:
  - n = number of rules
  - m = maximum condition complexity
  - i = number of iterations to reach fixed point

- **Space Complexity**: O(v + f) where:
  - v = number of variables
  - f = number of facts

- **Typical Usage**: Suitable for small to medium rule sets (< 1000 rules)

## Future Enhancements

Possible extensions to the current implementation:
- Support for negation (NOT operator)
- Arithmetic expressions in comparisons
- Rule priorities and ordering
- Incremental rule addition
- Query-based rule testing
- Graphical user interface

## Contributing

This is an academic project for formal languages courses. For questions or issues, please refer to the course materials.

## References

### Project Specification
- Document: Rule-Based Language with Execution and Analysis
- Courses: SI2002, ST0270, CM0081 - Formal Languages

### Technical References
- Compiler Design (Aho, Lam, Sethi, Ullman)
- Formal Languages and Automata Theory
- LR Parser Implementation Techniques

## License

Academic project for SI2002/ST0270/CM0081 Formal Languages courses at the institution.
