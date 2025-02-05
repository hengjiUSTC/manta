<div align="center">
  <img src="image/manta-banner.svg" alt="MantaCoder Banner" width="800"/>
</div>

# MantaCoder

MantaCoder is an intelligent code agent system that self-evolves. Like its namesake, the MantaCoder Ray, it gracefully navigates through code tasks with intelligence and efficiency.

## Features

- **Self-Evolution**: Learns and adapts from interactions
- **Intelligent Processing**: Smart command classification and execution
- **Context Awareness**: Maintains session history for better understanding
- **Tool System**: Extensible framework for custom capabilities

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mantacoder.git
cd mantacoder

# Install
pip install -e .
```

## Usage

### Basic Startup

```bash
MantaCoder --api-key YOUR_API_KEY --base-url YOUR_BASE_URL --model MODEL_NAME
```

### Tool Commands

MantaCoder provides several powerful tools that can be accessed through natural language commands:

#### Command Execution
Execute system commands directly:
```
"Please run ls in the current directory"
-> MantaCoder will use: <execute_command> <command>ls</command> </execute_command>
```

#### File Operations

**Reading Files**:
```
"Show me the contents of config.json"
-> MantaCoder will use: <read_file> <path>config.json</path> </read_file>
```

**Writing Files**:
```
"Create a new Python script called hello.py"
-> MantaCoder will use:
<write_to_file>
<path>hello.py</path>
<content>
print("Hello, World!")
</content>
</write_to_file>
```

**Updating Files**:
```
"Update the React import to include useState"
-> MantaCoder will use:
<replace_in_file>
<path>component.jsx</path>
<diff>
<<<<<<< SEARCH
import React from 'react';
=======
import React, { useState } from 'react';
>>>>>>> REPLACE
</diff>
</replace_in_file>
```

### Special Commands

#### History Review
To see the conversation history:
```
history
```
This will display all previous messages in the current session, including system messages, user inputs, and assistant responses.

#### File Context
To add a file to the conversation context:
```
@path/to/file.txt
```
This makes the file content available to MantaCoder for reference in subsequent interactions.

### Example Interactions

Here are some common ways to interact with MantaCoder:

1. Create a new project:
   ```
   "Create a new React component for a login form"
   ```

2. Modify existing code:
   ```
   "Add input validation to the login form component"
   ```

3. Fix issues:
   ```
   "Debug the authentication flow in auth.js"
   ```

4. Get explanations:
   ```
   "Explain how the routing system works in this project"
   ```

## Testing

To run the test suite, use `pytest`. Ensure that all dependencies are installed (including development dependencies).

```bash
# Use pytest to run the tests
pytest tests/
```

## Architecture

```
mantacoder/
├── mantacoder/
    ├── core/         # Core agent functionality
    ├── llm/          # Language model integration
    ├── session/      # Session management
    ├── tools/        # Extensible tools
    └── prompts/      # System prompts
```

## Examples

The `examples/` directory contains practical demonstrations of using MantaCoder for various project types:

```
examples/
├── snakegame/         # Creating a snakegame web applications with MantaCoder
├── minegame/          # Creating a minesweeper web applications with MantaCoder
```

These examples serve as both documentation and starting points for your own projects. They demonstrate real-world applications of MantaCoder's features and can be used as templates for similar implementations.

## Contributing

We welcome contributions! Please fork the repository and submit a pull request.

## License

MIT License

## Contact

- GitHub: [hengjiUSTC](https://github.com/hengjiUSTC)
