# kapao-wds
### Extraction tool for the Washington Double Star (WDS) Catalog

This tool requires:
 * [NumPy](https://github.com/numpy/numpy)
 * [Astropy](https://github.com/astropy/astropy)
 * [PyGTK](https://github.com/GNOME/pygtk)

These should be able to be installed easily on Lunix/Unix with your typical package manager.
Macs may have some troble with PyGTK. For more detailed dependancy installation instructions, see https://docs.google.com/document/d/1PLanSCL6TMRRJTipLeM3rZKFpSoFwu9hFaUDStEbvcs/edit?usp=sharing

To run the GUI, these files are required to be in the same folder:
 * `WDS_CSV_cat.txt`
 * `WDS_Extraction_Tool.py`
 * `WDS_GUI.py`
 
Download or clone them from here. 
 
Run 
```
python WDS_GUI.py
```

The GUI allows you to constrain the WDS catalog by 
time and date of observation run, 
star separation, 
magnitude of the primary, 
and magnitude difference of the binary.

There are preferences which depends on the telescope which are located in 
`WDS_Preferences.json`. 
This includes telescope latitude, and its viewing range in Dec and HA.
These preferences can be changed in the file, and will be update the next time
the GUI is run.
