from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.weakproxy import WeakProxy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.listview import ListView
from kivy.properties import *
import kivy.core.text
import glob
import os.path
from collections import OrderedDict
from kivy.lang import Builder

__version__ = "0.1"
_ALIGN_SYMBOLS = {'left': '<', 'center': '^', 'right': '>'}
__kv_mode__ = False


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

def table_row_str(cols, width=500, align="left"):
    assert cols.__iter__
    align_char = _ALIGN_SYMBOLS[align]
    col_count = len(cols)
    col_width, col_overflow = divmod(width, col_count)
    assert col_overflow == 0
    for col in cols:
        assert len(col) <= col_width
    col_frmt_str = "|{:%s%s}|" % (align_char, col_width)
    frmt_str = col_frmt_str * col_count
    return frmt_str.format(*cols)

class TableRowFactory(object):
    class Row(object):
        def __init__(self, *cols, **kwargs):
            self.cols = cols
            assert 'col_width' in kwargs.keys() or 'row_width' in kwargs.keys()
            pass

        def to_string(self):
            pass

        @classmethod
        def from_string(cls, row_str):
            assert row_str[0] == '|' and row_str[-1] == '|'
            inner_str = row_str[1:-1]
            cols = [col.strip() for col in inner_str.split('||')]
            calc_fixed_width = (len(inner_str) - (2 * len(cols))) / len(cols)

    def __init__(self, width=500, align='left'):
        self.width = width
        self.align_str = align

    @property
    def align_char(self):
        return _ALIGN_SYMBOLS[self.align_str]

class RootWidget(BoxLayout):
    '''This the class representing your root widget.
       By default it is inherited from FloatLayout,
       you can use any other layout/widget depending on your usage.
    '''
    orientation = OptionProperty('vertical', options=(
                                 'horizontal', 'vertical'))
    spacing = NumericProperty(10)

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        pass

if __kv_mode__:
    Builder.load_string('''
<InputGrid>:
    id: grid_root
    GridLayout:
        cols: 2
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: "Reset"
            on_press: grid_root._handle_btn_press(self)
        Widget:
        Button:
            text: "Submit"
            on_press: grid_root._handle_btn_press(self)
''')

class InputGrid(BoxLayout):
    label_align = OptionProperty('left', options=['left', 'center', 'right'])

    def __init__(self, **kwargs):
        super(InputGrid, self).__init__(size_hint_y=0.5, **kwargs)
        if not __kv_mode__:
            self.add_widget(GridLayout(cols=2))
            self.add_widget(BoxLayout(orientation='vertical'))

        self.btn_box, self.inputs_grid = self.children
        assert isinstance(self.inputs_grid, GridLayout)
        assert isinstance(self.btn_box, BoxLayout)

        if not __kv_mode__:
            self.btn_box.add_widget(Button(text="Reset", on_press=self._handle_btn_press))
            self.btn_box.add_widget(Widget())
            self.btn_box.add_widget(Button(text="Submit", on_press=self._handle_btn_press))

        self.btn_submit, fill_widget, self.btn_reset = self.btn_box.children

        self._inputs_dict = OrderedDict()
        self._labels = OrderedDict()
        self._align_char = _ALIGN_SYMBOLS[kwargs.get("label_align", "left")]
        self._fixed_width = kwargs.get("label_width", 10)
        assert isinstance(self._fixed_width, int)
        self.fixed_width = NumericProperty(self._fixed_width)
        self.output_table = None

    def add_input(self, new_label, new_id):
        formatted_str = self.__get_frmt_str().format(new_label)
        child_count = len(self.inputs_grid.children)
        self.inputs_grid.add_widget(Label(text=formatted_str), 0)
        self.inputs_grid.add_widget(TextInput(multiline=False, write_tab=False), 0)
        new_inp, new_lbl = self.inputs_grid.children[0:2]
        self._inputs_dict[new_id] = new_inp.proxy_ref
        self._labels[new_id] = new_lbl.proxy_ref
        return True

    def on_fixed_width(self, instance, value):
        self._fixed_width = int(value)
        print "set fixed width to", value

    def __get_frmt_str(self):
        return "{:%s%s}" % (self._align_char, self._fixed_width)

    def gather_inputs(self):
        new_o_dict = OrderedDict()
        for k, v in self._inputs_dict.items():
            new_o_dict[k] = v.text
        return new_o_dict

    def clear_inputs(self, *args):
        for _w in self._inputs_dict.values():
            assert isinstance(_w, TextInput)
            print "clearing", _w
            _w.text = ''

    def gather_all2(self):
        assert isinstance(self.output_table.table, ListView)
        old_rows = self.output_table.table.item_strings
        new_row = table_row_str(self.gather_inputs().values(), width=72)
        self.output_table.table.item_strings = old_rows + [new_row]

    def bind_table(self, table_instance):
        assert isinstance(table_instance, OutputTable)
        self.output_table = table_instance
        self.update_table_header()

    def update_table_header(self):
        assert isinstance(self.output_table, OutputTable)
        if len(self._labels.values()) == 0:
            return False
        self.output_table.set_th(table_row_str([k.text for k in self._labels.values()], width=72))
        return True

    def _handle_btn_press(self, instance):
        assert isinstance(instance, Button)
        print instance
        if instance.text == "Submit":
            return self.gather_all2()
        if instance.text == "Reset":
            return self.clear_inputs()
        else:
            raise Exception


class OutputTable(BoxLayout):
    orientation = OptionProperty('vertical', options=(
                                 'horizontal', 'vertical'))

    def __init__(self, **kwargs):
        super(BoxLayout, self).__init__(**kwargs)
        self.add_widget(Label(text="HI", bold=True, size_hint_y=None, height=30))
        self.add_widget(ListView())
        self.table = self.children[0]
        assert isinstance(self.table, ListView)
        self.do_layout()

    def set_th(self, value):
        self.children[1].text = value


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

    def build(self):
        '''Your app will be build from here.
           Return your root widget here.
        '''

        print 'build running'
        global app_root
        app_root = RootWidget()

        assert isinstance(app_root, BoxLayout)

        app_root.add_widget(InputGrid(label_align="left", label_width=11, cols=2), index=0)
        app_inputs_grid = app_root.children[0]
        assert isinstance(app_inputs_grid, InputGrid)

        app_root.add_widget(OutputTable())
        app_inputs_grid.bind_table(app_root.children[0])

        for row_x in range(1, 7):
            app_inputs_grid.add_input("Col%s:" % row_x, "txtin%s" % row_x)

        app_inputs_grid.update_table_header()
        app_inputs_grid.do_layout()
        app_root.do_layout()

        return app_root

    def on_pause(self):
        '''This is necessary to allow your app to be paused on mobile os.
           refer http://kivy.org/docs/api-kivy.app.html#pause-mode .
        '''
        return True

if __name__ == '__main__':
    MainApp().run()

