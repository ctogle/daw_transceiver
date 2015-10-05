import modular_core.fundamental as lfu

import modular_dt.libinstruction as lir
import modular_dr.libphidgmotor as lpm

import subprocess,thread,types,time,sys,os

import pdb

if __name__ == '__main__':pass
if __name__ == 'modular_dt.libsignaler':
    lfu.check_gui_pack()
    lgm = lfu.gui_pack.lgm
    lgd = lfu.gui_pack.lgd
    lgb = lfu.gui_pack.lgb

#this class only handles instruction file based signaling
class signaler(lfu.mobject):

    def __init__(self,*args,**kwargs):
        self._default('name','signaler',**kwargs)
        ipath = os.path.join(os.getcwd())
        self._default('instr_path',ipath,**kwargs)
        self._default('instr_file','',**kwargs)
        self._default('max_offset',lpm.max_offset,**kwargs)
        self._default('max_position',self.max_offset,**kwargs)
        self._default('min_position',-self.max_offset,**kwargs)
        self._default('domain_units','minutes',**kwargs)
        self._default('range_scheme','normalized',**kwargs)
        self._default('slider_resolution',5000,**kwargs)
        self._default('check_abort_delay',1.0,**kwargs)
        lfu.mobject.__init__(self,*args,**kwargs)
        self.signaling = False
        self.instruction_manager = lir.instruction_manager(delay = 0.5)

    def verify_time_units(self, values):
        if not self.domain_units == 'seconds':
            if self.domain_units == 'minutes':conv_factor = 60.0
            elif self.domain_units == 'hours':conv_factor = 3600.0
            elif self.domain_units == 'minutes':conv_factor = 60.0
            elif self.domain_units == 'milliseconds':conv_factor = 0.001
        else:conv_factor = 1.0
        return [conv_factor*float(val) for val in values]

    def verify_range_units(self, values):
        if not self.range_scheme == 'absolute':
            if self.range_scheme == 'normalized':
              #conv_factor = self.max_offset
              conv_factor = int(abs(int(self.max_position) -\
                    int(self.min_position)) / 2.0)
              #off by an additive factor equal to distance between zeros
            if self.range_scheme == 'differential (cm)':conv_factor = 55000.0/31.5
        else:conv_factor = 1.0
        return [int(conv_factor*float(val)) for val in values]

    def default_speak(self,message):print message
    def signal(self,*args,**kwargs):
        self.instruction_manager.begin_checking()
        all_queued_performed = False
        while not self.aborted or not all_queued_performed:
            time.sleep(self.check_abort_delay)
            all_queued_performed =\
                len(self.instruction_manager.performed) >=\
                len(self.instruction_manager.queued)
        print 'instruction manager no longer checking'
        self.instruction_manager.stop_checking()

    def load_instructions(self, start_time, speak):

        def issue(message, delay):
            instr_num = len(self.instruction_manager.queued)
            instruction_label = 'instruction-' + str(instr_num)
            instruction_time = start_time + delay
            self.instruction_manager.queued.append(
                lir.instruction(instruction_time, 
                    call = (speak, str(message)), 
                    label = instruction_label))

        try: parse = self.parse_results
        except AttributeError:
            print 'no parse results!'
            return

        ppos = parse['position']
        ptim = parse['time']
        for pair in zip(ppos,ptim):issue(pair[0], pair[1])

    def on_begin_signaling(self,*args,**kwargs):
        if self.signaling:print 'already signaling';return
        self.aborted = False
        if self.parent is None:message_function = self.default_speak
        else:message_function = self.parent.on_speak_message
        start_time = time.time()
        self.load_instructions(start_time,message_function)
        thread.start_new_thread(self.signal, (start_time, ))
        self.signaling = True

    def on_abort(self):self.aborted = True
    def on_choose_file(self):
        fidlg = lgd.create_dialog('Choose File', 'File?', 'file')
        self.instr_path = fidlg()
        self._rewidget(True)

    def on_parse_file(self):
        with open(self.instr_path,'r') as h:lines = h.readlines()
        if self.instr_path.endswith('.txt'):parser = self.parse_instructions_txt
        if self.instr_path.endswith('.csv'):parser = self.parse_instructions_csv
        parser(lines)

    def verify_parse_result(self, lines):
        dom, rng = [li for li in zip(*lines)]
        dom = self.verify_time_units(dom)
        rng = self.verify_range_units(rng)
        return {'time': dom, 'position': rng}

    def parse_instructions_csv(self,lines):
        nl = '\r'
        if len(lines) == 1:lines = lines[0].split(nl)
        lines = [tuple(l.split(',')) for l in lines]
        self.parse_results = self.verify_parse_result(lines)

    def parse_instructions_txt(self,lines):
        nl = '\n'
        if len(lines) == 1:lines = lines[0].split(nl)
        lines = [tuple(l.split(',')) for l in lines]
        self.parse_results = self.verify_parse_result(lines)

    def on_output_parse_results(self):
        try: print self.parse_results
        except AttributeError: print 'gotta parse to get results!'

    def _widget(self,*args,**kwargs):
        window = args[0]
        self._sanitize(*args,**kwargs)
        self.widg_templates.append(
            lgm.interface_template_gui(
                widgets = ['button_set', 'text'], 
                initials = [None, [self.instr_path]], 
                instances = [None, [self]], 
                keys = [None, ['instr_path']], 
                labels = [['Begin Signaling', 'Abort Signaling', 
                    'Choose File', 'Parse File','Print Parse Results'],None], 
                bindings = [[self.on_begin_signaling, self.on_abort, 
                    lgb.create_reset_widgets_wrapper(window,self.on_choose_file), 
                    self.on_parse_file, self.on_output_parse_results],None]))
        self.widg_templates.append(
            lgm.interface_template_gui(
                layout = 'horizontal', 
                widgets = ['radio', 'radio'], 
                labels = [
                    ['seconds','minutes','hours','milliseconds'], 
                    ['absolute','normalized','differential']], 
                initials = [[self.domain_units],[self.range_scheme]], 
                instances = [[self], [self]], 
                keys = [['domain_units'], ['range_scheme']], 
                box_labels = ['Delay Units', 'Position Units']))
        self.widg_templates.append(
            lgm.interface_template_gui(
                widgets = ['slider_advanced', 'slider_advanced'], 
                layout = 'horizontal', 
                initials = [[self.max_position], [self.min_position]], 
                orientations = [['vertical'], ['vertical']], 
                minimum_values = [[-self.max_offset],[-self.max_offset]], 
                maximum_values = [[self.max_offset],[self.max_offset]], 
                positions = [['left'], ['right']], 
                intervals = [[self.slider_resolution],[self.slider_resolution]], 
                instances = [[self], [self]], 
                minimum_sizes = [[(120, 240), (120, 240)]], 
                keys = [['max_position'], ['min_position']], 
                bind_events = [[None, None], [None, None]], 
                bindings = [[None, None], [None, None]], 
                box_labels = ['Max Position (+1.0)','Min Position (-1.0)']))
        lfu.mobject._widget(self,*args,from_sub = True)






