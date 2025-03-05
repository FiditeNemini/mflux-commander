# Detailed Implementation Blueprint for MFlux Command-Line Tool

After carefully reviewing the specification, I'll develop a comprehensive, step-by-step blueprint for building this Bash script tool that wraps the `mflux-generate` command. I'll then break it down into small, iterative chunks that are appropriately sized for implementation with thorough testing.

## High-Level Architecture

1. **Core Script Structure**: The main Bash script that processes arguments and controls execution flow
2. **Parameter Handling**: Processing user inputs with validation and defaults
3. **Directory Management**: Creating and organizing the file structure
4. **Command Execution**: Running `mflux-generate` with appropriate parameters
5. **Metadata Handling**: Capturing and storing metadata in structured JSON
6. **HTML Generation**: Creating dynamic HTML reports for output visualization
7. **Integration**: Tying all components together into a cohesive tool

## Iterative Development Plan

Breaking down the implementation into small, manageable chunks:

### Phase 1: Foundation and Basic Functionality

1. **Project Setup**

   - Create repository structure
   - Add README with initial documentation
   - Create a basic test harness for Bash scripts

2. **Core Script Structure**

   - Create main script file with executable permissions
   - Implement basic argument parsing
   - Set up help/usage information

3. **Basic Parameter Handling**

   - Implement prompt parameter processing
   - Add model type selection
   - Configure default steps per model

4. **Directory Management**

   - Implement output directory creation
   - Set up run subdirectory structure
   - Create basic file organization

5. **Simple Command Execution**
   - Build basic command execution for `mflux-generate`
   - Handle standard outputs and errors
   - Implement basic error handling

### Phase 2: Advanced Features and Refinement

6. **Enhanced Parameter Handling**

   - Add resolution parameter with aspect ratio support
   - Implement variations parameter
   - Add metadata flag support

7. **Metadata Management**

   - Capture command execution details
   - Store metadata in structured JSON
   - Implement timestamp and run information

8. **Basic HTML Generation**

   - Create simple HTML template for run results
   - Display generated images in a grid
   - Show basic run information

9. **Command Generation for Refinement**
   - Generate reusable command snippets
   - Implement seed selection for refinement
   - Add copy-to-clipboard functionality

### Phase 3: Integration and Polish

10. **Main Index Generation**

    - Create main index.html for navigating runs
    - Implement run sorting and filtering
    - Add search functionality

11. **Enhanced HTML Templates**

    - Improve visual design of HTML outputs
    - Add responsive design elements
    - Implement dark/light mode toggle

12. **Error Handling and Validation**

    - Implement comprehensive input validation
    - Add graceful error handling
    - Provide helpful error messages

13. **Testing and Documentation**

    - Create comprehensive test suite
    - Write detailed usage documentation
    - Add examples and tutorials

14. **Final Integration**
    - Ensure all components work together seamlessly
    - Verify outputs match expected structure
    - Polish user experience

## Refined Step-by-Step Implementation Plan

After reviewing the above plan, I've further refined it into smaller, more testable steps:

### Phase 1: Core Script Foundation

1. **Project Initialization**

   - Create directory structure
   - Add README.md with project overview
   - Set up .gitignore for temporary files
   - Create basic Makefile for testing

2. **Basic Script Creation**

   - Create main script with shebang and permissions
   - Add version and simple help command
   - Implement basic argument validation
   - Create test harness with simple assertions

3. **Argument Parser: Prompt Parameter**

   - Add --prompt argument processing
   - Validate prompt is non-empty
   - Add test cases for prompt validation
   - Implement usage examples for prompts

4. **Argument Parser: Model Selection**
   - Add model type selection (Schnell/Dev)
   - Implement model validation
   - Set default step counts per model
   - Add test cases for model validation

### Phase 2: Directory and Parameter Management

5. **Output Directory Setup**

   - Create output directory handling
   - Implement run subdirectory naming scheme
   - Add timestamp-based organization
   - Test directory structure creation

6. **Run Numbering and Management**

   - Implement sequential run numbering
   - Add ability to list previous runs
   - Create run metadata file structure
   - Test run management functionality

7. **Resolution Parameter Handling**

   - Add --resolution parameter support
   - Implement aspect ratio calculations
   - Add portrait/landscape options
   - Test resolution parameter validation

