# REALITYCHECK

This repository contains artifacts for the paper:
"Principled and Automated Approach for Investigating AR/VR Attacks"

## Note

- The artifacts in this repository include REALITYCHECK source code, instrumentation code, logs and log collection scripts.
- As described in the paper, the investigation begins with log collection, and then we use the REALITYCHECK code to generate provenance graphs.
- Instrumentation is optional and is only required for non-OpenXR applications.

## Dependencies

### Essential:
- networkx==3.1
- matplotlib==3.7.2
- nltk==3.8.1
- spacy==3.6.0
- pyinflect==0.5.1
- pyvis==0.3.2
- en-core-web-sm==3.6.0

### Complete dependencies in our test environment:
- asttokens==2.2.1
- backcall==0.2.0
- blis==0.7.10
- catalogue==2.0.9
- certifi==2023.7.22
- charset-normalizer==3.2.0
- click==8.1.6
- confection==0.1.0
- contourpy==1.1.0
- cycler==0.11.0
- cymem==2.0.7
- decorator==5.1.1
- en-core-web-sm==3.6.0
- executing==1.2.0
- fonttools==4.41.1
- idna==3.4
- importlib-resources==6.0.0
- ipython==8.12.2
- jedi==0.19.0
- Jinja2==3.1.2
- joblib==1.3.1
- jsonpickle==3.0.1
- kiwisolver==1.4.4
- langcodes==3.3.0
- MarkupSafe==2.1.3
- matplotlib==3.7.2
- matplotlib-inline==0.1.6
- murmurhash==1.0.9
- networkx==3.1
- nltk==3.8.1
- numpy==1.24.4
- packaging==23.1
- parso==0.8.3
- pathy==0.10.2
- pexpect==4.8.0
- pickleshare==0.7.5
- Pillow==10.0.0
- preshed==3.0.8
- prompt-toolkit==3.0.39
- ptyprocess==0.7.0
- pure-eval==0.2.2
- pydantic==1.10.12
- Pygments==2.15.1
- pyinflect==0.5.1
- pyparsing==3.0.9
- python-dateutil==2.8.2
- pyvis==0.3.2
- regex==2023.6.3
- requests==2.31.0
- six==1.16.0
- smart-open==6.3.0
- spacy==3.6.0
- spacy-legacy==3.0.12
- spacy-loggers==1.0.4
- srsly==2.4.7
- stack-data==0.6.2
- thinc==8.1.10
- tqdm==4.65.0
- traitlets==5.9.0
- typer==0.9.0
- typing-extensions==4.7.1
- urllib3==2.0.4
- wasabi==1.1.2
- wcwidth==0.2.6
- zipp==3.16.2


