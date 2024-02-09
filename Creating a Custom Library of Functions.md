## Creating our own Library of Functions
 
When you are planning to re-use several functions, you can create your own libraries and import them to Jupyter Notebooks.  We are going to write our functions here in Jupyter lab, then import them.  After we create the functions, we are going to add a couple of files to make the library installable.  You could write the functions in Visual Studio Code, which helps you write the code neat and clean without missing punctuation, however, every time you change the code, you need to restart the kernel and run all the cells again. Trade offs ...

For this lesson, we are going to create functions and explicitly define the arguments passed to the function as parameters in our notebook (Python Review: Slide 36, Automate ..:pg 59).  Later, in another lesson, we will beef up our own functions with the creation of classes and objects. 

After we create our functions, we will be able to import them like any other library and call them like all the other functions and methods we've been using, like <code>string.append()</code>.  For this first round, I've written the PostGIS functions for you; in future lessons you are going to work on writing your own functions to import.

### Converting a Function.py File to an Installable Python Library
A functions.py file was provided to you already (specifically named PostGISFunctions.py) inside a folder called "gis3011lib", which is inside a folder called "gis3011library".  When it comes to naming libraries, its best to stick with either camelCase and not pothole_case, mostly because of how Python converts underscores in library names to dashes, which then come up as illegal characters when importing the library to the notebook. Most often, the main folder and the folder which contains the functions have the same name and normally, you wouldn't include the word "library" in the name of the library, but instead name the library more for what it does like "arcpy" or "numpy". This will be the base of the library. I went ahead and called our library gis3011py, because it seemed fitting. In the next steps, we will take the folders with the functions.py file and convert it into an installable library.
    <table><tbody><tr><td><ol><li>Start by moving the "gis3011py" folder from your Assingment-2-Geopandas folder up a level and save it in your GIS-3011 folder.</li><li>Open the folder and using either VSCode, PyCharm, or Jupyter Lab, add a new Python file, naming it <strong>setup.py</strong></li><ul><li>This is the file that pip will read when it installs the library to the Python environment.</li></ul><li>In the setup.py file, enter the shown code and save.</li></ol>
This bit of code basically says "Use the setup functions built into Python (<code>from distutils.core import setup</code>) to install a library called "gis3011py" (<code>name='gis3011py'</code>), found in a sub-folder called "gis3011py" (<code>packages=['gis3011py']</code>). In order to use this library, the library Psycopg2 must also be installed (<code>install_requires=['psycopg2']</code>). That's it. That's the basic minimums required by Python to install a library (assuming the avaliable files are present). https://docs.python.org/3/distutils/setupscript.html#setup-script
</td><td>
    
```
from distutils.core import setup
setup(
    name='gis3011py',
    version='0.1.0',
    description='Reusable functions for GIS 3011',
    author='Jennifer Muha',
    install_requires=['psycopg2'],
    packages=['gis3011py']
)
```
</td></tr>
<tr><td colspan="2"><ol start="4"><li>Still in the main gis3011py folder, create another new Python file specifically named <strong>__init__.py</strong> and save it - yup, a blank file with that exact name.</li><ul><li>This is the initialization file required by Python to initilize a library of functions before utilizing it in a Python script. It doesn't need to contain anything, but it does tell Python there will be scripts that should be initialized.</li></ul><li>Copy said blank file to the gis3011py subfolder (gis3011py > gis3011py)</li><ul><li>Each folder that has install or functions files needs to have an initilization file.  Other files could exist in a python library folder, however, they don't all need an initilization file.</li><li>Each subfolder - the package folder - is a collection of functions. They can have one big functions.py file, several functions files, or you could do your whole library in one file.  We are going with the plan of one sub-folder (one package) and naming each functions.py file by the name of the function grouping (class). This way, we will later use the command <code>import gis3011py</code> and <code>from gis3011py import PostGISFunctions as postpy</code>. Several approaches to the same end.</ul></ol> 
</td></tr>
    <tr><td><ol start="6"><li>Launch an Anaconda prompt as an administrator</li><li>Activate the gis-3011 environment</li><li>Change the directory to the <em>where ever your GIS-3011 folder is stored</em>/GIS-3011/gis3011py</li><li>Install the library</li><li>Check out the installed package with <code>conda list</code></ol>
</td><td>

```
activate gis-3011
```
```
cd C:\Users\Jennifer\Documents\GIS-3011\gis3011py
 ```
```
pip install -e .
```
```
conda list
```
</td></tr>
<tr><td>The library is now installed (and can be uninstalled with the command <code>pip uninstall gis3011py</code>), but (possibly) if you attempt to import the library to a notebook right now, it will throw a "no such library" (even though there is! We saw it in conda list!).  We need to add the system path to the conda environment so Python knows to look for custom libaries in a custom location (alternatively, we could have saved the library in the default location, but then you'll need to remember that path when/if you add to/change your library!)<ol start="11"><li>Still in the Anacond prompt, run the command <code>conda develop <em>where ever your GIS-3011 folder is stored</em>/GIS-3011/gis3011py</code></li><ul><li>This added a file called "conda.pth" to the path <code>C:\Users\Jennifer\miniconda3\envs\gis-3011\Lib\site-packages</code></li></ul><li>Open the above path via File Explorer, and open the conda.pth file in a text editor. You'll see the added path. You're good to go! If you were ask Python to <code>print(sys.path)</code>, it would print several paths, including the one you just added. Library complete!</li></ol></td><td>

```
mamba install -c conda-forge conda-build
```
 
```
conda develop C:\Users\Jennifer\Documents\GIS-3011\gis3011py
```
</td></tr></tbody></table>
