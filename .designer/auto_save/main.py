from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.weakproxy import WeakProxy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.layout import Layout
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import *
import kivy.core.text
import glob
import os.path


class FontUtil(object):
    __fixed_width_fonts__ = ['Consolas', 'Courier New', 'Courier',
                             'Menlo', 'Monaco', 'Osaka'
                             ]

    def __init__(self):
        self._font_dirs = kivy.core.text.LabelBase.get_system_fonts_dir()
        assert isinstance(self._font_dirs, list)
        self._font_globs = ["%s*.*" % f1 for f1 in self.__fixed_width_fonts__] + ["*mono*.*", "*Mono*.*"]
        self._full_font_globs = []
        for f2 in self._font_dirs:
            for f3 in self._font_globs:
                self._full_font_globs.append(os.path.join(f2, f3))
        for f4 in self._full_font_globs:
            for f5 in glob.glob(f4):
                print f5



def table_row_str(*args, **kwargs):
    width = kwargs.get("width", 500)
    align_str = kwargs.get("align", "left")
    align_char = '<^>'[["left", "center", "right"].index(align_str)]
    col_count = len(args)
    col_width, col_overflow = divmod(width, col_count)
    assert col_overflow == 0
    col_frmt_str = "|{:%s%s}|" % (align_char, col_width)
    frmt_str = col_frmt_str * col_count
    return frmt_str.format(*args)

class RootWidget(FloatLayout):
    '''This the class representing your root widget.
       By default it is inherited from FloatLayout,
       you can use any other layout/widget depending on your usage.
    '''

    pass

class LabeledInput(BoxLayout):
    label_text = StringProperty("")

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(BoxLayout, self).__init__(**kwargs)
        lay_inp = AnchorLayout(anchor_x='left', anchor_y='bottom', height=50, size_hint_y=None, size_hint_x=0.5)
        lay_lbl = AnchorLayout(anchor_x='right', anchor_y='bottom', height=50, size_hint_y=None,size_hint_x=None)

        lbl_text = kwargs.get('lbl_text', 'Meow')
        lay_lbl.add_widget(Label(text=lbl_text, height=50))
        lay_inp.add_widget(TextInput(multiline=False, height=50))
        self.add_widget(lay_inp, 0)
        self.add_widget(lay_lbl, 1)

        assert len(self.children) == 2
        i_w, l_w = [c.children[0] for c in self.children]
        assert isinstance(l_w, Label)
        assert isinstance(i_w, TextInput)
        self._label = l_w.proxy_ref
        self._textinput = i_w.proxy_ref
        self._textinput.text = "------------------"

        i_w.parent.do_layout()
        l_w.parent.do_layout()
        self.do_layout()

    def clear(self):
        self._textinput.text = ''

    def get_value(self):
        return self._textinput.text

    def get_label(self):
        return self._label.text

    def on_label_text(self, instance, value):
        self._label.text = value

    def on_parent(self, instance, value):
        print "layoutting"
        instance.do_layout()
        value.do_layout()


class MainApp(App):
    '''This is the main class of your app.
       Define any app wide entities here.
       This class can be accessed anywhere inside the kivy app as,
       in python::

         app = App.get_running_app()
         print (app.title)

       in kv language::

         on_release: print(app.title)
       Name of the .kv file that is auto-loaded is derived from the name of this cass::

         MainApp = main.kv
         MainClass = mainclass.kv

       The App part is auto removed and the whole name is lowercased.
    '''
    title = 'Izzy\'s Logger Thingy'

    class LabeledInput(LabeledInput):
        pass

    def build(self):
        '''Your app will be build from here.
           Return your root widget here.
        '''
        def on_text(instance, value):
            print('The widget', instance, 'have:', value)

        def size_from_texture(instance, value):
            instance.size_hint = (None, None)
            instance.size = value
            instance.halign = 'right'

        print 'build running'
        global app_root
        app_root = RootWidget()
        global inputs_dict
        inputs_dict = {k: v for k, v in app_root.ids.items() if isinstance(v, TextInput)}

        grid_inputs = app_root.ids["gridinputs"]
        btn_reset = app_root.ids["btnreset"]
        btn_submit = app_root.ids["btnsubmit"]

        # assert isinstance(grid_inputs, GridLayout)
        assert isinstance(btn_submit, Button)
        assert isinstance(btn_reset, Button)

        global inputs
        inputs = inputs_dict.viewvalues()

        for x in inputs:
            assert isinstance(x, Widget)
            x.bind(text=on_text)
            x.multiline = False
            # x.size_hint_x = 0.3

        for lbl in [_i for _i in grid_inputs.children if isinstance(_i, Label)]:
            assert isinstance(lbl, Label)
            # lbl.bind(texture_size=size_from_texture)

        def reset_all(instance):
            assert isinstance(instance, Widget)
            for _x in inputs:
                _x.text = ''

        def gather_all(instance):
            #assert isinstance(instance, Widget)
            list_view_w = app_root.ids['output_table']

            form_dict = {k: v.text for k, v in inputs_dict.items()}
            sorted_keys = sorted(inputs_dict.keys())
            old_rows = list_view_w.item_strings
            new_row = table_row_str(*[form_dict[z] for z in sorted_keys], width=108)
            list_view_w.item_strings = old_rows + [new_row]
            print table_row_str(*[form_dict[z] for z in sorted_keys], width=96)
            print form_dict

        btn_reset.bind(on_press=reset_all)
        btn_submit.bind(on_press=gather_all)
        #btn_submit.parent.do_layout()

        print kivy.core.text.LabelBase.get_system_fonts_dir()
        FontUtil()
        gather_all(None)

        # app_root.bind(height=set_title)



        return app_root

    def on_pause(self):
        '''This is necessary to allow your app to be paused on mobile os.
           refer http://kivy.org/docs/api-kivy.app.html#pause-mode .
        '''
        return True

if __name__ == '__main__':
    MainApp().run()

