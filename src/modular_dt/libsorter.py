import modular_core.fundamental as lfu

import modular_dt.libinstruction as lir

import subprocess,thread,types,time,sys,os

import pdb

if __name__ == '__main__':pass
if __name__ == 'modular_dt.libsorter':
    lfu.check_gui_pack()
    lgm = lfu.gui_pack.lgm
    lgd = lfu.gui_pack.lgd
    lgb = lfu.gui_pack.lgb

#this class only handles script based sorting
class sorter_script(lfu.mobject):

    label = 'script sorter'
    check_file_time_delay = 1
    instruction_manager = lir.instruction_manager(delay = 0.5)
    image_directory = os.path.join(os.getcwd(),'resources')
    script = os.path.join(os.getcwd(),'get_total_project_lines.py')

    def __call__(self,*args,**kwargs):
        subp = subprocess.Popen([sys.executable,self.script],stdout=subprocess.PIPE)
        value,err  = subp.communicate()
        print 'script',self.script
        print 'returned',value
        #example: 'DECISION: ||', total, '||'
        return value.split('||')[1]

    def check_new_files(self):
        fis = os.listdir(self.image_directory)
        return [fi for fi in fis if not fi in self.processed_files]

    def sort(self,*args,**kwargs):
        while not self.aborted:
            time.sleep(self.check_file_time_delay)
            new_files = self.check_new_files()
            if new_files:
                new_result = self(new_files)
                self.sort_results.append(new_result)
                self.processed_files.extend(new_files)

    def on_begin_sorting(self, *args, **kwargs):
        self.aborted = False
        self.processed_files = []
        self.sort_results = []
        if self.parent is None:message_function = self.default_speak 
        else:message_function = self.default_speak 
        start_time = time.time()
        thread.start_new_thread(self.sort, (start_time, ))
        thread.start_new_thread(
            self.handle_sort_results,
            (start_time,message_function))

    def handle_sort_results(self, *args, **kwargs):
        start_time = args[0]
        speak_func = args[1]
        handled = []
        self.instruction_manager.begin_checking()
        while not self.aborted:
            if len(self.sort_results) > len(handled):
                result = self.sort_results[-1]
                self.handle_result(result, speak_func)
                handled.append(result)

    def handle_result(self,result,speak):

        def issue(message,delay):
            instr_num = len(self.instruction_manager.queued)
            instruction_label = 'instruction-' + str(instr_num)
            instruction_time = time.time() + delay
            self.instruction_manager.queued.append(
                lir.instruction(instruction_time, 
                    call = (speak, str(message)), 
                    label = instruction_label))

        def parse(entry):

            def fail(entry):print 'could not parse result', entry
            def check_lrz(ent):
                if ent in ['left', 'right', 'zero']:
                    return True

            try: return int(entry), 0.0
            except ValueError:
                check = check_lrz(entry)
                if check: return entry, 0.0
                try:
                    pair = eval(entry)
                    if type(pair) is types.TupleType:
                        try: delay = float(pair[1])
                        except: fail(entry)
                        try: return int(pair[0]), delay
                        except ValueError:
                            check = check_lrz(pair[0])
                            if check: return pair[0], delay
                            else: fail(entry)
                    else: fail(entry)
                except: fail(entry)

        #message should be left, right, zero, or an integer
        print 'result handling', result
        split = result.split(':')
        parsed = [parse(entry) for entry in split]
        for message, delay in parsed:issue(message, delay)

    def default_speak(self, message):print message
    def on_abort(self):self.aborted = True
    def on_output_sort_results(self):print self.sort_results
    def _widget(self,*args,**kwargs):
        window = args[0]
        self._sanitize(*args,**kwargs)
        self.widg_templates.append(
            lgm.interface_template_gui(
                widgets = ['button_set'], 
                labels = [['Begin Script Sorting', 'Abort Sorting', 
                    'Print Sort Results']], 
                bindings = [[self.on_begin_sorting, self.on_abort, 
                    self.on_output_sort_results]]))
        lfu.mobject._widget(self,*args,from_sub = True)