## How to collect logs:
1. First, connect your Meta Quest 2 headset to a Windows PC.
2. If your desired applications use non-OpenXR API, instrument the desired applications first by navigating to the instructions in the `Instrumentation` directory.
3. To collect Oculus Logs, you need to have the Meta Quest 2 connected to the PC. 
    * Download the Oculus utility for Meta Quest 2 [here](https://www.oculus.com/download_app/?id=1582076955407037).
    * Navigate to the Oculus installation folder, and find the Support -> oculus-diagnostics folder. For example: C:\Program Files (x86)\Oculus\Support\oculus-diagnostics\OculusLogGatherer.exe\. When you run the tool, you can select the following options:
        - Use last to indicate how much log data you want to export. The default log period is 24 hours.
        - Full logs checkbox to export all available logs
        - Auto submit checkbox to automatically submit the logs to Meta
        - The export, a .zip file, will be copied to the clipboard and saved to your desktop. The .zip export organizes the files by log type.
4. Next, while your device is connected to the PC, perform some configuration changes to redirect the logs to the system log buffer and then to sdcard.
    * Run the following commands through Windows PowerShell or terminal:
        1. `adb logcat -G 256M` (this will increase the space of the system log buffer).
        2. `adb logcat -f /sdcard/log_output.txt > /dev/null 2>&1 &` (this will make sure to redirect OpenXR logs to the system log buffer, and save the log file on your Meta Quest 2's SD card).
    * log_output.txt in SD card of the device will now contain `Logcat`, `Application`, `OpenXR API` and `Instrumented` logs.
5. Run Perfetto script from [here](Log%20Collection/Perfetto%20Config%20and%20Collection/) by running `python perfetto.py` from your PC. The script has been configured to save the logs on the Meta Quest 2 device as well.
6. You can collect Sysmon logs on the Windows PC by following the instructions provided [here](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon). The configuration file for Sysmon is also provided [here](Log%20Collection/Sysmon%20Config%20and%20Collection/).
7. If you chose to disconnect the Meta Quest 2 device from the Windows PC, all the logs will still be collected on the Meta Quest 2 device. Just make sure to re-run the following command after you re-connect the device to your PC:
    * `adb logcat -f /sdcard/log_output.txt > /dev/null 2>&1 &`

## How to stop the logging:
1. To stop the logging:
    - Run `adb shell` via the connected PC to get access to the device's shell
    - Run `ps -A | grep logd`
    - To stop the logcat process, use the kill command followed by the PID you noted in the previous step: `kill <PID>`

This will stop logcat and perfetto logging on your HMD device.

## How to retrieve the the logs from the device:

1. Run `adb pull /sdcard/log_output.txt` from the connected PC. This will provide you with HMD logs, and you can rename these to "hmd.txt" and place them in the `Logs` folder.
2. Run  `adb pull /data/misc/perfetto-traces/trace` from the connected PC. This will provide you with Perfetto logs. You can use Perfetto UI [here](https://ui.perfetto.dev/) to convert these logs to `.systrace` format. Then, you should rename these to "perfetto.systrace" and place them in the `Logs` folder.

## How to investigate:
- To run this code, first install all requirements using `pip3 install -r requirements.txt` in the root directory and run `python -m spacy download en_core_web_sm` to install the spaCy model.
- Paste the HMD, Oculus, and Sysmon logs in Logs/hmd.txt, Logs/oculuslog.txt, and Logs/sysmon.txt, respectively. Then, run `python3 main.py`.
- This command takes two optional arguments, `-t` and `-p`, that filter the output to those subgraphs connected to nodes with a particular TID or PID, respectively. For example, to filter to all subgraphs connected to a node with a PID of "3000", run `python3 main.py -p 3000`.
- You can use both optional arguments simultaneously to filter on all nodes that have a particular PID _and_ a particular TID.

## Query Functions

- The auxiliary functions `find_ancestors`, `find_successors`, `backward_query`, and `forward_query` are defined in `graph_functions.py`:
    - `find_ancestors` and `find_successors` return a list of nodes representing the ancestors and successors, respectively, of a given node in a directed networkx graph.
    - `backward_query` and `forward_query` return the subgraphs associated with the ancestors and successors, respectively, of a given node in a directed networkx graph; that is, they return graphs with the same nodes as `find_ancestors` and `find_successors` but with edges between those nodes from the original graphs.
    - These functions all take a networkx graph, node timestamp, and node entity name as input. The latter two inputs specify the node whose ancestors or successors are queried.

## Log Analysis and Multi-Layer Provenance Graph (MPG) Generation

This section provides more detailed instructions for running the log analysis and MPG generation processes, along with some common issues and troubleshooting guidelines.

### 1. Preparing Logs

1. **Collect or Identify Your Logs**  
   - Make sure you have followed the log-collection procedures described above (see [How to collect logs](#how-to-collect-logs)).  
   - If you are using **newly collected logs**, ensure they are formatted as required. For example, if collecting logs from a Meta Quest 2 device, follow the steps to run `adb logcat` commands, export logs, and pull them from the device using the `adb pull` commands.
   - Our prototype for REALITYCHECK is tested on the Meta Quest 2 version 333700.3370.0, as mentioned in the paper. The parsing procedures and system logs may vary for other versions. Our system is also tested only on Windows as Oculus logs are only available on Windows (more details on this are provided in the paper and `Log Collection` folder).

2. **Place Logs in the Correct Location**  
   - By default, REALITYCHECK expects the following files under the `Logs` folder:
     - `hmd.txt` (HMD logs)
     - `oculuslog.txt` (Oculus logs)
     - `sysmon.txt` (Sysmon logs)
   - If you prefer different file names or directories, either rename them to match the defaults or pass them as command - line arguments (see **Step 2** below).

3. **Handle Transfer Errors (If Any)**  
   - If `adb pull` fails or times out when transferring logs from your device, ensure:
     - Your Meta Quest 2 is still properly connected (USB debugging enabled).
     - The file paths you specified on the device actually exist (e.g., `/sdcard/log_output.txt`).
     - You have enough space and permissions on your local machine to save the logs.

### 2. Running Log Analysis and MPG Generation

1. **Locate and Run the Main Script**  
   - In this repository, the main script for log analysis and multi - layer provenance graph generation may be `main.py` (found in the root directory).  
   - Make sure to install all dependencies (see [Dependencies](#dependencies)) and, if you have not already, run:
     ```bash
     pip3 install -r requirements.txt
     ```

2. **Execute the Script with Appropriate Arguments**  
   - If your logs are named exactly `hmd.txt`, `oculuslog.txt`, and `sysmon.txt` and are stored under the `Logs` folder, you can typically just run:
     ```bash
     python3 main.py
     ```
   - Adjust the arguments and file paths as necessary in the code.

3. **Monitor for Errors**  
   - If any errors occur (e.g., library version mismatches, incorrect log formats, missing files), consult the **Troubleshooting** section below for potential solutions.

### 3. Common Issues and Troubleshooting

- **Incompatible Library Versions**  
  Double-check your Python environment to confirm that installed versions match those in the [Dependencies](#dependencies) list. Mismatched versions of networkx or matplotlib, for example, can lead to unexpected errors.
- **Incorrect Log Formats**  
  If the script reports it cannot parse your logs, ensure each log file (e.g., `hmd.txt`) truly contains the expected log lines. Verify that the logs have not been truncated or corrupted (especially if the file size seems suspiciously small).
- **Path Errors**  
  Make sure the paths you pass to `main.py` exist on your local machine. Watch out for backslashes vs. forward slashes.

---

