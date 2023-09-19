# Simple LSL UI for Sending and Logging Timestamps

## Description

This is a simple Lab Streaming Layer (LSL) User Interface that sends and logs timestamps. The UI allows the user to send triggers and custom messages while automatically sending a "heartbeat" timestamp every 5 seconds for post-synchronization. The UI also offers a log window that displays the past messages sent. The log is saved locally when the window is closed.

## Features

- Send triggers and custom messages
- Automatic "heartbeat" timestamps
- Log window to display past messages
- Local log file saved in CSV format
- Audio feedback with beeps
- Threading for asynchronous operations

## Requirements

- Python 3.8.10 or higher

## Installation

1. Clone this repository.
2. Navigate to the project directory.
3. Install the required packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the main script to start the UI:

```bash
python main.py
