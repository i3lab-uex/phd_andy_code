"""
Log capture utilities for real-time progress monitoring.
This module provides classes to capture console output and stream it to Gradio interface.
"""

import sys
import threading
import time
import queue
from io import StringIO
from typing import Callable, Optional, List
from contextlib import contextmanager


class StreamCapture:
    """Captures stdout and stderr and allows streaming to Gradio interface."""

    def __init__(self):
        """Initialize the stream capture system."""
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.captured_output = []
        self.output_queue = queue.Queue()
        self.is_capturing = False
        self.lock = threading.Lock()
        self.update_callback: Optional[Callable[[str], None]] = None

    def write(self, text):
        """
        Write text to both original output and capture buffer.

        Args:
            text: Text to write
        """
        # Write to original output first
        self.original_stdout.write(text)
        self.original_stdout.flush()

        # Add to captured output
        if text.strip():  # Only add non-empty lines
            with self.lock:
                self.captured_output.append(text.rstrip())
                # Limit buffer size to prevent memory issues
                if len(self.captured_output) > 1000:
                    self.captured_output = self.captured_output[-1000:]

                # Add to queue for real-time streaming
                self.output_queue.put(text.rstrip())

                # Call the update callback if set
                if self.update_callback:
                    self.update_callback(text.rstrip())

    def flush(self):
        """Flush the output."""
        self.original_stdout.flush()

    def get_full_output(self) -> str:
        """
        Get all captured output as a single string.

        Returns:
            str: All captured output
        """
        with self.lock:
            return "\n".join(self.captured_output)

    def get_new_output(self) -> List[str]:
        """
        Get new output since last call.

        Returns:
            List[str]: New output lines
        """
        new_lines = []
        try:
            while True:
                line = self.output_queue.get_nowait()
                new_lines.append(line)
        except queue.Empty:
            pass
        return new_lines

    def clear_output(self):
        """Clear the captured output buffer."""
        with self.lock:
            self.captured_output.clear()
            # Clear the queue
            try:
                while True:
                    self.output_queue.get_nowait()
            except queue.Empty:
                pass

    @contextmanager
    def capture(self):
        """
        Context manager for capturing output.

        Usage:
            with stream_capture.capture():
                # Code that produces output
                print("This will be captured")
        """
        if self.is_capturing:
            yield self
            return

        self.is_capturing = True
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        try:
            sys.stdout = self
            sys.stderr = self
            yield self
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.is_capturing = False

    def set_update_callback(self, callback: Callable[[str], None]):
        """
        Set callback function to update Gradio interface.

        Args:
            callback: Function to call when new output is available
        """
        self.update_callback = callback


class ProgressTracker:
    """Tracks optimization progress and provides structured updates."""

    def __init__(self, stream_capture: Optional[StreamCapture] = None):
        """
        Initialize progress tracker.

        Args:
            stream_capture: StreamCapture instance to use
        """
        self.stream_capture = stream_capture
        self.current_stage = "Initializing"
        self.current_file = ""
        self.current_slice = ""
        self.generation = 0
        self.total_generations = 0
        self.start_time = time.time()

    def update_stage(self, stage: str):
        """
        Update current processing stage.

        Args:
            stage: Description of current stage
        """
        self.current_stage = stage
        message = f"🔄 Stage: {stage}"
        print(message)

    def update_file(self, filename: str):
        """
        Update current file being processed.

        Args:
            filename: Name of current file
        """
        self.current_file = filename
        message = f"📁 Processing file: {filename}"
        print(message)

    def update_slice(self, slice_name: str):
        """
        Update current slice being processed.

        Args:
            slice_name: Name of current slice
        """
        self.current_slice = slice_name
        message = f"🖼️ Processing slice: {slice_name}"
        print(message)

    def update_generation(self, generation: int, total: int = 0):
        """
        Update optimization generation progress.

        Args:
            generation: Current generation
            total: Total generations (if known)
        """
        self.generation = generation
        if total > 0:
            self.total_generations = total
            message = f"🧬 Generation: {generation}/{total}"
        else:
            message = f"🧬 Generation: {generation}"
        print(message)

    def log_result(self, slice_name: str, metrics: dict):
        """
        Log results for a completed slice.

        Args:
            slice_name: Name of the slice
            metrics: Dictionary with metrics (dice, jaccard, score, time)
        """
        elapsed = time.time() - self.start_time
        message = f"""✅ Completed: {slice_name}
   📊 Dice: {metrics.get('dice', 0):.4f}
   📊 Jaccard: {metrics.get('jaccard', 0):.4f} 
   📊 Score: {metrics.get('score', 0):.4f}
   ⏱️ Time: {metrics.get('time', 0):.2f}s (Total: {elapsed:.1f}s)"""
        print(message)

    def log_error(self, error_msg: str):
        """
        Log an error message.

        Args:
            error_msg: Error message to log
        """
        message = f"❌ Error: {error_msg}"
        print(message)

    def log_final_summary(self, results: dict):
        """
        Log final summary of optimization.

        Args:
            results: Dictionary with final results
        """
        total_time = time.time() - self.start_time
        message = f"""
🎉 OPTIMIZATION COMPLETED!
📋 Task/Experiment: {results.get('name', 'Unknown')}
📊 Summary:
   • Processed slices: {results.get('processed_slices', 0)}
   • Average Dice: {results.get('avg_dice', 0):.4f}
   • Average Jaccard: {results.get('avg_jaccard', 0):.4f}
   • Average Score: {results.get('avg_score', 0):.4f}
   • Total time: {total_time:.2f}s
"""
        print(message)


# Global instance for easy access
global_stream_capture = StreamCapture()
