import front
import logging, wx

# Main function for testing
def main():
    # leventel = logging. + [CRITICAL, ERROR, WARNING, INFO, DEBUGGING]
    logging.basicConfig(format='%(asctime)s %(leventelname)s | %(message)s', level=logging.DEBUG)

    app = wx.App()



    app.MainLoop()

"""
    Sequence is a timeline-like menu where you can order either
    cronologically or in order of aparition each sequence in your
    story. 
"""
class Sequence_editor(object):
    def __init__(self, name:str="Sequence editor", parent:front.Frame=None, 
                        num_rows:int=10, num_columns:int=5, max_scroll_y:float=1000, 
                        max_scroll_x:float=00):
        logging.debug(f"Sequence_editor.__init__(self, {name}, {parent})")
        logging.info(f"New Sequence_editor(object) created.")

        self.name = name
        
        if(parent is None): parent = front.Frame(name=name)

        self._parent = parent

        self.num_rows = num_rows
        self.num_columns = num_columns

        # Cannot []*num_columns since lists are immutables
        self.rows = [([None]*num_columns) for num in range(num_rows)]

        self.panels = []
        self.sequences = {}
        self.num_sequences = 0
        self.panel = self.gui(parent, max_scroll_y=max_scroll_y, max_scroll_x=max_scroll_x)

        """
        nom, llista personatges
        album media, lloc,
        llista converses,
        llista textos,
        llista canvis
        """

    # This creates the graphical part of the sequence editor using
    # front.py
    def gui(self, frame:front.Frame=None, num_rows:int=None, num_columns:int=None, max_scroll_y:float=1000,
                    max_scroll_x:float=0):        
        logging.debug(f"Sequence_editor.gui(self, {frame}, {num_rows}, {num_columns}, {max_scroll_y})")

        if(frame is None): frame = self._parent
        if(num_rows is None): num_rows = self.num_rows
        if(num_columns is None): num_columns = self.num_columns

        panel = frame.new_panel("(_size[0]-@20, _size[1]-@520)","(0,@442)",(50,50,50),(max_scroll_x,max_scroll_y),resizable=False)

        rows = panel.create_multiple(num_rows,panel.new_panel,{"parent":panel, 
                                        "size":f"(_size[0]-@60,@{max_scroll_y/num_rows}+5)",
                                        "location":f"(@10, 10+(@{max_scroll_y/num_rows}+10)"
                                        "*num-self._parent.GetScrollPos(1))", 
                                        "bgcolor":(180,180,180)})
                            
        self.panels = rows

        subpanel = frame.new_panel("(_size[0],@40)", "(0, _size[1]-@79)", (255,255,255))
        subpanel.add_button("[+]", (0,0), "(15+@20,15+@20)", self.create_seqpanel)
        subpanel.add_textbox( "(15+@20,0)","(15+@20,15+@20)", str(num_columns), on_event=self.set_num_columns, 
                                event=wx.EVT_TEXT, multiline=False, style=wx.TE_CENTER)

        return panel

    # Creates a new sequence on button press event
    def create_seqpanel(self, _, start:int=None, sequence:"Sequence"=None, name:str=None) -> None:
        logging.debug(f"Sequence_editor.create_seqpanel(self, {_})")

        del _

        # The +5 is the separation between subpanels; can be found in the size.y
        # parameter when creating the rows list
        if(start is None): start = round(self.panels[0]._parent.GetScrollPos(1)/int(self.panels[0]._size[1]+5))

        for num, sub in enumerate(self.panels[start:]):
            if(self.rows[num][:self.num_columns].count(None)): 
                row = num + start
                position = self.rows[row][:self.num_columns].index(None)
                break
        else: return

        logging.debug(f"New sequence panel created in ({position}, {row})")

        seq = self.panels[row].new_panel(f"(@{self.panels[0]._size[0]/self.num_columns}," 
                                        f"@{self.panels[0]._size[1]})",  #Size
                                    f"(@{self.panels[0]._size[0]/self.num_columns}*{position},0)", # Location
                                    (100,100,100), style=wx.SUNKEN_BORDER)
        self.rows[row][position] = seq
        
        if(name is None): name = f"New sequence{f'.{self.num_sequences}' if self.num_sequences else ''}"
        
        if(sequence is None): self.sequences[seq] = Sequence(self._parent, name, row, position)
        else: self.sequences[seq] = sequence

        seq.Bind(wx.EVT_LEFT_DCLICK, self.sequences[seq].menu_gui)

        #logging.debug(f"self.panels actual state is {self.panels}")

        seq.add_button("[-]", (0,0), f"(@60, @{seq._size[1]}/3)", self.subpanel_delete)
        seq.add_textbox(f"(@60,0)",f"(_size[0]-@60,{seq._size[1]}*3/12)", name, multiline=False)
                            
               
        self.num_sequences += 1

    # Deletes the selected sequence on button press event
    def subpanel_delete(self, event) -> None:
        logging.debug(f"Sequence_editor.subpanel_delete(self, {event})")

        row = self.panels.index(event.GetEventObject().GetParent()._parent)

        logging.info(f"Deleted {event.GetEventObject().GetParent()}")
        logging.debug("located at self.rows"
                    f"[{row}][{self.rows[row].index(event.GetEventObject().GetParent())}]")

        self.rows[row][self.rows[row].index(event.GetEventObject().GetParent()) # Position
                        ] = None

        self.sequences[event.GetEventObject().GetParent()].delete

        del self.sequences[event.GetEventObject().GetParent()]

        event.GetEventObject().GetParent().delete

    # Sets the number of columns per row on modiifed text event
    def set_num_columns(self, event) -> None:
        try: num = int(event.String)
        except: return

        self.num_columns = num

        if(num > len(self.rows[0])):
            difference = num - len(self.rows[0])
            for row in self.rows:
                row.extend([None]*difference)

        for seq_panel, seq in self.sequences.items():
            if(not seq_panel.resizable): continue
            
            seq.resize = seq_panel.check_format(f"(@{self.panels[0]._size[0]/self.num_columns}, @{self.panels[0]._size[1]})",False)
            seq.relocate = seq_panel.check_format(f"(@{self.panels[0]._size[0]/self.num_columns}*{seq.column},0)",False)
            logging.debug(f"{seq_panel.resize}, {seq_panel.relocate}, {self.panels[0]._size}, {self.num_columns}")
            seq_panel.__resize__()


