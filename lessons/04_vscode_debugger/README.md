# VS Code Debugging

Welcome to the fourth module of the Python Debugging & Code Review Masterclass! In this module, we'll explore Visual Studio Code's powerful integrated debugging capabilities for Python.

## Learning Objectives

By the end of this module, you will be able to:
- Configure VS Code's debugging environment for Python
- Set and manage breakpoints through the VS Code interface
- Use the debugging control panel to navigate code execution
- Examine and modify variables using the Variables panel
- Debug with the Watch, Call Stack, and Breakpoints panels
- Use conditional breakpoints and logpoints
- Debug more complex scenarios like multi-file applications and web services

## Why Use VS Code's Debugger?

While Python's built-in `pdb` debugger is powerful, VS Code's integrated debugging environment offers several advantages:

- **Visual interface**: See your code, variables, and call stack all at once
- **Easier navigation**: Control execution with intuitive buttons rather than commands
- **Live variable watching**: Monitor values without manually printing them
- **Breakpoint management**: Set, disable, and modify breakpoints without changing code
- **Advanced features**: Conditional breakpoints, logpoints, and debug configurations

## Setting Up VS Code for Python Debugging

### Requirements

1. **VS Code**: Make sure you have Visual Studio Code installed
2. **Python Extension**: Install the Microsoft Python extension for VS Code
3. **Python Interpreter**: Configure VS Code to use your project's Python environment

### Configuring the Debugger

1. Open your Python file in VS Code
2. Click the "Run and Debug" icon in the sidebar (or press `Ctrl+Shift+D`)
3. Click "create a launch.json file" and select "Python"
4. Select "Python File" as the debug configuration

This creates a `.vscode/launch.json` file with basic settings. For most Python scripts, the default configuration works well.

## Basic Debugging in VS Code

### Setting Breakpoints

Breakpoints tell the debugger where to pause execution:

1. Click in the gutter (left margin) next to a line number
2. A red dot appears, indicating a breakpoint
3. Click the dot again to remove the breakpoint

### Starting the Debugger

There are several ways to start debugging:

- Press F5 to start debugging the current file
- Click the green "Play" button in the Debug panel
- Right-click in the editor and select "Start Debugging"

### Debugging Controls

Once debugging starts, the Debug toolbar appears with these controls:

- **Continue (F5)**: Run until the next breakpoint
- **Step Over (F10)**: Execute the current line and move to the next one
- **Step Into (F11)**: Move into a function call
- **Step Out (Shift+F11)**: Complete the current function and return to the caller
- **Restart (Ctrl+Shift+F5)**: Stop and restart the debug session
- **Stop (Shift+F5)**: End the debugging session

### Examining Variables

VS Code provides several ways to examine variables:

1. **Variables Panel**: Shows all local and global variables
2. **Watch Panel**: Monitor specific expressions
3. **Hover**: Hover over a variable in the code to see its value
4. **Debug Console**: Evaluate expressions and call functions

### Modifying Variables

You can change variable values during debugging:

1. In the Variables panel, right-click on a variable and select "Set Value"
2. In the Debug Console, type an assignment (e.g., `x = 10`)

## Advanced Debugging Features

### Conditional Breakpoints

Conditional breakpoints only pause execution when a condition is true:

1. Right-click on a breakpoint
2. Select "Edit Breakpoint" and enter a condition
3. The breakpoint will only trigger when the condition evaluates to true

Example: Break when `count > 10 and status == "error"`

### Logpoints

Logpoints print messages without modifying your code:

1. Right-click in the gutter and select "Add Logpoint"
2. Enter a message (can include expressions in curly braces)
3. The message appears in the Debug Console when execution reaches that line

Example: `User {username} logged in with status {status}`

### Data Breakpoints

In some languages, VS Code supports breaking when a variable's value changes:

1. In the Variables panel, right-click a variable
2. Select "Break When Value Changes"

### Expression Evaluation

The Debug Console allows evaluating complex expressions:

1. Press Ctrl+Shift+Y to open the Debug Console
2. Type expressions to evaluate in the current context
3. Access variables, call functions, and import modules

### Multi-file Debugging

VS Code can debug applications spanning multiple files:

1. Set breakpoints in different files
2. Start debugging from the entry point
3. Execution will pause at any breakpoint in any file

## Debugging Specific Python Scenarios

### Debugging Scripts with Arguments

To debug a script that requires command-line arguments:

1. Open `launch.json`
2. Add an `"args"` property with an array of arguments:
   ```json
   {
       "name": "Python: Current File",
       "type": "python",
       "request": "launch",
       "program": "${file}",
       "args": ["--input", "data.txt", "--verbose"]
   }
   ```

### Debugging Flask/Django Applications

VS Code can debug web applications:

1. Create a new debug configuration for your framework
2. Configure ports, environment variables, and other settings
3. Set breakpoints in route handlers or views

### Remote Debugging

You can debug code running on remote machines:

1. Install the `debugpy` package on the remote machine
2. Configure the remote debugger to connect to VS Code
3. Set up a "Remote Attach" debug configuration in VS Code

## VS Code Debugging Tips

1. **Use the Watch panel** for expressions you check frequently
2. **Name your debug configurations** for different scenarios
3. **Use logpoints** instead of adding/removing print statements
4. **Learn keyboard shortcuts** for common debugging actions
5. **Save debug configurations** in version control for team sharing

## Debugging Workflow in VS Code

1. **Set strategic breakpoints** near the suspected problem area
2. **Start debugging** with F5
3. **Step through code** using F10 (step over) and F11 (step into)
4. **Examine variables** in the Variables panel
5. **Set watches** for complex expressions
6. **Modify variables** to test fixes
7. **Continue** to the next breakpoint or area of interest

## When to Use VS Code Debugger vs. pdb

Use **VS Code Debugger** when:
- Working on local development
- Wanting a visual interface
- Dealing with complex applications
- Needing to monitor multiple variables
- Debugging as part of your regular workflow

Use **pdb** when:
- Working in a remote terminal
- Debugging on servers without a GUI
- Needing to automate debugging steps
- Working with minimal dependencies

## Conclusion

VS Code's debugger provides a powerful, user-friendly interface for debugging Python applications. By mastering these tools, you can significantly speed up your debugging process and gain deeper insights into your code's execution.

In the next module, we'll explore common Python errors and strategies for fixing them.

## Further Reading

- [Official VS Code Python Debugging Documentation](https://code.visualstudio.com/docs/python/debugging)
- [Advanced VS Code Debugging Features](https://code.visualstudio.com/docs/editor/debugging)
- [Remote Debugging in VS Code](https://code.visualstudio.com/docs/python/debugging#_remote-debugging)
