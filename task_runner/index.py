from flask import Flask, jsonify, request
import yaml
from .run_calculation import run_apptainer, render_psi4_input


app = Flask(__name__)


# Define a function to set CORS headers
def add_cors_headers(response):
    response.headers[
        "Access-Control-Allow-Origin"
    ] = "*"  # Allow requests from any origin (for testing)
    response.headers[
        "Access-Control-Allow-Methods"
    ] = "GET, POST, PUT, DELETE, OPTIONS"  # Specify allowed HTTP methods
    response.headers[
        "Access-Control-Allow-Headers"
    ] = "Content-Type, Authorization"  # Specify allowed headers
    return response


# Apply the CORS headers to all routes
@app.after_request
def after_request(response):
    return add_cors_headers(response)


@app.route("/run_data", methods=["POST"])
def run_data():
    data = request.json

    # Get copy of repo
    filename = "psi4_test.in"
    output_path = "/Users/jingchen/Documents/MolSSI/molssi-ews/ews_backend/data/"
    filepath_to_container = "/Users/jingchen/Documents/MolSSI/molssi-ews/ews_backend/education_container.sif"
    path_to_jinja_templates = (
        "/Users/jingchen/Documents/MolSSI/molssi-ews/ews_backend/task_runner/templates"
    )

    input_file = render_psi4_input(
        template_directory=path_to_jinja_templates,
        template_name="input_template",
        inputs=data,
        output_path=output_path,
        filename=filename,
    )
    commands = [
        ["psi4", "--version"],
        ["psi4", "-i", f"/data/{input_file}", "-o", "/data/output.dat"],
    ]
    result = run_apptainer(filepath_to_container, commands[1], [[output_path, "/data"]])

    return result


if __name__ == "__main__":
    app.run()
