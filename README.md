# Silent Shreder

Deletes specified files from your server when you haven't "pushed" the buttom.
It works by getting your `sha512` hashes from your `hashes` entry in `files`, and
when the timeout reaches, it will then read revelead hash from your `proves`
file and if it matches, it resets the counter, otherwise it runs your
`executable`.

**Warning:** This is still a work in progress, do not rely on this for now.

## Installing

1. Make sure change the `config` file for your needs.
2. `pip install -r requirements.txt` to install external Python libraries.
3. Create your hash files (make sure you have their revelations stored securely
   somewhere!)
4. Run the program with `python2 auto_delete.py`

## TODO
1. Kill the process after deleting the files
2. Trap kill signals making killing the process harder
3. Implement the clock timer
4. Run it as a UNIX daemon

