from subprocess import Popen

import time
from flask import Flask, jsonify
from flask import request
from base64 import b16encode
import os
import shutil

# Import the fixer
from werkzeug.contrib.fixers import ProxyFix


app = Flask(__name__)

# Use the fixer
app.wsgi_app = ProxyFix(app.wsgi_app)

compilerArray = [
    ['python', 'file.py', '', 'Python'],
    ['\'g++ -o /usercode/a.out\' ', 'file.cpp', '/usercode/a.out', 'C/C++'],
    ['javac', 'file.java', '\'./usercode/javaRunner.sh\'', 'Java'],
    ['\'vbnc -nologo -quiet\'', 'file.vb', '\'mono /usercode/file.exe\'', 'VB.Net'],
    ['gmcs', 'file.cs', '\'mono /usercode/file.exe\'', 'C#']
]


@app.route('/')
def index():
    return 'Alive'


def read_all_lines(filename):
    with open(filename, 'r') as f:
        return '\n'.join(f.readlines())


def extract_output_data(output_data_filename):
    data = read_all_lines(output_data_filename).split('*-COMPILEBOX::ENDOFOUTPUT-*')
    output_data = data[0]
    running_time = data[1]
    return output_data, running_time


def evaluate_code(folder, path, vm_name, timeout_value, language_index, code, stdin):
    _prepare_data(code, folder, language_index, path, stdin)
    command = _build_compile_command(folder, language_index, path, timeout_value, vm_name)
    process = Popen([command], shell=True)

    output_data_filename = path + folder + '/completed'
    error_data_filename = path + folder + '/errors'

    start_time = time.time()
    completed = False
    error_message = ''
    output_data = ''
    running_time = 0
    while time.time() - start_time < timeout_value and not completed:
        print('sleeping')
        time.sleep(1000)
        running_time += 1000

        # check to see if we're done
        if os.path.exists(output_data_filename):
            print('completed!')
            completed = True

    print('outside while loop')
    if completed:
        output_data, running_time = extract_output_data(output_data_filename)
        # check for any errors
        if os.path.exists(error_data_filename):
            error_message = read_all_lines(error_data_filename)
            print('error file existed, content was:', error_message)
    else:
        error_message = 'Code execution timed out.'
        print('timed out')
        process.terminate()
    return jsonify(errors=error_message, output=output_data, running_time=running_time)


def _build_compile_command(folder, language_index, path, timeout_value, vm_name):
    compiler_name = compilerArray[language_index][0]
    code_file = compilerArray[language_index][1]
    output_command = compilerArray[language_index][2]
    print(compiler_name, code_file, output_command, path, folder, vm_name)
    command = path + 'DockerTimeout.sh ' + str(timeout_value) \
              + 's -u mysql -e \'NODE_PATH=/usr/local/lib/node_modules\' -i -t -v  "' \
              + path + folder + '":/usercode ' + vm_name \
              + ' /usercode/script.sh ' + compiler_name + ' ' + code_file + ' ' + output_command
    print('Executing command:\n%s' % command)
    return command


def _prepare_data(code, folder, language_index, path, stdin):
    # Create the folder that will be shared with Docker
    os.mkdir(path + folder)
    # Copy over the scripts to do compilation and run everything
    shutil.copy(path + 'Payload/javaRunner.sh', path + folder + '/javaRunner.sh')
    shutil.copy(path + 'Payload/script.sh', path + folder + '/script.sh')
    # Set the correct permissions on the folder
    os.chmod(path + folder, 0o777)
    # Write all the code to the file
    code_filename = compilerArray[language_index][1]
    with open(path + folder + '/' + code_filename, 'w') as f:
        f.write(code)
    os.chmod(path + folder + '/' + code_filename, 0o777)
    with open(path + folder + '/inputFile', 'w') as f:
        f.write(stdin)


@app.route('/compile', methods=['POST'])
def compile():
    json_data = request.get_json(force=True)
    language_index = json_data['language']
    code = json_data['code']
    stdin = json_data['stdin']

    # Create a cryptographically secure random folder name. This will be mounted/shared with Docker
    folder = 'temp/' + b16encode(os.urandom(10)).decode('ascii')
    path = os.path.dirname(os.path.abspath(__file__)) + '/API/'  # current working path

    # Tag of the docker machine we want to execute
    vm_name = 'virtual_machine'
    timeout_value = 20  # Timeout Value, In Seconds

    return evaluate_code(folder, path, vm_name, timeout_value, language_index, code, stdin)

# app.run(debug=True)