8. **Variations Parameter**
   - Add --variations parameter
   - Validate number of variations
   - Set appropriate default (4)
   - Test variations parameter

### Phase 3: Command Execution

9. **Basic mflux-generate Command**

   - Construct basic command with required parameters
   - Implement execute function
   - Capture standard output and errors
   - Test command construction

10. **Random Seed Handling**

    - Add random seed generation
    - Implement seed storage mechanism
    - Enable reproducible runs
    - Test seed handling

11. **Command Execution with Error Handling**

    - Add robust error handling
    - Implement timeout mechanism
    - Create retry logic
    - Test error scenarios

12. **Output Capture and Organization**
    - Capture generated image paths
    - Implement file organization
    - Create naming conventions
    - Test output organization

### Phase 4: Metadata and HTML Generation

13. **Basic Metadata Capture**

    - Create metadata JSON structure
    - Capture command parameters
    - Store timestamps and run information
    - Test metadata creation

14. **Enhanced Metadata**

    - Add system information
    - Implement model details capture
    - Store seed values
    - Test complete metadata structure

15. **Basic HTML Template**

    - Create simple HTML template file
    - Implement template variables
    - Add basic styling
    - Test HTML generation

16. **Run-Level HTML Generation**
    - Generate run-specific HTML
    - Implement image grid display
    - Add metadata information section
    - Test run HTML outputs

### Phase 5: Advanced Features and Integration

17. **Command Generation for Refinement**

    - Create reusable command snippets
    - Implement copy functionality
    - Add refinement instructions
    - Test command generation

18. **Main Index HTML**

    - Create main index template
    - Implement run listing functionality
    - Add navigation features
    - Test main index generation

19. **Enhanced HTML Features**

    - Add responsive design
    - Implement dark/light mode
    - Create improved image viewing
    - Test enhanced features

20. **Final Integration and Testing**
    - Ensure all components work together
    - Verify entire workflow
    - Create end-to-end tests
    - Prepare documentation

## Final Implementation Prompts for Code Generation

Now, I'll create a series of prompts for a code-generation LLM to implement each step in a test-driven manner. These prompts will build incrementally, ensuring each step is properly integrated with previous steps.

### Prompt 1: Project Initialization

```
Create a new Bash project called "mflux-wrapper" that will wrap the `mflux-generate` command with enhanced functionality.

1. Setup a clean project structure with:
   - A README.md explaining the purpose of the tool
   - A main script called `mflux-wrapper.sh` with proper shebang and executable permissions
   - A simple Makefile for testing
   - A .gitignore file for temporary files
   - A tests/ directory for test scripts

2. The README should describe that this tool:
   - Wraps the mflux-generate command for image generation
   - Allows for prompt exploration with variations
   - Supports different models (Schnell, Dev) with appropriate defaults
   - Organizes outputs with HTML reports
   - Enables refinement of selected outputs

3. Add a simple version command (-v or --version) that prints the tool version (0.1.0)

4. Create a basic test script in the tests/ directory that verifies:
   - The script is executable
   - The version command works correctly

Ensure all files have appropriate permissions and the main script shows a simple usage message when run without arguments.
```

### Prompt 2: Basic Script Creation and Argument Validation

```
Building on the previously created project structure, enhance the `mflux-wrapper.sh` script with proper argument handling and basic validation:

1. Implement comprehensive help/usage information (-h or --help) that explains:
   - All available parameters
   - Default values
   - Examples of usage

2. Create a function for parsing command-line arguments that supports:
   - --prompt: The text prompt for image generation (required)
   - --model: The model type (Schnell or Dev, default: Schnell)
   - --help: Display usage information
   - --version: Display version information

3. Implement basic validation that ensures:
   - The script exits with an error if no prompt is provided
   - The model type is either "Schnell" or "Dev"
   - Unknown arguments trigger a helpful error message

4. Enhance the test script to verify:
   - The help command provides comprehensive information
   - The script properly validates the presence of a prompt
   - The script validates the model type
   - The script handles unknown arguments gracefully

Make sure the script follows Bash best practices, including:
- Using `set -e` for error handling
- Using functions for code organization
- Including helpful comments
- Implementing proper exit codes for different error conditions
```

### Prompt 3: Advanced Parameter Handling

