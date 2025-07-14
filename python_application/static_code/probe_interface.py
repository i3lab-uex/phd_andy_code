import gradio as gr
from python_application.generated_code.model.PROBE import PROBE


class ProbeInterface:
    def __init__(self, probe: PROBE):
        self.probe = probe
        self.task_names = [ot.name for ot in probe.optimization_task]
        self.interface = self._build_interface()

    def display_probe(self):
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

    def save_logs_to_file(self):
        content = self.display_probe()
        filepath = "probe_log.txt"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Logs correctly saved to {filepath}"

    def update_experiment_choices(self, task_name):
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
        with gr.Blocks() as interface:
            gr.Markdown("# 🧠 PROBE GUI Interface")
            with gr.Tabs():
                with gr.TabItem("👁️ PROBE Viewer"):
                    gr.Markdown("## 🔬 PROBE Configuration Viewer")
                    output_textbox = gr.Textbox(label="Output:", lines=25)
                    display_btn = gr.Button("🔍 Show PROBE Configuration")
                    display_btn.click(
                        fn=self.display_probe, inputs=[], outputs=output_textbox
                    )
                    save_status = gr.Textbox(
                        label="Filename saved", lines=1, interactive=False
                    )
                    save_btn = gr.Button("Save logs")
                    save_btn.click(
                        fn=self.save_logs_to_file, inputs=None, outputs=save_status
                    )

                with gr.TabItem("⚙️ Run Algorithms"):
                    gr.Markdown("## 🧪 Run experiments for selected optimization tasks")
                    with gr.Row():
                        default_task = self.task_names[0] if self.task_names else None
                        task_selector = gr.Dropdown(
                            label="Select an optimization task",
                            choices=self.task_names,
                            value=default_task,
                        )

                    with gr.Row():
                        default_experiments = (
                            [
                                exp.name
                                for exp in self.probe.optimization_task[0].experiment
                            ]
                            if self.probe.optimization_task
                            else []
                        )
                        experiment_selector = gr.Dropdown(
                            label="Select an experiment",
                            choices=default_experiments,
                            value=(
                                default_experiments[0] if default_experiments else None
                            ),
                        )

                        task_selector.change(
                            fn=self.update_experiment_choices,
                            inputs=[task_selector],
                            outputs=experiment_selector,
                        )

                        run_single_btn = gr.Button("▶ Run experiment")

                    run_all_btn = gr.Button("⏩ Run all experiments for selected task")
                    execution_output = gr.Textbox(label="Execution status", lines=10)

                    run_single_btn.click(
                        fn=self.probe.run_single_experiment,
                        inputs=[task_selector, experiment_selector],
                        outputs=execution_output,
                    )
                    run_all_btn.click(
                        fn=self.probe.run_all_experiments_for_task,
                        inputs=[task_selector],
                        outputs=execution_output,
                    )

        return interface

    def launch(self):
        self.interface.launch()
