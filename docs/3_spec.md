Here’s a summary of what we’ve discussed along with a detailed specification for your command-line tool.

---

## **Summary**

You're building a **Bash script** that wraps the `mflux-generate` command to allow for easy **prompt exploration**, **style selection**, and **running variations with random seeds**. The tool will support **tracking runs, storing metadata, and generating HTML pages** for easy review of outputs.

---

## **Detailed Specification**

### **1. Overview**

- The tool runs `mflux-generate` in a structured way, enabling iterative prompt generation.
- It allows users to explore multiple variations with random seeds and select one for further refinement.
- Outputs are stored in a structured directory with HTML pages for easy browsing.

---

### **2. Command-Line Interface**

- The script will be a **Bash script** designed for Unix-based systems.
- Users interact with it via the command line, providing parameters like:
  - **Prompt** (`--prompt` argument)
  - **Model type** (e.g., `Schnell`, `Dev`)
  - **Steps** (`--steps`, with defaults per model)
  - **Number of variations** (`--variations`, default is 4)
  - **Resolution** (`--resolution`, default is 1024x1024, supports landscape/portrait)
  - **Metadata inclusion** (`--metadata`)
  - **Output directory** (optional)

---

### **3. Default Behaviors & Configurations**

- **Step Defaults**:

  - **Schnell model**: **1 step**
  - **Dev model**: **5 steps**
  - User can override these.

- **Resolution Options**:

  - Default: `1024x1024`
  - Landscape and portrait support with appropriate aspect ratios.
  - Option for regular and large versions.

- **File Structure**:

  - Each session lives in a **specified or auto-created directory**.
  - Runs are stored in subdirectories named sequentially: `run_1/`, `run_2/`, etc.
  - Each run contains:
    - **Generated images**
    - **Metadata JSON** (from `--metadata` flag)
    - **An `index.html` file** for previewing results.

- **Main Directory**:
  - Contains an **overall `index.html`** for navigating different runs.

---

### **4. HTML Output**

- The tool will generate an `index.html` inside each run directory.
- The HTML page will display:
  - All generated images.
  - Metadata details.
  - A **pre-generated command snippet** to rerun or refine a specific image.
- The **main `index.html`** in the root directory will list all runs for easy navigation.

---

### **5. Selecting & Refining Images**

- Users can **select an image** from a run and refine it.
- The HTML output will **generate a ready-to-run Bash command** for continuing a variation.

---

### **6. Metadata Handling**

- The tool will automatically **store metadata in a JSON file**.
- The `--metadata` flag from `mflux-generate` will be used.
- Metadata will include:
  - **Timestamps**
  - **Model parameters**
  - **Prompt history**
  - **Random seed values**

---

### **7. Next Steps**

- Implement the **Bash script** to execute these functionalities.
- Develop the **HTML template** for viewing images and metadata.
- Ensure easy **image selection and refinement workflow**.

---

This spec is now detailed enough for a developer to start implementing the tool. Let me know if you want to refine anything further!
