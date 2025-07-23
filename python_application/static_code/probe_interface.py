import gradio as gr
import threading
import time
from python_application.generated_code.model.PROBE import PROBE
from python_application.static_code.utils.log_capture import global_stream_capture


class ProbeInterface:
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

        # Setup log capture callback for real-time updates
        self.current_output_textbox = None
        global_stream_capture.set_update_callback(self._update_output_callback)

    def _update_output_callback(self, output_text: str):
        """
        Callback function to update Gradio interface with new log output.

        Args:
            output_text (str): New output text to display
        """
        # This will be used to update the textbox in real-time
        # Gradio will handle the update through the streaming mechanism
        pass

    def display_probe(self) -> str:
        """
        Display the complete PROBE configuration.

        Returns:
            str: Formatted string with PROBE information
        """
        output = [f"Device: {self.probe.device}"]

        for ds in self.probe.dataset:
            output.append(f"\n📂 Dataset: {ds.name} - {ds.description} ({ds.type})")
            for ss in ds.subset:
                output.append(f"  📁 Subset: {ss.name}, Path: {ss.path}")
                output.append(
                    f"    Data folder: {ss.dataFolderName}, Labels folder: {ss.labelsFolderName}"
                )
                for sp in ss.sample:
                    output.append(
                        f"      🖼️ Sample: {sp.filename} (Format: {sp.extension})"
                    )

        for i, ot in enumerate(self.probe.optimization_task):
            output.append(
                f"\n🚀 Optimization Task {i + 1}: {ot.name} - {ot.description}"
            )
            output.append(f"  Algorithm: {ot.algorithm}")
            output.append(
                f"  Foundation Model: {ot.foundation_model.name} ({ot.foundation_model.type}) "
                f"v{ot.foundation_model.version}"
            )
            output.append(f"    Checkpoint: {ot.foundation_model.checkpointFilepath}")
            output.append(f"    Configuration: {ot.foundation_model.configuration}")
            output.append(
                f"  Optimization Metric: {ot.optimization_metric.name} ({ot.optimization_metric.type})"
            )
            output.append("  Performance Metrics:")
            for m in ot.performance_metric:
                output.append(f"    - {m.name}: {m.type}")
            output.append("  Experiments:")
            for e in ot.experiment:
                output.append(f"    ▶ Experiment: {e.name}")
                output.append(
                    f"    Initial State: {e.initial_state.description} (Improved: {e.initial_state.hasImproved})"
                )
                output.append(
                    f"      Prompt Type: {type(e.initial_state.prompt).__name__}"
                )
                if (
                    hasattr(e.initial_state.prompt, "bounding_box")
                    and e.initial_state.prompt.bounding_box
                ):
                    output.append("        Bounding Boxes:")
                    for box in e.initial_state.prompt.bounding_box:
                        output.append(
                            f"          - Min: ({box.min_coordinates.x}, {box.min_coordinates.y}), "
                            f"Max: ({box.max_coordinates.x}, {box.max_coordinates.y})"
                        )
                if (
                    hasattr(e.initial_state.prompt, "point")
                    and e.initial_state.prompt.point
                ):
                    output.append("        Points:")
                    for point in e.initial_state.prompt.point:
                        output.append(
                            f"          - Coordinates: ({point.coordinates.x}, {point.coordinates.y}), "
                            f"Type: {point.type}"
                        )
                output.append("      Stop Conditions:")
                for sc in e.stop_condition:
                    output.append(f"        - {type(sc).__name__}")
                output.append(
                    f"      Sample: {e.sample.filename} ({e.sample.extension})"
                )

        return "\n".join(output)

    def save_logs_to_file(self) -> str:
        """
        Save PROBE logs to a file.

        Returns:
            str: Confirmation message
        """
        content = self.display_probe()
        filepath = "probe_log.txt"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Logs correctly saved to {filepath}"

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

    def toggle_prompts_visibility(self, use_prompts: bool):
        """
        Toggle visibility of prompts directory field based on checkbox state.

        Args:
            use_prompts (bool): Whether to use custom prompts

        Returns:
            gr.Textbox: Updated textbox with visibility state
        """
        return gr.Textbox(
            label="Prompts Directory Path",
            info="Directory containing JSON prompt files",
            visible=use_prompts,
            interactive=True,
            value="/home/carlosbc24/PycharmProjects/phd2_code/python_application/static_code/initial_prompts_configuration/covid",
        )

    def run_task_optimization(
        self, task_name: str, population_size: int, seed: int
    ) -> str:
        """
        Run optimization for all experiments in a task using PROBE configuration.

        Args:
            task_name (str): Name of the optimization task
            population_size (int): Population size for genetic algorithm
            seed (int): Random seed for reproducibility

        Returns:
            str: Formatted results message
        """
        try:
            result = self.probe.run_optimization_whole_task(
                task_name=task_name, population_size=population_size, seed=seed
            )

            if result["status"] == "success":
                results = result["results"]
                return f"""✅ Task Optimization Completed Successfully!

📋 Task: {results['task_name']}
📊 Results Summary:
• Total execution time: {results['total_time']:.2f} seconds
• Number of experiments: {results['num_experiments']}
• Total processed slices: {results['total_processed_slices']}
• Average Jaccard Index: {results['avg_jaccard']:.4f}
• Average Dice Coefficient: {results['avg_dice']:.4f}
• Average SAM Score: {results['avg_score']:.4f}

Check the output directory for detailed results and visualizations."""
            else:
                return f"❌ Error: {result['message']}"

        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"

    def run_experiment_optimization(
        self, task_name: str, experiment_name: str, population_size: int, seed: int
    ) -> str:
        """
        Run optimization for a specific experiment using PROBE configuration.

        Args:
            task_name (str): Name of the optimization task
            experiment_name (str): Name of the specific experiment
            population_size (int): Population size for genetic algorithm
            seed (int): Random seed for reproducibility

        Returns:
            str: Formatted results message
        """
        try:
            result = self.probe.run_optimization_using_task_experiment(
                task_name=task_name,
                experiment_name=experiment_name,
                population_size=population_size,
                seed=seed,
            )

            if result["status"] == "success":
                results = result["results"]
                return f"""✅ Experiment Optimization Completed Successfully!

📋 Experiment: {results['experiment_name']}
📊 Results Summary:
• Total execution time: {results['total_time']:.2f} seconds
• Processed slices: {results['processed_slices']}
• Average Jaccard Index: {results['avg_jaccard']:.4f}
• Average Dice Coefficient: {results['avg_dice']:.4f}
• Average SAM Score: {results['avg_score']:.4f}

Check the output directory for detailed results and visualizations."""
            else:
                return f"❌ Error: {result['message']}"

        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"

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
            result = self.probe.run_prompt_optimization_whole_task(
                task_name=task_name,
                prompts_path=prompts_path,
                population_size=population_size,
                seed=seed,
            )

            if result["status"] == "success":
                results = result["results"]
                return f"""✅ Prompt-based Task Optimization Completed Successfully!

📋 Task: {results['task_name']}
📊 Results Summary:
• Total execution time: {results['total_time']:.2f} seconds
• Number of experiments: {results['num_experiments']}
• Total processed slices: {results['total_processed_slices']}
• Average Jaccard Index: {results['avg_jaccard']:.4f}
• Average Dice Coefficient: {results['avg_dice']:.4f}
• Average SAM Score: {results['avg_score']:.4f}

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
            result = self.probe.run_prompt_optimization_using_task_experiment(
                task_name=task_name,
                experiment_name=experiment_name,
                prompts_path=prompts_path,
                population_size=population_size,
                seed=seed,
            )

            if result["status"] == "success":
                results = result["results"]
                return f"""✅ Prompt-based Experiment Optimization Completed Successfully!

