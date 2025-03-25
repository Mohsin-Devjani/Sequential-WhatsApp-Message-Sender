from flask import Flask, Response, request, render_template
import pandas as pd
import queue
import threading
import time
import requests
import random

app = Flask(__name__)

# A thread-safe queue for log messages (for SSE)
log_queue = queue.Queue()

# A global event for stopping the background process
stop_event = threading.Event()

def send_msgs(row, message, image_url, api_key, log_queue, min_sleep, max_sleep):
    """
    Sends a WhatsApp message using textmebot.com API.
    Logs messages to log_queue.
    """
    recipient = row['whatsapp']
    if image_url.strip():
        url = f"https://api.textmebot.com/send.php?recipient={recipient}&apikey={api_key}&text={message}&file={image_url}"
    else:
        url = f"https://api.textmebot.com/send.php?recipient={recipient}&apikey={api_key}&text={message}"

    response = requests.get(url)
    if response.status_code == 200:
        log_queue.put(f"Successfully sent message to {recipient}")
        success_value = 1
    else:
        log_queue.put(f"Error {response.status_code} while sending message to {recipient}")
        success_value = 0

    # Sleep in [min_sleep, max_sleep], checking stop_event
    sleep_time = random.uniform(min_sleep, max_sleep)
    for _ in range(int(sleep_time)):
        if stop_event.is_set():
            # Abort during sleep if event is set
            log_queue.put("Aborting process during sleep...")
            return success_value
        time.sleep(1)
    
    # If there's leftover fractional part of sleep_time, handle it
    fractional_part = sleep_time - int(sleep_time)
    if fractional_part > 0 and not stop_event.is_set():
        time.sleep(fractional_part)

    return success_value

def background_process(df, message, image_url, api_key, log_queue, min_sleep, max_sleep):
    """
    Loops through rows where success == 0 and sends messages.
    The DataFrame's "success" column is updated based on the API call.
    Logs progress to log_queue.
    Stops early if stop_event is set.
    """
    try:
        log_queue.put("Starting the message-sending process...")
        for index, row in df[df["success"] == 0].iterrows():
            if stop_event.is_set():
                log_queue.put("Aborting process before sending next message...")
                break

            # Check API status before sending each message
            check_url = f"https://api.textmebot.com/connect.php?apikey={api_key}&json=yes"
            check_response = requests.get(check_url)
            if check_response.status_code == 200:
                check_data = check_response.json()
                if check_data.get("status") == "banned":
                    log_queue.put("WhatsApp Account got banned! Exiting script now.")
                    stop_event.set()
                    break
            else:
                log_queue.put(f"Error checking API status: {check_response.status_code}")

            result = send_msgs(row, message, image_url, api_key, log_queue, min_sleep, max_sleep)
            df.at[index, "success"] = result

        if stop_event.is_set():
            log_queue.put("Process was aborted!")
        else:
            log_queue.put("All messages processed.")
    except Exception as e:
        log_queue.put(f"Error during processing: {e}")
    finally:
        log_queue.put("__PROCESS_COMPLETE__")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    """
    Starts a background thread to process the DataFrame.
    Reads the CSV, ensures a 'success' column exists, and loops
    through rows where success == 0 to send messages.
    """
    # Clear any previous stop event before starting a new process
    stop_event.clear()

    message = request.form.get('message', '')
    image_url = request.form.get('image_url', '')

    # Must provide an API key
    api_key = request.form.get('api_key', '').strip()
    if not api_key:
        log_queue.put("No API key provided. Please enter a valid key.")
        log_queue.put("__PROCESS_COMPLETE__")
        return "No API key provided", 400

    try:
        min_sleep = float(request.form.get('min_sleep', '10'))
        max_sleep = float(request.form.get('max_sleep', '16'))
    except ValueError:
        min_sleep, max_sleep = 10.0, 16.0
    if min_sleep > max_sleep:
        min_sleep, max_sleep = max_sleep, min_sleep

    csv_file = request.files.get('csv')
    if not csv_file:
        log_queue.put("No CSV file provided.")
        log_queue.put("__PROCESS_COMPLETE__")
        return "No CSV file", 400

    try:
        df = pd.read_csv(csv_file)
        if 'Number' in df.columns:
            df['Number'] = '+' + df['Number'].astype(str)
            df.rename(columns={'Number': 'whatsapp'}, inplace=True)
        if 'whatsapp' not in df.columns:
            log_queue.put("Error: CSV must have a 'whatsapp' column.")
            log_queue.put("__PROCESS_COMPLETE__")
            return "Invalid CSV", 400

        if 'success' not in df.columns:
            df['success'] = 0
    except Exception as e:
        log_queue.put(f"Error reading CSV file: {e}")
        log_queue.put("__PROCESS_COMPLETE__")
        return "Error reading CSV file", 400

    # Start background processing in a new thread
    thread = threading.Thread(
        target=background_process,
        args=(df, message, image_url, api_key, log_queue, min_sleep, max_sleep)
    )
    thread.start()

    return "Process started"

@app.route('/abort', methods=['POST'])
def abort():
    """
    Sets the stop_event so the background thread will stop gracefully.
    """
    stop_event.set()
    return "Abort signal sent"

@app.route('/stream')
def stream():
    """
    SSE endpoint that streams log messages from log_queue in real time.
    """
    def event_stream():
        while True:
            message = log_queue.get()
            yield f"data: {message}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True)
