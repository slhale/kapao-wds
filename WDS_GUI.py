#!/usr/bin/env python

# example helloworld.py

import pygtk
pygtk.require('2.0')
import gtk
import pango
import WDS_Extraction_Tool as wdsExtractor

class HelloWorld:

    # This is a callback function. The data arguments are ignored
    # in this example. More on callbacks below.
    def hello(self, widget, data=None):
        print "Hello World"
        
    # This is a callback function. 
    # This constrains the WDS table.
    # This ignores inputs and directly accesses the input Entry fields. 
    def constrain(self, widget, data=None):
        # Get the inputs from the user entry fields 
        # time constraints
        startHAInput = float(self.startHAInput.get_text())
        stopHAInput = float(self.stopHAInput.get_text())
        # star contraints
        separationInput = (float(self.upperSeparationInput.get_text()), float(self.lowerSeparationInput.get_text()))
        magnitudeInput = (float(self.upperMagnitudeInput.get_text()), float(self.lowerMagnitudeInput.get_text()))
        deltaMagInput = (float(self.upperDeltaMagInput.get_text()), float(self.lowerDeltaMagInput.get_text()))
        
        # Apply the user inputs as the constraints
        wdsExtractor.setTimeConstraints(startHA=startHAInput, stopHA=stopHAInput)
        wdsExtractor.setStarConstraints(separation=separationInput, magnitude=magnitudeInput, deltaMag=deltaMagInput)
        
        # Constrain the wds table
        wdsExtractor.constrain()
        
        # Display the new wds table
        self.text.set_text(str(wdsExtractor.getWdsInterestingHere()))

    def delete_event(self, widget, event, data=None):
        # If you return FALSE in the "delete_event" signal handler,
        # GTK will emit the "destroy" signal. Returning TRUE means
        # you don't want the window to be destroyed.
        # This is useful for popping up 'are you sure you want to quit?'
        # type dialogs.
        print "delete event occurred"

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    def __init__(self):
        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    
        # When the window is given the "delete_event" signal (this is given
        # by the window manager, usually by the "close" option, or on the
        # titlebar), we ask it to call the delete_event () function
        # as defined above. The data passed to the callback
        # function is NULL and is ignored in the callback function.
        self.window.connect("delete_event", self.delete_event)
    
        # Here we connect the "destroy" event to a signal handler.  
        # This event occurs when we call gtk_widget_destroy() on the window,
        # or if we return FALSE in the "delete_event" callback.
        self.window.connect("destroy", self.destroy)
    
        # Sets the border width of the window.
        self.window.set_border_width(10)
        
        # Make the window always be centered 
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        
        # Make the window visible
        self.window.show()
        
        
        ########### HBOX
        ##### Highest level box
        ##### Left = 'old' WDS extraction tool; Right = Graphing 
        
        # TODO figure out what the best settings for homogenous and spacing are
        # Create an hbox
        self.mainHBox = gtk.HBox(False, True)#(homogeneous, spacing)
        # Add it to the window itself
        self.window.add(self.mainHBox)
        self.mainHBox.show()
        
	    
        ########### VBOX
        ##### Box containing the 'old' WDS extraction tool
        ##### Top = user inputs for constraints; Bottom = resulting WDS table
        
        # Create a vbox
        self.wdsVBox = gtk.VBox(False, True)#(homogeneous, spacing)
	    # Add this vbox to the highest level hbox
        self.mainHBox.pack_start(self.wdsVBox, True, True, False)#, expand, fill, padding)
        self.wdsVBox.show()
        
        ########### BUTTON 
        
        # Creates a new button with the label "Hello World".
#        self.button = gtk.Button("Hello World")
    
        # When the button receives the "clicked" signal, it will call the
        # function hello() passing it None as its argument.  The hello()
        # function is defined above.
#        self.button.connect("clicked", self.hello, None)
    
        # This will cause the window to be destroyed by calling
        # gtk_widget_destroy(window) when "clicked".  Again, the destroy
        # signal could come from here, or the window manager.
#        self.button.connect_object("clicked", gtk.Widget.destroy, self.window)
    
        # This packs the button into the window (a GTK container).
        #self.window.add(self.button)
#        self.vbox.pack_start(self.button, False, False, False)#, expand, fill, padding)
	    
	    
        # The final step is to display this newly created widget.
