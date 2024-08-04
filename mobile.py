import kivy
import networkx as nx
import os


from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.app import Builder
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior





Window.clearcolor = (1, 1, 1, 1)

Builder.load_file('my.kv')

graph = 'sad'
graphs=[]

def upload(document):
    #Itt kapsz egy dokumentumot amivel lehet mokolni. 
    # Egyelore csak elmentem a helyet a filenak 
    # Ezek a graphs listaban vannak eltarolva
    return "sikeres"

def download():
    return nx.karatete_club_graph()

def kerdez(kerdes):
    #Itt a kivezetese a rakerdezesnek. 
    #Ennel a resznel megjelenik egy chat felulet a felhasznalo szamara,
    #ahol beirja a kerdeset amit a 'kerdes' valtozo tarol, ezutan ad egy valaszt 
    #ez kerul a return utan.
    return "valasz"

def test():
    #Ez a kivezetese a tesztnek.
    #  Itt nincs semmi argument amit a UI hiv, csak benne tortenik a moka. 
    # Nekem itt egy tuple kell ket stringgel. A 0. elem a kerdes, a masodik a vart valasz.
    return "kerdes", "vart valasz"



class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    pass

class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))



class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class NameDialog(FloatLayout):
    create = ObjectProperty(None)
    cancel = ObjectProperty(None)
    

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in range(100)]

#screen 2: Test
class Test(Screen):

    question,answer=test()

    def hide(self,obj,hid):
        try:
            if hid:
                obj.saved_attrs = obj.height, obj.size_hint_y, obj.opacity, obj.disabled
                obj.height, obj.size_hint_y, obj.opacity, obj.disabled = 0, None, 0, True
            else:
                obj.height, obj.size_hint_y, obj.opacity, obj.disabled = obj.saved_attrs
                del obj.saved_attrs
        except:
            pass

    def on_pre_enter(self, *args):
        self.hide(self.ids.answer,True)
        self.ids.txt.disabled=True
        self.ids.txt.hint_text=''
        return super().on_pre_enter(*args)

    def begin(self):
        Ques=True
        self.hide(self.ids.btn,Ques)
        self.ids.txt.disabled=False
        self.ids.txt.hint_text='Start typing your answer.'
        if self.ids.answer.height != 0:
            self.hide(self.ids.answer,Ques)
        self.ids.ques.text='[font=Afacad-Regular.ttf]' + str(self.question) + '[/font]'

    def submit(self):
        try:
            if self.ids.btn.height == 0:
                Ques=False
                answer='asd '
                self.ids.answer.text='[font=Afacad-Regular.ttf]'+ str(self.answer) + '[/font]'
                self.hide(self.ids.answer,Ques)
                Clock.schedule_once(lambda dt: self.hide(self.ids.btn,Ques), 3)
                self.ids.txt.text=''
                self.ids.txt.disabled=True
        except:
            pass

class Question(Screen):
    
    def input(self):
        self.ids.chat.text += '[font=Afacad-Regular.ttf]' +'\n' + str(kerdez(self.ids.txt.text)) + '[/font]'
        self.ids.txt.text = ''

class Graph(Screen):
    pass

class Upload(Screen):
    Text=''
    def __init__(self, **kwargs):
        super(Upload, self).__init__(**kwargs)
        self.ids.box.add_widget(RV())

    def on_enter(self, *args):
        self.ids.up.text='Upload document!'
        return super().on_enter(*args)
    
    def close(self):
        self._popup.dismiss()

    def add_graph(self):
        pass

    def show_load(self):
        if self.ids.up.text == 'Upload document!':
            content=LoadDialog(load=self.load,cancel=self.close)
            self._popup = Popup(title="Load file", content=content,size_hint=(0.9, 0.9))
            self._popup.open()

        elif self.ids.up.text=='Create graph!':
            content=NameDialog(create=self.create, cancel=self.close)
            self._popup = Popup(title="Give a name to this graph", content=content,size_hint=(0.9, 0.9))
            self._popup.open()
            
        elif self.ids.up.text=='Select graph':
            pass

    def create(self):
        #with open(graphs[-1][1]) as stream:
                #upload(stream.read())
        self.ids.up.text='Upload document!'
        RV().data.append({'text':str(self.ids.textin.text)})
        print(graphs[-1])
        self.close()

    def load(self, path, filename):
        self.close()
        self.ids.up.text='Create graph!'
        print(os.path.join(path, filename[0]))
        graphs.append([filename[0],os.path.join(path, filename[0])])

class Download(Screen):
    pass

class Edugraph(App):

    def build(self):
        self.width = Window.width
        self.height = Window.height
        global Te, Qs, Gr, Up, do, sm
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='Home'))
        Te=Test(name='Test')
        Qs=Question(name='Question')
        Gr=Graph(name='Graph')
        Up=Upload(name='Upload')
        do=Download(name='Download')
        sm.add_widget(Te)
        sm.add_widget(Qs)
        sm.add_widget(Gr)
        sm.add_widget(Up)
        sm.add_widget(do)
        return sm

#screen 1: Home screen
class HomeScreen(Screen):
    def Redirect(self,screen):
        warn = Popup(title='No graph is selected', content=Label(text='Please select or upload a graph.'), size_hint=(None, None), size=(600, 600))
        global Te,Qs,Gr,Up,do,sm
        if graph == '':
            warn.open()
            Clock.schedule_once(lambda dt: warn.dismiss(),3)
        else:
            if screen == 'Test':
                sm.switch_to(Te)
            elif screen == 'Qs':
                sm.switch_to(Qs)
            elif screen == 'Gr':
                sm.switch_to(Gr)
        if screen == 'Up':
            warn.dismiss()
            sm.switch_to(Up)
        elif screen == 'Do':
            warn.dismiss()
            sm.switch_to(do)

if __name__ == '__main__':
    Edugraph().run()