"""
    The Sequence class contains data from every sequence created in the sequence editor
    and handles the edition and drawing of the sequence edition menu
"""
class Sequence(object):
    def __init__(self, parent:front.Frame, name:str, row:int, column:int, size:tuple=None, resizable:bool=True):
        logging.debug(f"Sequence.__init__(self, {parent}, {name}, {row}, {column}, {size}, {resizable})")
        logging.info("New Sequence(object) created.")
        self.name = name
        self.row = row
        self.column = column
        self.size = size
        self.resizable = resizable

        self.warning = None

        self.panels = []

        self._parent = parent
        self._frame = None

        self.__deleted = False

    # This function opens a new window with the gui for advanced sequence
    # editing
    def menu_gui(self, _):

        del _

        self._frame = front.Frame(self._parent, f"Edit sequence - {self.name}", self.size, self.resizable)

        self.panels.append(self._frame.new_panel("(%.5,%1)",(0,0), allow_files_drop=True))
        self.panels[-1].add_image((0,0),self.panels[-1]._size, allow_files_drop=True)

    @property
    def delete(self):
        logging.debug("Sequence.delete(self)")

        if(self.__deleted): return

        self.__deleted = True

        if(self._frame is None): return
        
        self.warning = self._frame.new_panel("(_size[0],10+@30)","(0,_size[1]-@100)", (200,0,0))

        self.warning.add_text("The sequence you were working on has been deleted", (0,0), "(_size[0],_size[1]/2)",
                                bgcolor=(150,0,0), color=(255,255,255)) 
                                #font=wx.Font(1000,wx.FONTFAMILY_SCRIPT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD))

        # Needs a fix
        self.warning.add_button("RESTORE", (50,0), (20,20), on_click=self.restore)

    # Tries to restore the sequence in the sequence editor
    def restore(self):
        if(not self.__deleted): return
        
        self._parent.create_seqpanel(None, self.row, self, self.name)

        self.__deleted = False

        self.warning.delete

        self.warning = None


class Character(object):
    def __init__(self, name):
        self.name = name
        """
        nom, album media,
        llista pensaments,
        inventari, llista textos
        """

class Place(object):
    def __init__(self):
        pass
        """
        nom, propietaris,
        album media, inventari,
        lloc, llista textos
        """

class Relation(object):
    def __init__(self):
        pass
        """
        name,
        from, to
        """


class Action(object):
    def __init__(self):
        pass
        """
        descripcio,
        qui la fa, qui la rep
        """

class Conversation(Action):
    def __init__(self):
        pass
        """
        llista Speak
        """

class Speak(object):
    def __init__(self):
        pass
        """
        text
        """

class Think(object):
    def __init__(self):
        pass
        """
        accio, pensament
        """


class Element(object):
    def __init__():
        pass
        """
        nom, categoria,
        album media
        """


class Text_field(object):
    def __init__(self, name):
        self.name = name
        self.text = ""
        """
        LLegir el que he de fer que es molta merda i no se com es fa
        """

if __name__ == "__main__":
    main()