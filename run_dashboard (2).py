import glob, os, shutil, subprocess, sys, threading, webbrowser

PORT = 8611  # a fresh port, so an old copy of the app can't get in the way

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def use_newest(name):
    """If Windows saved a download as 'name (1).py', 'name (2).py'..., use the newest one as name.py."""
    files = glob.glob(name + ".py") + glob.glob(name + " (*).py")
    if not files:
        return
    newest = max(files, key=os.path.getmtime)
    if newest != name + ".py":
        shutil.copyfile(newest, name + ".py")


for part in ("app", "models", "sprig"):
    use_newest(part)

threading.Timer(5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.headless", "true", "--server.port", str(PORT)])
