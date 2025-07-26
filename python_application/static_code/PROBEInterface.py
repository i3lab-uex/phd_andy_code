import os
import time
import threading
from typing import Dict, Union
import gradio as gr
from python_application.generated_code.model.PROBE import PROBE
from python_application.static_code.utils.LogCapture import global_stream_capture


class PROBEInterface:
    """Enhanced PROBE interface with optimization capabilities and real-time logging."""

    def __init__(self, probe: PROBE):
        """
        Initialize the PROBE interface.

        Args:
            probe (PROBE): PROBE instance containing configuration and optimization tasks
        """
        self.probe = probe
        self.task_names = [ot.name for ot in probe.optimization_task]
        self.interface = self._build_interface()

        # Control variables for optimization execution
        self.optimization_running = False
        self.stop_optimization = False
        self.current_thread = None

    def run_prompt_task_optimization(
        self, task_name: str, prompts_path: str, population_size: int, seed: int
    ) -> str:
        """
        Run prompt-based optimization for all experiments in a task.

        Args:
            task_name (str): Name of the optimization task
            prompts_path (str): Path to JSON prompts directory
            population_size (int): Population size for genetic algorithm
            seed (int): Random seed for reproducibility

        Returns:
            str: Formatted results message
        """
        try:
            # Create stop callback function that the optimization process can check
            def should_stop():
                return self.stop_optimization

            result = self.probe.run_prompt_optimization_whole_task(
                task_name=task_name,
                prompts_path=prompts_path,
                population_size=population_size,
                seed=seed,
                stop_callback=should_stop,
            )

            if result["status"] == "success":
                results = result["results"]
                return f"""✅ Prompt-based Task Optimization Completed Successfully!
                
                📋 Task: {results["task_name"]}
                📊 Results Summary:
                • Total execution time: {results["total_time"]:.2f} seconds
                • Number of experiments: {results["num_experiments"]}
                • Total processed slices: {results["total_processed_slices"]}
                • Average Jaccard Index: {results["avg_jaccard"]:.4f}
                • Average Dice Coefficient: {results["avg_dice"]:.4f}
                • Average SAM Score: {results["avg_score"]:.4f}
                
                Check the output directory for detailed results and visualizations."""
            else:
                return f"❌ Error: {result['message']}"

        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"

    def run_prompt_experiment_optimization(
        self,
        task_name: str,
        experiment_name: str,
        prompts_path: str,
        population_size: int,
        seed: int,
    ) -> str:
        """
        Run prompt-based optimization for a specific experiment.

        Args:
            task_name (str): Name of the optimization task
            experiment_name (str): Name of the specific experiment
            prompts_path (str): Path to JSON prompts directory
            population_size (int): Population size for genetic algorithm
            seed (int): Random seed for reproducibility

        Returns:
            str: Formatted results message
        """
        try:
            # Create stop callback function that the optimization process can check
            def should_stop():
                return self.stop_optimization

            result = self.probe.run_prompt_optimization_using_task_experiment(
                task_name=task_name,
                experiment_name=experiment_name,
                prompts_path=prompts_path,
                population_size=population_size,
                seed=seed,
                stop_callback=should_stop,
            )

            if result["status"] == "success":
                results = result["results"]
                return f"""✅ Prompt-based Experiment Optimization Completed Successfully!
                
                📋 Experiment: {results["experiment_name"]}
                📊 Results Summary:
                • Total execution time: {results["total_time"]:.2f} seconds
                • Processed slices: {results["processed_slices"]}
                • Average Jaccard Index: {results["avg_jaccard"]:.4f}
                • Average Dice Coefficient: {results["avg_dice"]:.4f}
                • Average SAM Score: {results["avg_score"]:.4f}
                
                Check the output directory for detailed results and visualizations."""
            else:
                return f"❌ Error: {result['message']}"

        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"

    def stop_current_optimization(self):
        """
        Stop the currently running optimization.

        Returns:
            tuple: Updated button states and status message
        """
        if self.optimization_running:
            self.stop_optimization = True
            return (
                gr.Button("🚀 Run Whole Task", variant="primary", interactive=True),
                gr.Button(
                    "⚡ Run Single Experiment", variant="secondary", interactive=True
                ),
                gr.Button("⏹️ Stop Optimization", variant="stop", interactive=False),
                "🛑 Optimization stopped by user request. The system is ready for new operations.",
            )
        else:
            return (
                gr.Button("🚀 Run Whole Task", variant="primary", interactive=True),
                gr.Button(
                    "⚡ Run Single Experiment", variant="secondary", interactive=True
                ),
                gr.Button("⏹️ Stop Optimization", variant="stop", interactive=False),
                "ℹ️ No optimization is currently running.",
            )

    def run_unified_task_optimization_with_progress(
        self,
        task_name: str,
        prompts_path: str,
        population_size: int,
        seed: int,
    ):
        """
        Run prompt-based optimization with real-time progress updates and stop control.

        This is a generator function that yields progress updates.
        """
        # Set an optimization state
        self.optimization_running = True
        self.stop_optimization = False

        # Clear previous logs
        global_stream_capture.clear_output()

        # Initial status
        yield "🚀 Starting prompt-based optimization...\n"

        # Run optimization in a separate thread and stream logs
        result_container: Dict[str, Union[str, None, bool]] = {
            "result": None,
            "error": None,
            "stopped": False,
        }

        def run_optimization():
            try:
                # Check for stop signal periodically during optimization
                if self.stop_optimization:
                    result_container["stopped"] = True
                    return

                if not prompts_path or prompts_path.strip() == "":
                    result_container["error"] = (
                        "❌ Error: Please specify the prompts directory path."
                    )
                    return
                result_container["result"] = self.run_prompt_task_optimization(
                    task_name, prompts_path, population_size, seed
                )
            except Exception as e:
                if self.stop_optimization:
                    result_container["stopped"] = True
                else:
                    result_container["error"] = f"❌ Unexpected error: {str(e)}"

        # Start optimization in the background
        opt_thread = threading.Thread(target=run_optimization)
        self.current_thread = opt_thread
        opt_thread.start()

        # Stream logs while optimization is running
        last_output = ""
        while opt_thread.is_alive():
            if self.stop_optimization:
                # Give the thread a moment to finish gracefully
                opt_thread.join(timeout=2.0)
                break

            current_output = global_stream_capture.get_full_output()
            if current_output != last_output:
                # Append new content
                yield current_output
                last_output = current_output
            time.sleep(0.5)  # Update every 500 ms

        # Wait for the thread to complete
        if opt_thread.is_alive():
            opt_thread.join(timeout=1.0)

        # Reset optimization state
        self.optimization_running = False
        self.current_thread = None

        # Final output
        if result_container["stopped"] or self.stop_optimization:
            final_output = global_stream_capture.get_full_output()
            yield (
                final_output
                + "\n\n🛑 **Optimization stopped by user request.**\nSystem is ready for new operations."
            )
        elif result_container["error"]:
            yield result_container["error"]
        elif result_container["result"]:
            final_output = global_stream_capture.get_full_output()
            if final_output:
                yield final_output + "\n\n" + result_container["result"]
            else:
                yield result_container["result"]
        else:
            yield "❌ No result received from optimization"

    def run_unified_experiment_optimization_with_progress(
        self,
        task_name: str,
        experiment_name: str,
        prompts_path: str,
        population_size: int,
        seed: int,
    ):
        """
        Run unified experiment optimization with real-time progress updates and stop control.

        This is a generator function that yields progress updates.
        """
        # Set optimization state
        self.optimization_running = True
        self.stop_optimization = False

        # Clear previous logs
        global_stream_capture.clear_output()

        # Initial status
        yield "⚡ Starting experiment optimization...\n"

        # Run optimization in a separate thread and stream logs
        result_container: Dict[str, Union[str, None, bool]] = {
            "result": None,
            "error": None,
            "stopped": False,
        }

        def run_optimization():
            try:
                # Check for stop signal
                if self.stop_optimization:
                    result_container["stopped"] = True
                    return

                if not prompts_path or prompts_path.strip() == "":
                    result_container["error"] = (
                        "❌ Error: Please specify the prompts directory path when using custom initial prompts."
                    )
                    return
                result_container["result"] = self.run_prompt_experiment_optimization(
                    task_name,
                    experiment_name,
                    prompts_path,
                    population_size,
                    seed,
                )
            except Exception as e:
                if self.stop_optimization:
                    result_container["stopped"] = True
                else:
                    result_container["error"] = f"❌ Unexpected error: {str(e)}"

        # Start optimization in background
        opt_thread = threading.Thread(target=run_optimization)
        self.current_thread = opt_thread
        opt_thread.start()

        # Stream logs while optimization is running
        last_output = ""
        while opt_thread.is_alive():
            if self.stop_optimization:
                # Give the thread a moment to finish gracefully
                opt_thread.join(timeout=2.0)
                break

            current_output = global_stream_capture.get_full_output()
            if current_output != last_output:
                # Append new content
                yield current_output
                last_output = current_output
            time.sleep(0.5)  # Update every 500 ms

        # Wait for thread to complete
        if opt_thread.is_alive():
            opt_thread.join(timeout=1.0)

        # Reset optimization state
        self.optimization_running = False
        self.current_thread = None

        # Final output
        if result_container["stopped"] or self.stop_optimization:
            final_output = global_stream_capture.get_full_output()
            yield (
                final_output
                + "\n\n🛑 **Optimization stopped by user request.**\nSystem is ready for new operations."
            )
        elif result_container["error"]:
            yield result_container["error"]
        elif result_container["result"]:
            final_output = global_stream_capture.get_full_output()
            if final_output:
                yield final_output + "\n\n" + result_container["result"]
            else:
                yield result_container["result"]
        else:
            yield "❌ No result received from optimization"

    def update_experiment_choices(self, task_name: str):
        """
        Update experiment choices based on a selected task.

        Args:
            task_name (str): Name of the selected task

        Returns:
            gr.Dropdown: Updated dropdown with experiment choices
        """
        if not task_name:
            return gr.Dropdown(choices=[], value="")
        selected_task = next(
            (task for task in self.probe.optimization_task if task.name == task_name),
            None,
        )
        if selected_task:
            experiment_names = [exp.name for exp in selected_task.experiment]
            return gr.Dropdown(
                choices=experiment_names,
                value=experiment_names[0] if experiment_names else None,
            )
        return gr.Dropdown(choices=[], value="")

    def _build_interface(self):
        """
        Build the Gradio interface with optimization capabilities.

        Returns:
            gr.Interface: Configured Gradio interface
        """
        with gr.Blocks(
            title="PROBE - SAM Optimization Interface",
            theme=gr.themes.Base(),
            css="""
            .output-textbox textarea {
                height: 500px !important;
                overflow-y: auto !important;
                scroll-behavior: smooth !important;
                white-space: pre-wrap !important;
                word-wrap: break-word !important;
                resize: none !important;
            }
            .output-textbox .scroll-hide {
                scrollbar-width: thin !important;
            }
            .output-textbox .wrap {
                height: 500px !important;
                overflow-y: auto !important;
            }
            """,
        ) as interface:
            # Header
            gr.Markdown("# 🔬 PROBE - SAM Optimization Interface")
            gr.Markdown(
                "Advanced interface for SAM optimization experiments using genetic algorithms and dynamic PROBE "
                "configuration"
            )

            with gr.Tabs():
                # Original PROBE Tab
                with gr.TabItem("📋 Configuration"):
                    with gr.Row():
                        with gr.Column():
                            display_button = gr.Button(
                                "🔍 Display PROBE Configuration", variant="primary"
                            )
                            save_button = gr.Button("💾 Save Logs to File")

                    probe_output = gr.Textbox(
                        label="PROBE Configuration",
                        lines=15,
                        max_lines=20,
                        interactive=False,
                        autoscroll=False,
                        show_copy_button=True,
                        elem_classes=["output-textbox"],
                        scale=1,
                    )

                    status_output = gr.Textbox(
                        label="Status", lines=2, interactive=False
                    )

                    display_button.click(self.probe.display_probe, outputs=probe_output)
                    save_button.click(
                        self.probe.save_logs_to_file, outputs=status_output
                    )

                # PROBE-based Optimization Tab
                with gr.TabItem("🚀 Optimization"):
                    gr.Markdown(
                        "### Run SAM prompt optimization algorithm using PROBE configuration"
                    )

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### 🎛️ Global Parameters")
                            probe_pop_size = gr.Slider(
                                minimum=10,
                                maximum=500,
                                value=100,
                                step=10,
                                label="Population Size",
                                info="Number of individuals in the genetic algorithm population",
                            )
                            probe_seed = gr.Number(
                                value=1,
                                minimum=1,
                                maximum=9999,
                                label="Random Seed",
                                info="Seed for reproducible results",
                            )

                        with gr.Column():
                            gr.Markdown("#### 📋 Task/Experiment Selection")
                            probe_task_dropdown = gr.Dropdown(
                                choices=self.task_names,
                                label="Select Optimization Task",
                                value=self.task_names[0] if self.task_names else None,
                                interactive=True,
                            )
                            default_experiments = (
                                [
                                    exp.name
                                    for exp in self.probe.optimization_task[
                                        0
                                    ].experiment
                                ]
                                if self.probe.optimization_task
                                else []
                            )
                            probe_experiment_dropdown = gr.Dropdown(
                                choices=default_experiments,
                                value=(
                                    default_experiments[0]
                                    if default_experiments
                                    else None
                                ),
                                label="Select Experiment (for single experiment runs)",
                                interactive=True,
                            )

                    # Prompts Configuration Section
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### 🎯 Initial Prompts Configuration")
                            probe_prompts_path = gr.Textbox(
                                label="Prompts Directory Path",
                                value=os.path.join(
                                    os.getcwd(),
                                    "initial_prompts_configuration/covid",
                                ),
                                info="Directory containing JSON prompt files",
                                interactive=True,
                            )

                    # Control Buttons Section
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### 🚀 Optimization Execution")
                            with gr.Row():
                                probe_run_task_btn = gr.Button(
                                    "🚀 Run Whole Task", variant="primary"
                                )
                                probe_run_exp_btn = gr.Button(
                                    "⚡ Run Single Experiment", variant="secondary"
                                )
                                probe_stop_btn = gr.Button(
                                    "⏹️ Stop Optimization",
                                    variant="stop",
                                    interactive=False,
                                )

                    # Output Section with enhanced scroll
                    with gr.Row():
                        with gr.Column():
                            probe_output = gr.Textbox(
                                label="Optimization Results & Logs",
                                lines=25,
                                interactive=False,
                                autoscroll=True,
                                show_copy_button=True,
                                elem_classes=["output-textbox"],
                                scale=1,
                            )

                    # Hidden state components for managing button states
                    optimization_state = gr.State(
                        False
                    )  # Track if optimization is running

                    # Function to update button states when optimization starts
                    def start_optimization_ui():
                        return (
                            gr.Button(
                                "🚀 Run Whole Task",
                                variant="primary",
                                interactive=False,
                            ),
                            gr.Button(
                                "⚡ Run Single Experiment",
                                variant="secondary",
                                interactive=False,
                            ),
                            gr.Button(
                                "⏹️ Stop Optimization", variant="stop", interactive=True
                            ),
                            True,  # optimization_state
                        )

                    # Function to reset button states when optimization ends
                    def end_optimization_ui():
                        return (
                            gr.Button(
                                "🚀 Run Whole Task", variant="primary", interactive=True
                            ),
                            gr.Button(
                                "⚡ Run Single Experiment",
                                variant="secondary",
                                interactive=True,
                            ),
                            gr.Button(
                                "⏹️ Stop Optimization", variant="stop", interactive=False
                            ),
                            False,  # optimization_state
                        )

                    # Enhanced optimization functions that handle UI state
                    def run_task_with_ui_control(*args):
                        # Update UI to show optimization is running
                        self.optimization_running = True
                        self.stop_optimization = False

                        # Run the optimization with progress updates
                        for update in self.run_unified_task_optimization_with_progress(
                            *args
                        ):
                            yield update

                        # Reset state when done
                        self.optimization_running = False

                    def run_experiment_with_ui_control(*args):
                        # Update UI to show optimization is running
                        self.optimization_running = True
                        self.stop_optimization = False

                        # Run the optimization with progress updates
                        for (
                            update
                        ) in self.run_unified_experiment_optimization_with_progress(
                            *args
                        ):
                            yield update

                        # Reset state when done
                        self.optimization_running = False

                    # Event handlers
                    probe_task_dropdown.change(
                        self.update_experiment_choices,
                        inputs=probe_task_dropdown,
                        outputs=probe_experiment_dropdown,
                    )

                    # Task optimization with UI state management
                    task_click_event = probe_run_task_btn.click(
                        start_optimization_ui,
                        outputs=[
                            probe_run_task_btn,
                            probe_run_exp_btn,
                            probe_stop_btn,
                            optimization_state,
                        ],
                    )
                    task_click_event.then(
                        run_task_with_ui_control,
                        inputs=[
                            probe_task_dropdown,
                            probe_prompts_path,
                            probe_pop_size,
                            probe_seed,
                        ],
                        outputs=probe_output,
                        show_progress="minimal",
                    ).then(
                        end_optimization_ui,
                        outputs=[
                            probe_run_task_btn,
                            probe_run_exp_btn,
                            probe_stop_btn,
                            optimization_state,
                        ],
                    )

                    # Experiment optimization with UI state management
                    exp_click_event = probe_run_exp_btn.click(
                        start_optimization_ui,
                        outputs=[
                            probe_run_task_btn,
                            probe_run_exp_btn,
                            probe_stop_btn,
                            optimization_state,
                        ],
                    )
                    exp_click_event.then(
                        run_experiment_with_ui_control,
                        inputs=[
                            probe_task_dropdown,
                            probe_experiment_dropdown,
                            probe_prompts_path,
                            probe_pop_size,
                            probe_seed,
                        ],
                        outputs=probe_output,
                        show_progress="minimal",
                    ).then(
                        end_optimization_ui,
                        outputs=[
                            probe_run_task_btn,
                            probe_run_exp_btn,
                            probe_stop_btn,
                            optimization_state,
                        ],
                    )

                    # Stop button functionality
                    probe_stop_btn.click(
                        self.stop_current_optimization,
                        outputs=[
                            probe_run_task_btn,
                            probe_run_exp_btn,
                            probe_stop_btn,
                            status_output,
                        ],
                    )

        return interface

    def launch(self):
        """
        Launch the Gradio interface.
        """
        return self.interface.launch()
