## autoeval
A code evaluation program to run and evaluate code using predefined testcases.

# Usage
Windows:
`eval.exe Solution.py`
Ubuntu:
`./eval Solution.py`
MacOS:
`./eval Solution.py`

# Make Execuatbles
Note: You can only create executable for your OS, i.e. the OS you used to compile the executable. 
1) Install requirements
`pip install -r requirements.txt`
2) Make executable
`pyinstaller --onefile eval.py`
3) Check the dist/ folder in same directory to find the executable. 