📋 Experiment: {results['experiment_name']}
📊 Results Summary:
• Total execution time: {results['total_time']:.2f} seconds
• Processed slices: {results['processed_slices']}
• Average Jaccard Index: {results['avg_jaccard']:.4f}
• Average Dice Coefficient: {results['avg_dice']:.4f}
• Average SAM Score: {results['avg_score']:.4f}

Check the output directory for detailed results and visualizations."""
            else:
                return f"❌ Error: {result['message']}"

        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"

    def run_unified_task_optimization(
        self,
        task_name: str,
        use_prompts: bool,
        prompts_path: str,
        population_size: int,
        seed: int,
    ) -> str:
        """
        Run unified optimization for all experiments in a task.
        Decides between normal or prompt-based optimization based on checkbox state.

        Args:
            task_name (str): Name of the optimization task
            use_prompts (bool): Whether to use custom prompts
            prompts_path (str): Path to JSON prompts directory
            population_size (int): Population size for genetic algorithm
            seed (int): Random seed for reproducibility

        Returns:
            str: Formatted results message
        """
        # Validate inputs when prompts are enabled
        if use_prompts:
            if not prompts_path or prompts_path.strip() == "":
                return "❌ Error: Please specify the prompts directory path when using custom initial prompts."

            # Run prompt-based optimization
            return self.run_prompt_task_optimization(
                task_name, prompts_path, population_size, seed
            )
        else:
            # Run normal optimization
            return self.run_task_optimization(task_name, population_size, seed)

    def run_unified_experiment_optimization(
        self,
        task_name: str,
        experiment_name: str,
        use_prompts: bool,
        prompts_path: str,
        population_size: int,
        seed: int,
    ) -> str:
        """
        Run unified optimization for a specific experiment.
        Decides between normal or prompt-based optimization based on checkbox state.

        Args:
            task_name (str): Name of the optimization task
            experiment_name (str): Name of the specific experiment
            use_prompts (bool): Whether to use custom prompts
            prompts_path (str): Path to JSON prompts directory
            population_size (int): Population size for genetic algorithm
            seed (int): Random seed for reproducibility

        Returns:
            str: Formatted results message
        """
        # Validate inputs when prompts are enabled
        if use_prompts:
            if not prompts_path or prompts_path.strip() == "":
                return "❌ Error: Please specify the prompts directory path when using custom initial prompts."

            # Run prompt-based optimization
            return self.run_prompt_experiment_optimization(
                task_name, experiment_name, prompts_path, population_size, seed
            )
        else:
            # Run normal optimization
            return self.run_experiment_optimization(
                task_name, experiment_name, population_size, seed
            )

    def run_unified_task_optimization_with_progress(
        self,
        task_name: str,
        use_prompts: bool,
        prompts_path: str,
        population_size: int,
        seed: int,
    ):
        """
        Run unified optimization with real-time progress updates.

        This is a generator function that yields progress updates.
        """
        # Clear previous logs
        global_stream_capture.clear_output()

        # Initial status
        yield "🚀 Starting optimization...\n"

        # Run optimization in a separate thread and stream logs
        import threading
        result_container = {"result": None, "error": None}

        def run_optimization():
            try:
                if use_prompts:
                    if not prompts_path or prompts_path.strip() == "":
                        result_container["error"] = "❌ Error: Please specify the prompts directory path when using custom initial prompts."
                        return
                    result_container["result"] = self.run_prompt_task_optimization(
                        task_name, prompts_path, population_size, seed
                    )
                else:
                    result_container["result"] = self.run_task_optimization(
                        task_name, population_size, seed
                    )
            except Exception as e:
                result_container["error"] = f"❌ Unexpected error: {str(e)}"

        # Start optimization in background
        opt_thread = threading.Thread(target=run_optimization)
        opt_thread.start()

        # Stream logs while optimization is running
        last_output = ""
        while opt_thread.is_alive():
            current_output = global_stream_capture.get_full_output()
            if current_output != last_output:
                yield current_output
                last_output = current_output
            time.sleep(0.5)  # Update every 500ms

        # Wait for thread to complete
        opt_thread.join()

        # Final output
        if result_container["error"]:
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
        use_prompts: bool,
        prompts_path: str,
        population_size: int,
        seed: int,
    ):
        """
        Run unified experiment optimization with real-time progress updates.

        This is a generator function that yields progress updates.
        """
        # Clear previous logs
        global_stream_capture.clear_output()

        # Initial status
        yield "⚡ Starting experiment optimization...\n"

        # Run optimization in a separate thread and stream logs
        import threading
        result_container = {"result": None, "error": None}

        def run_optimization():
            try:
                if use_prompts:
                    if not prompts_path or prompts_path.strip() == "":
                        result_container["error"] = "❌ Error: Please specify the prompts directory path when using custom initial prompts."
                        return
                    result_container["result"] = self.run_prompt_experiment_optimization(
                        task_name, experiment_name, prompts_path, population_size, seed
                    )
                else:
                    result_container["result"] = self.run_experiment_optimization(
                        task_name, experiment_name, population_size, seed
                    )
            except Exception as e:
                result_container["error"] = f"❌ Unexpected error: {str(e)}"

        # Start optimization in background
        opt_thread = threading.Thread(target=run_optimization)
        opt_thread.start()

        # Stream logs while optimization is running
        last_output = ""
        while opt_thread.is_alive():
            current_output = global_stream_capture.get_full_output()
            if current_output != last_output:
                yield current_output
                last_output = current_output
            time.sleep(0.5)  # Update every 500ms

        # Wait for thread to complete
        opt_thread.join()

        # Final output
        if result_container["error"]:
            yield result_container["error"]
        elif result_container["result"]:
            final_output = global_stream_capture.get_full_output()
            if final_output:
                yield final_output + "\n\n" + result_container["result"]
            else:
                yield result_container["result"]
        else:
            yield "❌ No result received from optimization"

    def _build_interface(self):
        """
        Build the Gradio interface with optimization capabilities.

        Returns:
            gr.Interface: Configured Gradio interface
        """
        with gr.Blocks(
            title="PROBE - SAM Optimization Interface", theme=gr.themes.Soft()
        ) as interface:
            # Header
            gr.Markdown("# 🔬 PROBE - SAM Optimization Interface")
            gr.Markdown(
                "Advanced interface for SAM optimization experiments using genetic algorithms and dynamic PROBE configuration"
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
                        autoscroll=False
                    )

                    status_output = gr.Textbox(
                        label="Status", lines=2, interactive=False
                    )

                    display_button.click(self.display_probe, outputs=probe_output)

                    save_button.click(self.save_logs_to_file, outputs=status_output)

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
                            probe_task_dropdown.change(
                                self.update_experiment_choices,
                                inputs=probe_task_dropdown,
                                outputs=probe_experiment_dropdown,
                            )

                    # Optional Prompts Section
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown(
                                "#### 🎯 Optional: Initial Prompts Configuration"
                            )
                            use_prompts_checkbox = gr.Checkbox(
                                label="Use custom initial prompts",
                                value=False,
                                info="Enable to use custom prompt configuration from JSON files",
                            )
                            probe_prompts_path = gr.Textbox(
                                label="Prompts Directory Absolute Path",
                                value="/home/carlosbc24/PycharmProjects/phd2_code/python_application/static_code/initial_prompts_configuration/covid",
                                info="Directory containing JSON prompt files",
                                visible=False,
                                interactive=True,
                            )

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

                    probe_output = gr.Textbox(
                        label="Optimization Results",
                        lines=20,
                        max_lines=30,
                        interactive=False,
                        autoscroll=False
                    )

                    # Event handlers for PROBE-based optimization with streaming
                    probe_task_dropdown.change(
                        self.update_experiment_choices,
                        inputs=probe_task_dropdown,
                        outputs=probe_experiment_dropdown,
                    )

                    probe_run_task_btn.click(
                        self.run_unified_task_optimization_with_progress,
                        inputs=[
                            probe_task_dropdown,
                            use_prompts_checkbox,
                            probe_prompts_path,
                            probe_pop_size,
                            probe_seed,
                        ],
                        outputs=probe_output,
                        show_progress="full"
                    )

                    probe_run_exp_btn.click(
                        self.run_unified_experiment_optimization_with_progress,
                        inputs=[
                            probe_task_dropdown,
                            probe_experiment_dropdown,
                            use_prompts_checkbox,
                            probe_prompts_path,
                            probe_pop_size,
                            probe_seed,
                        ],
                        outputs=probe_output,
                        show_progress="full"
                    )

                    use_prompts_checkbox.change(
                        self.toggle_prompts_visibility,
                        inputs=[use_prompts_checkbox],
                        outputs=[probe_prompts_path],
                    )

        return interface

    def launch(self, **kwargs):
        """
        Launch the Gradio interface.

        Args:
            **kwargs: Additional arguments for Gradio launch
        """
        return self.interface.launch(**kwargs)
