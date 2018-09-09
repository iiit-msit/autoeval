import os.path, subprocess
from subprocess import STDOUT,PIPE
import re
import sys
import platform
import os.path
import hashlib
import base64
import json
# import crypt
def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform
    return platforms[sys.platform]

def check_git():
    try:
        run_proc = subprocess.Popen(['git'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception as e:
        return False

def check_if_repo():
    run_proc = subprocess.Popen(['git', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = run_proc.communicate()
    if stderr: return False
    return True

def check_if_user():
    run_proc = subprocess.Popen(['git','config','user.name'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = run_proc.communicate()
    if stdout: return stdout.decode("utf-8").rstrip()
    return False

def submit_score(score_obj,msg):
    """ Take a score object and submit it to an endpoint
        kwargs:
        score object -- (<problemid>,<user.name>,<score>)
    """
    with open('md5/problem_id.txt', 'r') as f:
        data = f.read()
        if computeMD5hash(score_obj[0]) != data:
            print('Something is wrong with the problem ID. Result not generated.')
            return
    try:
        os.makedirs('result')
    except:
        pass

    try:
        if len(sys.argv)>=3 and sys.argv[2] == "-git":
            # to replcae contents for each run
            git_op_file = open("git_result.txt", "w+")
            git_op_file.close()
            runProcess(["git","add","."])
            runProcess(["git","commit", "-m","\"" + msg + " \""])
            runProcess(["git","push","-u","origin","master"])
            git_op_file = open("git_result.txt", "r")
            git_op = git_op_file.read()
            if "fatal: " in git_op or "! [rejected]" in git_op:
                print("Git Status: push unsuccessful. Details in git_output.txt")
            else:
                print("Git Status: push successful. Details in git_output.txt")
        # version_number = subprocess.check_output(["git","shortlog","-s","--grep="+str(score_obj[0].decode('utf8')).strip()])
        # print(["git","shortlog","-s","--grep="+str(score_obj[0])], version_number)
        # version_number = version_number.strip().split('\t')[0]
        # if int(version_number):
        #     version_number = "v"+str(version_number).replace('\n','')
        # else:
        #     version_number = "v1"
        scorejson = {'problem_id':str(score_obj[0].decode('utf-8')).strip(),'user_id':score_obj[1],'score':score_obj[2], STYLE_CHECKER+'_score':score_obj[3]}
        with open('result/score.json','w') as f:
            json.dump(scorejson,f)
        with open('md5/score.txt','w') as f:
            f.write(computeMD5hash(str(f)))
    except Exception as e:
        print(e)
        print("Caution: Couldn't submit your code. Check internet connection or Git repo.")
        pass

def runProcess(command):
    git_op_file = open("git_result.txt", "a")
    run_proc = subprocess.call(command, stdout=git_op_file, stderr=subprocess.STDOUT)
    git_op_file.close()
       
def runProcessUseFileout(command, filename):
    run_proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    proc_out = run_proc.stdout.read().decode('utf-8')
    with open(filename, 'w+') as logfile:
        logfile.write(proc_out)
    return proc_out

def which_python():
    if (sys.version_info > (3, 0)):
        return 3
    else:
        return 2

python_version = which_python()

def computeMD5hash(stringg):
    m = hashlib.md5()
    if python_version == 2:
        m.update(stringg.encode('utf8'))
    else:
        m.update(str.encode(str(stringg), 'utf-8'))
    return m.hexdigest()

def get_content(filename):
    with open(filename, "rb") as f:
        return f.read()

def execute(file, stdin):
    from threading import Timer
    
    filename,ext = os.path.splitext(file)
    if ext == ".java":
        subprocess.check_call(['javac', file])     #compile
        cmd = ['java', file.strip('.java')]                     #execute
    elif ext == ".c":
        subprocess.check_call(['gcc',"-o","Solution","Solution.c"])     #compile
        if(platform.system() == "Windows"):
            cmd = ['Solution']              #execute for windows OS.
        else:
            cmd = ['./Solution']            #execute for other OS versions
    else:
        cmd = ['python', file]
    
    kill = lambda process: process.kill()
    proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    
    my_timer = Timer(10, kill, [proc])
    try:
        my_timer.start()
        stdout,stderr = proc.communicate(stdin)
    except Exception as e:
        stdout = 'Caution: Your program is running for more than 10 seconds.'
    finally:
        my_timer.cancel()
    
    return stdout

def run_test(testcase_input,testcase_output):
    input1 = get_content('testcases/'+testcase_input)
    md5input = get_content("md5/"+testcase_input)
    output = get_content('testcases/'+testcase_output)
    md5output = get_content("md5/"+testcase_output)
    your_output = execute(program_name, input1)

    if python_version == 3:
        md5input = md5input.decode('utf-8')
        md5output = md5output.decode('utf-8')

    if computeMD5hash(input1) != md5input or computeMD5hash(output) != md5output:
        # print(computeMD5hash(input1),md5input,computeMD5hash(output),md5output)
        return False

    if python_version == 3:
        your_output = your_output.decode('UTF-8').replace('\r','').rstrip() #remove trailing newlines, if any
        output = output.decode('UTF-8').replace('\r','').rstrip()
    else:
        your_output = your_output.replace('\r','').rstrip() #remove trailing newlines, if any
        output = output.replace('\r','').rstrip()

    return input1,output,your_output,output==your_output

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.environ.get("_MEIPASS2",os.path.abspath("."))

    return os.path.join(base_path, relative_path)

def run_tests(inputs,outputs,extension):
    passed = 0
    problemid = get_content("testcases/problem_id.txt")
    tc_result_dict = {}
    res_str = ""
    for i in range(len(inputs)):
        result = run_test(inputs[i],outputs[i])
        tc_result_dict[i] = {}
        if result == False:
            res_str += "########## Testcase "+str(i)+": Failed ##########\n"
            res_str += "Something is wrong with the testcase.\n"
        elif result[3] == True:
            res_str += "########## Testcase "+str(i)+": Passed ##########\n"
            res_str += "Expected Output: \n"
            res_str += result[1]+"\n"
            res_str += "Your Output: \n"
            res_str += result[2]+"\n"
            passed+=1
            tc_result_dict[i]['passed'] = True
            # tc_result_dict[i]['output'] = result[2]
        else:
            res_str += "########## Testcase "+str(i)+": Failed ##########\n"
            res_str += "Expected Output: \n"
            res_str += result[1]+"\n"
            res_str += "Your Output: \n"
            res_str += result[2]+"\n"
            tc_result_dict[i]['passed'] = False
            # tc_result_dict[i]['output'] = result[2]
        res_str += "----------------------------------------\n"
    with open("testcases_output.txt", "w+") as tc_res_file:
        tc_res_file.write(res_str)
    print("Testcases Status: "+str(passed)+"/"+str(len(inputs))+" testcases passed. Details in testcases_output.txt")
    return (problemid, passed, len(inputs), tc_result_dict)

inputs = []
outputs = []

# populate input and output lists
for root,dirs,files in os.walk('testcases/'):
    for file in files:
        if 'input' in file and '.txt' in file and "md5" not in file:
            inputs.append(file)
        if 'output' in file and '.txt' in file and "md5" not in file:
            outputs.append(file)
    break

# if get_platform() == 'Windows':
if not check_git():
    raise Exception('git not available')

if not check_if_repo():
    raise Exception('You are not in git repo')

if not check_if_user():
    raise Exception('user not logged in')

inputs = sorted(inputs)
outputs = sorted(outputs)

if len(sys.argv)>=2 and os.path.isfile(sys.argv[1]):
    style_fname = ""
    if sys.argv[1].endswith(".java"):
        style_fname = "check_style_errors.txt"
        program_name = sys.argv[1]
        extension = ".java"
        result = run_tests(inputs,outputs,extension)
        proc_out = runProcessUseFileout(['java', '-jar', resource_path('data/checkstyle-8.12-all.jar'), '-c', resource_path('data/sun_checks_custom.xml'), program_name], style_fname)
        score = 0
        if len(proc_out) <= 32: score = 1
        problemid, cases, totalcases, tc_result_dict = result
        STYLE_CHECKER = "check_style"
        totalscore = 1
        
        proc_out = re.findall("Checkstyle ends with (.*) errors.", proc_out)
        if proc_out == []:
            proc_out = "Your code has scored "+str(score)+"/"+str(totalscore)
        else:
            proc_out = "Checkstyle ends with "+str(proc_out[0])+" errors."

    elif sys.argv[1].endswith(".py"):
        style_fname = "pylint_errors.txt"
        program_name = sys.argv[1]
        extension = ".py"
        result = run_tests(inputs,outputs,extension)
        problemid, cases, totalcases, tc_result_dict = result
        proc_out = runProcessUseFileout(["pylint",program_name], style_fname)
        proc_out = re.findall("Your code has been rated at (.*)/(.*) \(.*\)", proc_out)
        score, totalscore = 0,0
        if proc_out:
            score = int(float(proc_out[0][0]))
            totalscore = int(float(proc_out[0][1]))
        STYLE_CHECKER = "pylint"

    elif sys.argv[1].endswith(".c"):
        program_name = sys.argv[1]
        extension = ".c"
        result = run_tests(inputs,outputs,extension)
        exit(0)
    elif sys.argv[1] == "eval.py":
        print("eval.py cannot be passed as argument")
        exit(0)
    else:
        print("Invalid Extension.\nPass only .java or .py files")
        exit(0)

    msg = str(problemid.decode('utf-8')).strip() + ": " + str(cases)+"/"+str(totalcases)+" testcases passed. "+ STYLE_CHECKER +" score: "+str(score)+"/"+str(totalscore)
    print("Code Style: "+str(proc_out)+" Details in "+style_fname)
    # print(str(problemid.decode('utf-8')).strip())
    submit_score((problemid, check_if_user() , tc_result_dict, str(score)+'/'+str(totalscore)), msg)
else:
    print("File not found.\nPass a valid filename with extension as argument.\npython eval.py <filename>")

