import modular_core.fundamental as lfu
import modular_core.io.mudp as ludp
import modular_core.settings as lset

import modular_dt.libsorter as lso
import modular_dt.libsignaler as lsg

import pdb

if __name__ == '__main__':pass
if __name__ == 'modular_dt.libdawcommander':
    lfu.check_gui_pack()
    lgm = lfu.gui_pack.lgm
    lgd = lfu.gui_pack.lgd
    lgb = lfu.gui_pack.lgb

class daw_commander(lfu.mobject):

    label = 'daw commander'

    def __init__(self,*args,**kwargs):
        self.settings_manager = lset.settings_manager(
            parent = self, filename = 'daw_trans_settings.txt')
        self.settings = self.settings_manager.read_settings()
        def_ip = lset.get_setting('default_IP')
        self.udp_receiver = ludp.receiver(
            parent = self, default_IP = def_ip)
        self.udp_transceiver = ludp.transceiver(
            parent = self, default_IP = def_ip)
        self.script_sorter = lso.sorter_script(parent = self)
        self.daw_signaler = lsg.signaler(parent = self)
        self.children = [
            self.script_sorter,self.daw_signaler,
            self.udp_transceiver,self.udp_receiver]
        lfu.mobject.__init__(self,*args,**kwargs)

    def on_test_udp_receiver_transceiver(self, *args, **kwargs):
        self.udp_receiver.listen(*args, **kwargs)
        self.udp_transceiver.speak(*args, **kwargs)

    def on_speak_go_left(self):
        self.udp_transceiver.speak(message = 'left')

    def on_speak_go_right(self):
        self.udp_transceiver.speak(message = 'right')

    def on_speak_go_zero(self):
        self.udp_transceiver.speak(message = 'zero')

    def on_speak_message(self, message):
        self.udp_transceiver.speak(message = message)

    def change_settings(self):
        if hasattr(self,'settings_manager'):  
            self.settings_manager.display()

    def interpret_udp(self,data):
        print 'transceiver received msg:',data

    def _widget(self,*args,**kwargs):
        window = args[0]
        self._sanitize(*args,**kwargs)
        self.widg_templates.append(
            lgm.interface_template_gui(
                widgets = ['button_set'], 
                labels = [['Test UDP System']], 
                bindings = [[self.on_test_udp_receiver_transceiver]]))
        self.widg_templates.append(
        	  lgm.interface_template_gui(
                widgets = ['panel'], 
                templates = [self.udp_receiver.widg_templates]))
        self.widg_templates.append(
            lgm.interface_template_gui(
                widgets = ['panel'], 
                templates = [self.udp_transceiver.widg_templates]))
        self.widg_templates.append(
            lgm.interface_template_gui(
                widgets = ['panel'], 
                templates = [self.script_sorter.widg_templates]))
        self.widg_templates.append(
            lgm.interface_template_gui(
                widgets = ['panel'], 
                templates = [self.daw_signaler.widg_templates]))
        self.widg_templates.append(
            lgm.interface_template_gui(
                widgets = ['button_set'], 
                labels = [['Say Left', 'Say Right', 'Say Zero']], 
                bindings = [[self.on_speak_go_left, 
                    self.on_speak_go_right, self.on_speak_go_zero]]))
        self.widg_templates.append(
            lgm.interface_template_gui(
                widgets = ['button_set'], 
                labels = [['Change Settings', 'Update GUI']], 
                bindings = [[self.change_settings, 
                    lgb.create_reset_widgets_function(window)]]))
        lfu.mobject._widget(self,*args,from_sub = True)





