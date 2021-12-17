# File-Explorer
File Explorer app made with Python
___________________________________________
To bundle executable version of this program:
1. Install pyinstaller package
2. Open this project folder in terminal
3. Run the following command:  
    `pyinstaller --onedir -w main.py --runtime-hook addlib.py`
4. After some minutes, these things will be generated inside the project folder:
   - A file named *main.spec*
   - A folder named *build*
   - A folder named *dist*, which has our *main* program folder inside.
5. Now you can open *dist/main* and run the file *main.exe*
6. To make the program folder tidier:
    - Create a folder name ***lib*** inside *dist/main* (You MUST name this folder ***lib***)
    - Move all the **FILES** (NOT folders) inside *dist/main* into *lib* folder, except:
      - *base_library.zip*
      - *main.exe*
      - *python38.dll*
7. Now you can rename the program folder (*dist/main*) to anything you'd like.
___________________________________________
# Change log:
- 11/07/2021:
  - Added the overall GUI
  - The program doesn't have any functionality yet
- 11/08/2021:
  - The browser can now be refreshed. It can be refreshed manually 
    using the refresh option in File menu, or will be refreshed automatically 
    when the user browses a new directory.
- 11/09/2021:
  - The user can browse directories.
  - Executable files can now be opened from the browser.
- 11/16/2021:
  - The user can now use the search bar to search 
    for items whose name contains the search keyword.
  - The user can now go to a particular directory by using the directory bar.
- 11/17/2021:
  - Recent directories can be accessed from the directory bar's drop down list.
- 12/13/2021:
  - User can now quickly navigate to Local Disk Drives on the PC (Windows only).
  - User can now pin favourite folders to Quick Access.
- 12/14/2021:
  - All options in the menus are now working.
  - Added various keyboard shortcut similar to MS Windows File Explorer.
- 12/15/2021:
  - Added right-click option
- 12/17/2021:
  - The program now comes with executable bundle.