```
Extend the argument parsing in `mflux-wrapper.sh` to handle additional parameters and implement model-specific defaults:

1. Add support for the following parameters:
   - --steps: Number of steps for generation (default depends on model)
      - Schnell model default: 1 step
      - Dev model default: 5 steps
   - --variations: Number of variations to generate (default: 4)
   - --resolution: Output resolution (default: 1024x1024)
      - Support common formats: square, landscape, portrait
      - Implement parsing for formats like "1024x1024", "landscape", "portrait"
   - --metadata: Flag to include metadata in output

2. Implement validation for these parameters:
   - Steps should be a positive integer
   - Variations should be between 1 and 10
   - Resolution should be a valid format

3. Create a function that converts resolution keywords to actual dimensions:
   - "square" → 1024x1024
   - "landscape" → 1280x768
   - "portrait" → 768x1280
   - Custom dimensions should be validated as WxH format

4. Update the test script to verify:
   - Default values are correctly assigned based on model type
   - Parameter validation works as expected
   - Resolution conversion handles all supported formats
   - Error messages are helpful and specific

Ensure all parameters are properly documented in the help text, including information about defaults and acceptable values.
```

### Prompt 4: Directory Structure Management

```
Enhance the `mflux-wrapper.sh` script to implement output directory management for organizing generated images and reports:

1. Add support for an optional output directory parameter:
   - --output: Directory where results will be stored (default: ./mflux-output)

2. Implement directory structure creation:
   - Create the main output directory if it doesn't exist
   - Create timestamped run directories in the format "run_N_YYYYMMDD_HHMMSS"
   - Add a "logs" subdirectory for command outputs
   - Add an "images" subdirectory for generated images
   - Add a "metadata" subdirectory for JSON metadata

3. Implement a function to get the next run number by:
   - Scanning the output directory for existing run directories
   - Finding the highest number and incrementing it
   - Defaulting to 1 if no runs exist

4. Create a function to generate a unique run identifier that combines:
   - Sequential run number
   - Timestamp
   - A hash of the prompt (first 8 characters)

5. Update the test script to verify:
   - Directories are created with proper permissions
   - Run numbering works correctly
   - The unique run identifier is properly formatted
   - The script handles existing directories gracefully

Make sure to implement proper error handling for file system operations, including permission errors and disk space checks.
```

### Prompt 5: Command Construction and Execution

```
Implement the core command construction and execution functionality in the `mflux-wrapper.sh` script:

1. Create a function to build the mflux-generate command based on parameters:
   - Use the prompt parameter
   - Apply the selected model type
   - Set the number of steps based on defaults or user input
   - Configure the resolution
   - Add the variations parameter
   - Include the metadata flag if specified

2. Implement a function to generate random seeds for variations:
   - Generate one seed per variation
   - Store seeds in an array for later use
   - Ensure seeds are properly documented in metadata

3. Create an execute_command function that:
   - Takes the constructed command
   - Runs it with proper error handling
   - Captures stdout and stderr to log files
   - Returns the command exit status
   - Implements a timeout mechanism

4. Implement a dry-run option (--dry-run) that:
   - Prints the constructed command without executing it
   - Shows what would be executed
   - Displays the directory structure that would be created

5. Update tests to verify:
   - Commands are correctly constructed for different parameter combinations
   - Random seeds are properly generated
   - Command execution captures output correctly
   - Timeout mechanism works as expected
   - Dry-run option displays accurate information

Ensure proper handling of command execution errors, including helpful error messages and appropriate exit codes.
```

### Prompt 6: Metadata Handling and Storage

```
Enhance the `mflux-wrapper.sh` script to implement comprehensive metadata handling:

1. Create a function to build a metadata JSON structure that includes:
   - Command parameters (prompt, model, steps, etc.)
   - Generated seed values
   - Timestamp information (start, end)
   - Run identifier
   - System information (bash version, OS)

2. Implement a function to save metadata to a JSON file:
   - Create a properly formatted JSON file
   - Store it in the metadata directory
   - Ensure it's human-readable with proper indentation
   - Add a unique identifier for each run

3. Create a function to extract metadata from the mflux-generate output:
   - Parse the output to find generated image paths
   - Extract any model-specific information
   - Capture performance metrics if available

4. Implement a metadata display function that:
   - Formats the metadata in a human-readable way
   - Can be called with --show-metadata for a specific run
   - Supports JSON or plain text output formats

5. Update tests to verify:
   - Metadata is correctly structured
   - JSON output is valid
   - Extraction from command output works correctly
   - Display formatting is readable

Make sure to handle potential errors in JSON formatting and file operations, providing informative error messages when issues occur.
```

