# Auto-delete

Deletes specified files from your server when you haven't "pushed" the buttom. 
It works by checking at the `fcheck` entry from the `files` section 
specified at the `config.cfg` file. If that files hasn't been updated in a day 
(can be specified by the user) it will safely remove all files specified at the
`include` entry.

**Warning:** This is still a work in progress, do not rely on this for now.

## Installing

1. Make sure change the `config` file for your needs.
2. `pip install -r requirements.txt` to install external Python libraries.
3. Create a .deletion file using `touch`.
4. Run the code with `python auto_delete.py`

## Notes
This is still a work in progress
