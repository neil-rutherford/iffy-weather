Reverse engineering an IoT device for a job application!

This is meant to show my knowledge of programming skills, and it is not meant to actually be run. If run, it will break because:

- The weather API doesn't have a valid token
- ZMQ doesn't have a valid REQ socket to bind to
- Amazon Alexa isn't connected
- The sensors aren't hooked up
- Flask is going to be running on 0.0.0.0, which is non-routable
- I'm using placeholder functions for AC controls (I mean, it won't break, but it won't work like you expect it to)
- Something else that I'm probably not seeing :)

Other than that, enjoy! My write-up is in the cover letter PDF file. I hope it's well-documented enough to follow.

Assuming you're on Linux with sudo permissions, here's how you can get started:
```
chmod +x setup.sh
chmod +x main.py
./setup.sh
./main.py
```
