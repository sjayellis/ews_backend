from flask import Flask, jsonify, request
import yaml
from .run_calculation import run_apptainer, render_psi4_input



app = Flask(__name__)


@app.route('/run_data', methods=['POST'])
def run_data():
    data = request.json
    
    # Get copy of repo
    filename = "psi4_test.in"
    output_path = "/mnt/c/Users/Sam_Local/Desktop/Molssi/flask_testing/task_executer/data/"
    filepath_to_container = "/mnt/c/Users/Sam_Local/Desktop/Molssi/flask_testing/task_executer/task_runner/container/education_container.sif"
    path_to_jinja_templates = "/mnt/c/Users/Sam_Local/Desktop/Molssi/flask_testing/task_executer/task_runner/templates"
    
    input_file = render_psi4_input(template_directory=path_to_jinja_templates, template_name="input_template", inputs=data, output_path=output_path, filename=filename)
    commands = [["psi4", "--version"], ["psi4", "-i", f"/data/{input_file}", "-o", "/data/output.dat"]]
    result = run_apptainer(filepath_to_container, commands[1], [[output_path, "/data"]])
        
    return result



if __name__ == "__main__":
    app.run()