#        self.button.show()
        
        
        ############# OPTIONS
        
        # Make a table to contain all the input fields 
        self.inputsTable = gtk.Table(rows=7, columns=6, homogeneous=False)
        # Add the inputs table to the wds vbox container 
        self.wdsVBox.pack_start(self.inputsTable, False, True, False)#, expand, fill, padding)
        self.inputsTable.show()
        
        ### Now let's put things into the table
        
        ######## TIME CONSTRAINTS
        
        # Make title for time constraints section 
        self.timeConstrainLabel = gtk.Label("Time constraints:")
        
        # Attach it to the top row of the table
        self.inputsTable.attach(self.timeConstrainLabel, left_attach=0, right_attach=1, top_attach=0, bottom_attach=1)
        self.timeConstrainLabel.show()
        
        
        # Make subtitles for the start and stop hour angle fields
        self.startHALabel = gtk.Label("Start HA")
        self.stopHALabel = gtk.Label("Stop HA")
        
        # Attach them to the 2nd row of the table
        self.inputsTable.attach(self.startHALabel, left_attach=0, right_attach=1, top_attach=1, bottom_attach=2)
        self.startHALabel.show()
        self.inputsTable.attach(self.stopHALabel, left_attach=1, right_attach=2, top_attach=1, bottom_attach=2)
        self.stopHALabel.show()
        
        
        # Make time input fields for the user 
        # They start out with default values 
        self.startHAInput = gtk.Entry()
        self.startHAInput.set_text("180000.0")
        self.stopHAInput = gtk.Entry()
        self.stopHAInput.set_text("240000.0")
        
        # Set the width of the entry fields 
        self.startHAInput.set_width_chars(8)
        
        # Attach them to the 3rd row of the table
        self.inputsTable.attach(self.startHAInput, left_attach=0, right_attach=1, top_attach=2, bottom_attach=3)
        self.startHAInput.show()
        self.inputsTable.attach(self.stopHAInput, left_attach=1, right_attach=2, top_attach=2, bottom_attach=3)
        self.stopHAInput.show()
        
        
        ######## STAR CONSTRAINTS
        
        # Make title for star constraints section 
        self.starConstrainLabel = gtk.Label("Star constraints:")
        
        # Attach it to the 4th row of the table
        self.inputsTable.attach(self.starConstrainLabel, left_attach=0, right_attach=1, top_attach=3, bottom_attach=4)
        self.starConstrainLabel.show()
        
        
        # Make subtitles for the star options
        self.separationLabel = gtk.Label("Separation")
        self.magnitudeLabel = gtk.Label("Magnitude")
        self.deltaMagLabel = gtk.Label("Delta Magnitude")
        
        # Attach them to the 5th row of the table
        self.inputsTable.attach(self.separationLabel, 0, 2, 4, 5)#left_attach, right_attach, top_attach, bottom_attach)
        self.separationLabel.show()
        self.inputsTable.attach(self.magnitudeLabel, 2, 4, 4, 5)#left_attach, right_attach, top_attach, bottom_attach)
        self.magnitudeLabel.show()
        self.inputsTable.attach(self.deltaMagLabel, 4, 6, 4, 5)#left_attach, right_attach, top_attach, bottom_attach)
        self.deltaMagLabel.show()
        
        
        # Make star input fields for the user 
        # They start out with default values 
        self.lowerSeparationInput = gtk.Entry()
        self.lowerSeparationInput.set_text("0.5")
        self.upperSeparationInput = gtk.Entry()
        self.upperSeparationInput.set_text("2.0")
        
        self.lowerMagnitudeInput = gtk.Entry()
        self.lowerMagnitudeInput.set_text("-10.0")
        self.upperMagnitudeInput = gtk.Entry()
        self.upperMagnitudeInput.set_text("7.0")
        
        self.lowerDeltaMagInput = gtk.Entry()
        self.lowerDeltaMagInput.set_text("-2.0")
        self.upperDeltaMagInput = gtk.Entry()
        self.upperDeltaMagInput.set_text("2.0")
        
        # Attach them to the 6th row of the table
        self.inputsTable.attach(self.lowerSeparationInput, left_attach=0, right_attach=1, top_attach=5, bottom_attach=6)
        self.lowerSeparationInput.show()
        self.inputsTable.attach(self.upperSeparationInput, left_attach=1, right_attach=2, top_attach=5, bottom_attach=6)
        self.upperSeparationInput.show()
        self.inputsTable.attach(self.lowerMagnitudeInput, left_attach=2, right_attach=3, top_attach=5, bottom_attach=6)
        self.lowerMagnitudeInput.show()
        self.inputsTable.attach(self.upperMagnitudeInput, left_attach=3, right_attach=4, top_attach=5, bottom_attach=6)
        self.upperMagnitudeInput.show()
        self.inputsTable.attach(self.lowerDeltaMagInput, left_attach=4, right_attach=5, top_attach=5, bottom_attach=6)
        self.lowerDeltaMagInput.show()
        self.inputsTable.attach(self.upperDeltaMagInput, left_attach=5, right_attach=6, top_attach=5, bottom_attach=6)
        self.upperDeltaMagInput.show()
        
        
        ######## DO IT BUTTON
        
        # Make a button to apply the wds table contraints 
        self.constrainButton = gtk.Button("Constrain")
        
        # Attach it to the 7th row of the table
        self.inputsTable.attach(self.constrainButton, left_attach=0, right_attach=1, top_attach=6, bottom_attach=7)
        self.constrainButton.show()
        
        # When the button receives the "clicked" signal, it will call the
        # function constrain() passing it None as its argument.
        self.constrainButton.connect("clicked", self.constrain, None)
        
        
        # TODO Make the textview scrollable 
        ############# TEXTVIEW
        ####### Displays the produced WDS table
        
        ######## TEXTBUFFER
        ## Contains the actual text for the WDS table 
        
        # Make a text buffer, which contains the actual text to 
        # go into the text view
        self.text = gtk.TextBuffer()
        # TODO set the text to be the WDS table, and make it updateable
        self.text.set_text("")
        
        # Make a text view, which is used to view the text buffer 
        # containing the WDS table
        self.textview = gtk.TextView(buffer = self.text)#None)
        
        # Make text uneditable 
        self.textview.set_editable(False)
        
        # Change the font to be monospaced 
        self.textview.modify_font(pango.FontDescription('mono'))
        
        # Add the text to the wds vbox container 
        self.wdsVBox.pack_start(self.textview, True, True, False)#, expand, fill, padding)
        self.textview.show()
        
        
    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    hello = HelloWorld()
    hello.main()

