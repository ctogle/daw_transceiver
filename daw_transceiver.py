import modular_core.fundamental as lfu
#import modular_dt.gui.libqtgui_daw_transceiver as praqg

if __name__ == '__main__':
    lfu.using_gui = True
    lfu.set_gui_pack('modular_dt.gui.libqtgui_daw_transceiver')
    lfu.gui_pack.initialize()


