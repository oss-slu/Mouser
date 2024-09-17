Fixes #213

**What was changed?**

Changes have been made as comments as the fix is not yet functioning. But changes include adding import sys and import os to support dynamic path resolution. The new helper function get_resource_path() was added to dynamically resolve resource paths. The path to the image "shared/images/MouseLogo.png" was changed to use the get_resource_path() function instead of a static path. 

**Why was it changed?**

Adding import sys and import os to support dynamic path resolution for files, both in development and when the program is packaged as an executable. The new helper function was added to resolve resource paths, allowing the program to correctly locate assets whether its running as an executable or from source. The path was updated to use the new helper function instead of a static relative path, ensuring the image can be found regardless of how the program is run. 

**How was it changed?**

The file that was modified was main.py. Two lines were added at the beginning, a new function after the global variables, and a path change towards the end of the file. 
