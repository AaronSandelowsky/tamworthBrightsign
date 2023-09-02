import subprocess

i = 1

while i > 0:
    print(i)
    subprocess.run(["python", "assembly.py"])
    i += 1
