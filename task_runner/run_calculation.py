from jinja2 import Environment, FileSystemLoader

import shutil
import time
import os
import subprocess
import json
from typing import List, Dict, Tuple, Any

_apptainer_cmd = None


def get_apptainer_cmd() -> str:
    global _apptainer_cmd

    if _apptainer_cmd is not None:
        return _apptainer_cmd

    _apptainer_cmd = shutil.which("apptainer")
    if _apptainer_cmd is None:
        _apptainer_cmd = shutil.which("singularity")
    if _apptainer_cmd is None:
        raise RuntimeError("apptainer or singularity not found in PATH")

    return _apptainer_cmd

def run_apptainer(sif_path: str, command: List[str], volumes: List[Tuple[str, str]]) -> Dict[str, Any]:

    cmd = [get_apptainer_cmd()]

    volumes_tmp = [f"{v[0]}:{v[1]}" for v in volumes]
    cmd.extend(["run", "--bind", ",".join(volumes_tmp), sif_path])
    cmd.extend(command)

    time_0 = time.time()
    proc_result = subprocess.run(cmd, capture_output=True, text=True)
    time_1 = time.time()

    if proc_result.returncode == 0:
        return {"success": True, "stdout": proc_result.stdout}
    else:
        msg = (
            f"Running in apptainer failed with error code {proc_result.returncode}\n"
            f"stdout: {proc_result.stdout}\n"
            f"stderr: {proc_result.stderr}"
        )

        ret = {"success": False, "error": {"error_type": "RuntimeError", "error_message": msg}}
        return ret
    
def render_input(template_directory: str, template_name: str, inputs: Dict[str, Any], filename: str = None) -> str:
    environment = Environment(loader=FileSystemLoader(template_directory))
    template = environment.get_template(template_name)

    if filename is None:
        filename = f"{'_'.join(list(inputs.keys()))}"

    content = template.render(inputs)

    with open(filename, mode="w", encoding="utf-8") as input:
        input.write(content)
    
    return filename

def process_molecule(molecule_name: str, molecules: List[List[str]]) -> str:
    proc_mol = f"{molecule_name} {{\n"
    for mol in molecules:
        mol_str = "  "
        for i in range(0,len(mol)):
            mol_str += f"{mol[i]} "
        mol_str += "\n"
        
        proc_mol += mol_str
    proc_mol += "}"
    return proc_mol

def render_psi4_input(template_directory: str, template_name: str, inputs: Dict[str, Any], output_path: str, filename: str = None) -> str:
    environment = Environment(loader=FileSystemLoader(template_directory))
    template = environment.get_template(template_name)
    
    hf_methods = ["HF", "MP2", "MP4", "CCSD(T)"]
    dft_methods = ["PBE", "B3LYP", "M06", "M06-D3"]
    if inputs["method"] in hf_methods:
        inputs["reference"] += "hf"
    elif inputs["method"] in dft_methods:
        inputs["reference"] += "ks"
    else:
        raise TypeError("Method not recognized as HF or DFT method.")

    if filename is None:
        filename = f"{'_'.join(list(inputs.keys()))}"

    content = template.render(inputs)

    with open(output_path+filename, mode="w", encoding="utf-8") as input:
        input.write(content)
    
    return filename


# mol_name = "benzene"
# mol_list =   [["0", "1"],
#     ["C", "-0.332299786126", "1.266293763992", "-2.614838533626"],
#     ["C", "0.349364948473", "-1.405736084573", "-2.053211127230"],
#     ["C", "1.020488041771", "0.885549327624", "-2.541894070443"],
#     ["C", "-1.003239896063", "-1.025876820472", "-2.129389566957"],
#     ["C", "-1.344397149122", "0.310721315449", "-2.406682914582"],
#     ["C", "1.361021504218", "-0.450112768420", "-2.258845478849"],
#     ["H", "-0.597444236584", "2.304886349910", "-2.828097741910"],
#     ["H", "0.615252976785", "-2.442033294231", "-1.829683359417"],
#     ["H", "1.806668588160", "1.628112492256", "-2.700437111401"],
#     ["H", "-1.790003212223", "-1.767955258107", "-1.970079207440"],
#     ["H", "-2.394850547123", "0.607656321453", "-2.458092486410"],
#     ["H", "2.411449677875", "-0.744182632917", "-2.193390546325"]]
# mol_str = process_molecule(mol_name, mol_list)
# inputs = {
#     "calculation": 'optimize',
#     "method": 'HF',
#     "freeze_core": 'True',
#     "reference": 'r',
#     "basis_set": 'aug-cc-pVDZ',
#     "molecule": mol_str
# }
# with open("psi4_test.json", "w") as file:
#     file.write(json.dumps(inputs))
# print(inputs)

# inputs = {}
# with open("psi4_test.json", "r") as file:
#     inputs = json.load(file)

# filename = "psi4_test.in"
# output_path = "/mnt/c/Users/Sam_Local/Desktop/Molssi/flask_testing/task_executer/data/"
# input_file = render_psi4_input(template_directory=f"{os.getcwd()+'/templates'}", template_name="input_template", inputs=inputs, output_path=output_path, filename=filename)
# commands = [["psi4", "--version"], ["psi4", "-i", f"/data/{input_file}", "-o", "/data/output.dat"]]
# result = run_apptainer("./container/education_container.sif", commands[1], [["/mnt/c/Users/Sam_Local/Desktop/Molssi/flask_testing/task_executer/data", "/data"]])
# print(result)