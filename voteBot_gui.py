import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import sys
import threading
import queue

class VoteBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VoteBot Manager")
        # Dictionary to store {pid: {'process': Popen, 'frame': Frame, 'log_queue': Queue, 'log_window': Toplevel or None, 'log_text': ScrolledText or None, 'stop_event': threading.Event}}
        self.processes = {}

        # --- Input Section ---
        input_frame = ttk.Frame(root, padding="10")
        input_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(input_frame, text="Poll URL:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.poll_url_entry = ttk.Entry(input_frame, width=50)
        self.poll_url_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(input_frame, text="Answer ID:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.answer_id_entry = ttk.Entry(input_frame, width=50)
        self.answer_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(input_frame, text="Proxy URL (Optional):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.proxy_url_entry = ttk.Entry(input_frame, width=50)
        self.proxy_url_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        delay_frame = ttk.Frame(input_frame)
        delay_frame.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(input_frame, text="Delays (sec):").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(delay_frame, text="Min:").pack(side=tk.LEFT, padx=(0, 2))
        self.min_delay_entry = ttk.Entry(delay_frame, width=5)
        self.min_delay_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.min_delay_entry.insert(0, "5")
        ttk.Label(delay_frame, text="Max:").pack(side=tk.LEFT, padx=(0, 2))
        self.max_delay_entry = ttk.Entry(delay_frame, width=5)
        self.max_delay_entry.pack(side=tk.LEFT)
        self.max_delay_entry.insert(0, "20")

        input_frame.columnconfigure(1, weight=1) # Make entry fields expand

        launch_button = ttk.Button(input_frame, text="Launch Instance", command=self.launch_instance)
        launch_button.grid(row=4, column=0, columnspan=2, pady=10)

        # --- Instance Display Area ---
        self.instance_area = ttk.Frame(root, padding="10")
        self.instance_area.pack(pady=10, padx=10, fill='both', expand=True)
        ttk.Label(self.instance_area, text="Running Instances:").pack(anchor='w')

        # Ensure cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start periodic check for log messages
        self._update_log_displays()

    def launch_instance(self):
        poll_url = self.poll_url_entry.get().strip()
        answer_id = self.answer_id_entry.get().strip()
        proxy_url = self.proxy_url_entry.get().strip()
        min_delay = self.min_delay_entry.get().strip()
        max_delay = self.max_delay_entry.get().strip()

        if not poll_url or not answer_id:
            messagebox.showerror("Error", "Poll URL and Answer ID are required.")
            return

        # Validate delays
        try:
            min_d = int(min_delay) if min_delay else 5
            max_d = int(max_delay) if max_delay else 20
            if min_d < 0 or max_d < 0 or min_d > max_d:
                raise ValueError("Invalid delay values")
        except ValueError:
            messagebox.showerror("Error", "Invalid delay values. Ensure Min <= Max and both are non-negative numbers.")
            return

        # Prepare environment
        env = os.environ.copy()
        env['POLLURL'] = poll_url
        env['ANSWERID'] = answer_id
        if proxy_url:
            env['PROXY_URL'] = proxy_url
        env['MIN_DELAY'] = str(min_d)
        env['MAX_DELAY'] = str(max_d)

        # Prepare command and flags
        command = [sys.executable.replace('pythonw.exe', 'python.exe') if sys.platform == "win32" else 'node', 'voteBot.js'] # Adjust path if needed
        # command = ['node', 'voteBot.js'] # Use node directly
        creationflags = 0
        if sys.platform == "win32":
            # This flag prevents the black console window from appearing for each node process on Windows
            creationflags = subprocess.CREATE_NO_WINDOW
            command = ['node', 'voteBot.js'] # On windows, node should be in PATH

        try:
            process = subprocess.Popen(
                command,
                env=env,
                cwd='voteBot', # Run node script from its directory
                stdout=subprocess.PIPE, # Capture stdout
                stderr=subprocess.PIPE, # Capture stderr
                creationflags=creationflags, # Hide console window on Windows
                encoding='utf-8', # Decode stdout/stderr using utf-8
                text=True, # Decode stdout/stderr as text
                bufsize=1 # Line buffered
            )
            print(f"Launched process {process.pid} for {poll_url}") # Debug print

            # Create GUI representation for the instance
            frame_id = process.pid # Use PID as a unique ID
            instance_frame = ttk.Frame(self.instance_area, borderwidth=1, relief="groove", padding=5) # Changed relief for visibility
            instance_frame.pack(pady=5, fill='x')

            info_label = ttk.Label(instance_frame, text=f"PID: {process.pid} - URL: {poll_url[:40]}...")
            info_label.pack(side=tk.LEFT, expand=True, fill='x', padx=5)

            log_button = ttk.Button(instance_frame, text="Show Log", command=lambda pid=frame_id: self.show_log_window(pid))
            log_button.pack(side=tk.LEFT, padx=(0, 5))

            stop_button = ttk.Button(instance_frame, text="Stop", command=lambda pid=frame_id: self.stop_instance(pid))
            stop_button.pack(side=tk.RIGHT)

            # Setup log handling
            log_queue = queue.Queue()
            stop_event = threading.Event()
            log_thread = threading.Thread(target=self._read_output,
                                        args=(process.stdout, process.stderr, log_queue, stop_event),
                                        daemon=True) # Daemon thread exits when main app exits
            log_thread.start()

            self.processes[frame_id] = {
                'process': process,
                'frame': instance_frame,
                'log_queue': log_queue,
                'log_window': None,
                'log_text': None,
                'stop_event': stop_event
            }

        except FileNotFoundError:
             messagebox.showerror("Error", "Could not find 'node' executable or 'voteBot.js'. Ensure Node.js is installed and in PATH, and the script is in the 'voteBot' directory.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch process: {e}")
            print(f"Error launching process: {e}") # Debug print


    def _read_output(self, stdout_pipe, stderr_pipe, log_queue, stop_event):
        """Reads stdout and stderr of a process and puts lines into a queue."""
        try:
            # Read both streams concurrently using threads
            def reader_thread(pipe, pipe_name):
                try:
                    for line in iter(pipe.readline, ''):
                        if stop_event.is_set():
                            break
                        log_queue.put((pipe_name, line))
                    # Signal pipe closed (optional)
                    # log_queue.put((pipe_name, None))
                finally:
                    pipe.close()

            stdout_thread = threading.Thread(target=reader_thread, args=(stdout_pipe, 'stdout'), daemon=True)
            stderr_thread = threading.Thread(target=reader_thread, args=(stderr_pipe, 'stderr'), daemon=True)
            stdout_thread.start()
            stderr_thread.start()

            # Wait for threads to finish (which they will when pipes close or stop_event is set)
            stdout_thread.join()
            stderr_thread.join()

        except Exception as e:
            # This might happen if pipes are closed abruptly
            print(f"Error reading output: {e}")
        finally:
            # Ensure queue gets a final signal if needed, or rely on stop_event
            # log_queue.put(None) # Signal end of output
            pass # Stop event handles termination signal


    def stop_instance(self, pid):
        if pid not in self.processes:
            return

        data = self.processes[pid]
        process = data['process']
        frame = data['frame']
        stop_event = data['stop_event']
        log_window = data['log_window']

        print(f"Attempting to stop process {pid}")

        # Signal the reader thread to stop
        stop_event.set()

        # Terminate the process
        try:
            process.terminate() # Send SIGTERM (Unix) or TerminateProcess (Win)
            process.wait(timeout=2) # Wait a bit for it to close
            print(f"Process {pid} terminated.")
        except subprocess.TimeoutExpired:
            print(f"Process {pid} did not terminate gracefully, killing.")
            process.kill() # Send SIGKILL (Unix) or TerminateProcess (Win)
            try:
                process.wait(timeout=1) # Wait briefly after kill
            except:
                pass # Ignore errors after kill
        except Exception as e:
            pass

        # Clean up GUI elements
        if log_window:
            try:
                log_window.destroy()
            except tk.TclError:
                pass # Window might already be destroyed
        frame.destroy()

        # Remove from tracking
        del self.processes[pid]

    def show_log_window(self, pid):
        if pid not in self.processes:
            return

        data = self.processes[pid]

        if data['log_window'] and data['log_window'].winfo_exists():
            # Window already exists, bring it to front
            data['log_window'].lift()
            return

        # Create new log window
        log_window = tk.Toplevel(self.root)
        log_window.title(f"Log - PID: {pid}")
        log_window.geometry("600x400")

        log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, state='disabled')
        log_text.pack(expand=True, fill='both')

        # Configure tags for potential coloring
        log_text.tag_config('stdout', foreground='black')
        log_text.tag_config('stderr', foreground='red')

        data['log_window'] = log_window
        data['log_text'] = log_text

        # Make the window closing remove the reference
        log_window.protocol("WM_DELETE_WINDOW", lambda: self._on_log_window_close(pid))

    def _on_log_window_close(self, pid):
        if pid in self.processes:
            log_window = self.processes[pid]['log_window']
            self.processes[pid]['log_window'] = None
            self.processes[pid]['log_text'] = None
            if log_window:
                try:
                    log_window.destroy()
                except tk.TclError:
                    pass # Ignore if already destroyed
                    pass # Ignore if already destroyed

    def _update_log_displays(self):
        """Periodically check queues and update active log windows."""
        for pid, data in list(self.processes.items()): # Iterate over copy
            if data['log_window'] and data['log_text']:
                try:
                    # Process all messages currently in the queue
                    while True:
                        source, line = data['log_queue'].get_nowait()
                        if line is None: # End signal (optional)
                            continue
                        data['log_text'].configure(state='normal')
                        data['log_text'].insert(tk.END, line, (source,))
                        data['log_text'].configure(state='disabled')
                        data['log_text'].see(tk.END) # Autoscroll
                except queue.Empty:
                    pass # No new messages
                except tk.TclError:
                    # Log window might have been closed unexpectedly
                    self._on_log_window_close(pid)
                except Exception as e:
                    print(f"Error updating log display for PID {pid}: {e}")
                    self._on_log_window_close(pid) # Close window on error

        # Schedule the next check
        self.root.after(100, self._update_log_displays) # Check every 100ms

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to stop all running bots and quit?"):
            print("Closing application and stopping all processes...")
            for pid in list(self.processes.keys()): # Iterate over a copy of keys
                self.stop_instance(pid)
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VoteBotGUI(root)
    root.mainloop()