### Prompt 7: Basic HTML Report Generation

```
Implement basic HTML report generation for the `mflux-wrapper.sh` script:

1. Create a simple HTML template file (template.html) that includes:
   - Basic responsive layout with CSS
   - Placeholders for dynamic content
   - Image grid display area
   - Metadata display section
   - Command reproduction section

2. Implement a function to generate a run-specific HTML report:
   - Use the template to create an index.html in the run directory
   - Replace placeholders with actual content
   - Include all generated images in a grid
   - Display formatted metadata
   - Show command used for generation

3. Add a function to generate reusable command snippets that:
   - Create a command that would reproduce a specific variation
   - Show how to refine a specific output with the same seed
   - Include copy-to-clipboard functionality with JavaScript

4. Create a simple CSS file for styling the reports with:
   - Responsive grid layout
   - Clean, modern design
   - Image hover effects
   - Proper spacing and typography

5. Update tests to verify:
   - HTML generation creates valid HTML
   - All images are properly included
   - Command snippets are correctly formatted
   - CSS is properly linked and functional

Ensure the HTML is valid, responsive, and works in modern browsers. Include basic JavaScript for interactive elements like copying commands.
```

### Prompt 8: Main Index HTML and Navigation

```
Extend the HTML reporting capabilities of the `mflux-wrapper.sh` script to include a main index page and enhanced navigation:

1. Create a main index.html template that:
   - Lists all runs in the output directory
   - Shows thumbnails of generated images for each run
   - Displays run timestamps and prompts
   - Provides sorting and filtering options

2. Implement a function to generate the main index.html that:
   - Scans the output directory for runs
   - Extracts key information from each run's metadata
   - Creates thumbnails for the run preview
   - Updates the index whenever a new run is completed

3. Add navigation features to both the main index and run pages:
   - Back/forward links between pages
   - Breadcrumb navigation
   - Run history navigation

4. Implement a simple search functionality that:
   - Allows filtering runs by prompt text
   - Supports filtering by date ranges
   - Can filter by model type

5. Add a function to regenerate all HTML reports that:
   - Can be triggered with --rebuild-html
   - Updates all run pages and the main index
   - Fixes any missing or corrupted HTML files

6. Update tests to verify:
   - Main index generation works correctly
   - Navigation links are properly created
   - Search functionality works as expected
   - Rebuild functionality correctly updates all files

Ensure all HTML pages are properly linked, navigation is intuitive, and the main index provides a useful overview of all runs.
```

### Prompt 9: Enhanced Image Viewing and Interaction

```
Implement enhanced image viewing and interaction features for the HTML reports:

1. Add a lightbox image viewer to the HTML reports that:
   - Shows full-size images when thumbnails are clicked
   - Supports navigation between images
   - Displays image metadata in the viewer
   - Has zoom functionality

2. Implement side-by-side comparison functionality:
   - Allow selecting multiple images for comparison
   - Show differences between variations
   - Include metadata comparison

3. Add image favoriting/rating functionality:
   - Allow marking preferred variations
   - Store ratings in a local storage or file
   - Show highest-rated images prominently

4. Implement a copy-to-clipboard function for image paths that:
   - Provides easy access to file locations
   - Includes absolute and relative paths
   - Works across different browsers

5. Add a simple slideshow feature for run results that:
   - Cycles through generated images
   - Shows progression of variations
   - Has play/pause controls

6. Update tests to verify:
   - Lightbox functionality works correctly
   - Comparison features operate as expected
   - Rating system properly stores preferences
   - Copy functions work across environments

Ensure all JavaScript functions are properly encapsulated, avoid global namespace pollution, and provide fallbacks for browsers without JavaScript enabled.
```

### Prompt 10: Error Handling and Robustness

