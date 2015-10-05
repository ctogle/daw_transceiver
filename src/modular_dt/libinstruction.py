import modular_core.fundamental as lfu

import time
from threading import Timer
from threading import Thread

if __name__ == '__main__':pass
if __name__ == 'modular_dt.libinstruction':
    lfu.check_gui_pack()
    lgm = lfu.gui_pack.lgm
    lgd = lfu.gui_pack.lgd
    lgb = lfu.gui_pack.lgb

class timer_event(lfu.mobject):

    label = 'timer event'
    active = True

    def __init__(self, function, delay, func_args = ()):
        lfu.mobject.__init__(self)
        self.function = function
        self.delay = delay
        self.func_args = func_args
        self.thread = Thread(target = self.be_active, args = ())
        self.thread.daemon = True
        self.thread.start()

    def be_active(self):
        while self.active:
            time.sleep(self.delay)
            Timer(self.delay,self.function,self.func_args).start()

class instruction_manager(lfu.mobject):

    def __init__(self,**kwargs):
        self._default('name','instruction manager',**kwargs)
        self._default('delay',1.0,**kwargs)
        lfu.mobject.__init__(self)
        self.queued = []
        self.to_remove = []
        self.performed = []

    def begin_checking(self):
        self.timer = timer_event(self.check_instructions,self.delay)

    def stop_checking(self):
        self.timer.active = False

    def check_instructions(self):
        check_time = time.time()
        for instruction, dex in zip(self.queued, range(len(self.queued))):
            if not dex in self.to_remove:
                if instruction.call_time + instruction.tolerance <\
                                  check_time:
                    #print 'time for instruction has expired!'
                    pass
                elif instruction.call_time - instruction.tolerance >\
                                  check_time:
                    #print 'not time for instruction yet!'
                    pass
                else:
                    if instruction():
                        self.performed.append(instruction)
                        self.to_remove.append(dex)

class instruction(lfu.mobject):

    def __init__(self,call_time,**kwargs):
        self.call_time = call_time
        self._default('name','instruction',**kwargs)
        self._default('call',(None,()),**kwargs)
        self._default('tolerance',1.0,**kwargs)
        lfu.mobject.__init__(self,**kwargs)

    def __call__(self):
        try:
            self.call[0](self.call[1])
            return True
        except:
            print 'instruction failed!'
            return False






