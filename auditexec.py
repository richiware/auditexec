import sys, argparse, time, subprocess, threading, fnmatch

max_runtime = 120
executions = []
workers = []

class Execution:
    command = ''
    instances = 1
    count = None

    def print(self):
        print('Execution: command(' + self.command + '), instances(' + str(self.instances) + '), count(' +
                self.count + ')')

class Worker:
    exection = None
    thread = None
    instance = 0

    def __init__(self, execution, instance):
        self.execution = execution
        self.instance = instance

    def execute(self):
        try:
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
        except:
            print("Error: unable start thread to execute \"" + command + "\"")

    def run(self):
        start = time.perf_counter()
        proc = subprocess.Popen(self.execution.command.split(), stdout=subprocess.PIPE, text=True, encoding='utf-8')
        try:
            output, err = proc.communicate(timeout=max_runtime)
            print("Crash=" + str(time.perf_counter() - start) + " for Instance: " + str(self.instance) + " - Command: "
                    + self.execution.command)
        except subprocess.TimeoutExpired:
            proc.kill()
            output, err = proc.communicate()
            if self.execution.count:
                matching = fnmatch.filter(output.splitlines(), self.execution.count)
                print("Count=" + str(len(matching)) + " for Instance: " + str(self.instance) + " - Command: " + self.execution.command)



    def wait(self):
        self.thread.join()

def parse_options():
    global max_runtime

    opt_parser = argparse.ArgumentParser(description="Audit the execution of several applications")
    opt_parser.add_argument('--max_runtime', nargs=1, dest='max_runtime', help="Maximum time running the test (seconds).")
    opt_parser.add_argument('--exec', nargs=argparse.REMAINDER, dest='executions_str', help="Execution of a command.")

    exec_parser = argparse.ArgumentParser(description="Options for each execution")
    exec_parser.add_argument('--command', nargs=1, dest='command')
    exec_parser.add_argument('--instances', nargs=1, dest='instances')
    exec_parser.add_argument('--count', nargs=1, dest='count')

    options = vars(opt_parser.parse_args())

    break_position = 0
    next_args = ''

    while break_position != None:
        if options['executions_str']:
            try:
                break_position = options['executions_str'].index('---')
                next_args = options['executions_str'][break_position + 1:]
            except:
                break_position = None

            exec_options = vars(exec_parser.parse_args(options['executions_str'][0:break_position]))

            execution = Execution()
            if exec_options['command']:
                execution.command = exec_options['command'][0]
            if exec_options['instances']:
                execution.instances = int(exec_options['instances'][0])
            if exec_options['count']:
                execution.count = exec_options['count'][0]

            executions.append(execution)

        else:
            break_position = None

        if break_position != None:
            new_options = vars(opt_parser.parse_args(next_args))
            for k,v in new_options.items():
                if v:
                    options[k] = v

    if options['max_runtime']:
        max_runtime = int(options['max_runtime'][0])

def execute_workers():
    for execution in executions:
        count = 1
        while count <= execution.instances:
            worker = Worker(execution, count)
            workers.append(worker)
            worker.execute()
            count += 1

    for worker in workers:
        worker.wait()

if __name__ == "__main__":
    assert sys.version_info >= (3, 7)
    parse_options()
    execute_workers()