```
Enhance the `mflux-wrapper.sh` script with comprehensive error handling and robustness features:

1. Implement thorough input validation with:
   - Detailed error messages for each parameter
   - Suggestions for fixing invalid inputs
   - Examples of correct usage in error messages
   - Type checking for numeric parameters

2. Add robust command execution handling:
   - Implement timeouts for hanging commands
   - Add retry logic for transient failures
   - Capture detailed error information
   - Provide clear error messages for common failures

3. Implement graceful degradation for:
   - Missing dependencies (check for mflux-generate)
   - Permission issues
   - Network connectivity problems
   - Disk space limitations

4. Add a debug mode (--debug) that:
   - Shows verbose output
   - Keeps intermediate files
   - Displays detailed timing information
   - Logs all operations

5. Implement a recovery function that:
   - Can restart from a failed run
   - Detects and completes partial runs
   - Salvages any generated outputs
   - Updates metadata with recovery information

6. Update tests to verify:
   - Error handling correctly identifies issues
   - Recovery functions work as expected
   - Debug output provides useful information
   - The script gracefully handles all error conditions

Ensure all error messages are helpful, specific, and guide the user toward resolution. Implement appropriate exit codes for different error types.
```

### Prompt 11: Command Refinement and Seed Management

```
Enhance the `mflux-wrapper.sh` script with functionality for refining outputs and managing seeds:

1. Implement a refinement mode (--refine) that:
   - Takes a specific run and variation as input
   - Extracts the seed used for that variation
   - Re-runs with the same seed and parameters
   - Allows modifying the prompt while keeping the seed

2. Create a seed management system that:
   - Stores seeds in a retrievable format
   - Allows specifying seeds manually (--seed)
   - Can generate consistent seeds from text
   - Provides seed visualization in reports

3. Implement a variation mode (--variation-mode) with options:
   - "random" - completely random seeds (default)
   - "similar" - seeds with small variations
   - "diverse" - seeds designed to produce maximum variation

4. Add a seed browser in the HTML reports that:
   - Shows thumbnails organized by seed
   - Highlights similar seeds
   - Provides visual indication of seed "distance"
   - Allows filtering by seed characteristics

5. Implement a command history feature that:
   - Tracks all commands run in a session
   - Allows recalling and modifying previous commands
   - Shows the evolution of prompts and parameters
   - Enables creating "branches" of exploration

6. Update tests to verify:
   - Refinement mode correctly preserves seeds
   - Seed management properly stores and retrieves seeds
   - Variation modes produce expected results
   - History tracking accurately records commands

Ensure all seed-related functionality is well-documented and the refinement workflow is intuitive for users exploring variations.
```

### Prompt 12: Final Integration and Documentation

```
Complete the `mflux-wrapper.sh` script with final integration, comprehensive documentation, and polish:

1. Implement comprehensive documentation:
   - Create a detailed man page
   - Add extensive comments in the code
   - Create a usage guide with examples
   - Produce a tutorial for common workflows

2. Add a configuration file system:
   - Support reading defaults from ~/.mflux-wrapper.conf
   - Allow setting persistent preferences
   - Implement configuration validation
   - Add command to generate a default config

3. Create a check-dependencies function that:
   - Verifies all required tools are installed
   - Checks versions of dependencies
   - Suggests installation commands if missing
   - Warns about potential compatibility issues

4. Implement a logging system that:
   - Records all operations to a log file
   - Uses proper log levels (INFO, WARNING, ERROR)
   - Rotates logs to prevent excessive growth
   - Includes timestamps and context

5. Add final integration tests that:
   - Verify the entire workflow end-to-end
   - Test all major features in combination
   - Check for performance issues
   - Validate output correctness

6. Create a release preparation function that:
   - Packages the script for distribution
   - Generates documentation artifacts
   - Creates release notes
   - Performs final validation checks

Ensure the final product is well-documented, robust, and provides a seamless user experience with clear error messages, intuitive behavior, and comprehensive help.
```

## Final Review

After creating these prompts, I've reviewed them to ensure they build incrementally without orphaned code or major complexity jumps:

1. Each prompt builds directly on the previous ones
2. The steps are small enough to be implemented safely with strong testing
3. Each component is fully integrated into the overall workflow
4. Testing is emphasized throughout the development process
5. Best practices for Bash scripting are maintained
6. Error handling is comprehensive
7. The final product meets all the requirements in the specification

These prompts provide a solid foundation for implementing the mflux-wrapper tool in a test-driven, incremental manner. The code generation process should result in a robust, well-documented tool that effectively wraps the mflux-generate command with enhanced functionality for prompt exploration, style selection, and output management.
