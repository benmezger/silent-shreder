# Auto-delete

Deletes specified files from your server when you haven't "pushed" the buttom. 
It works by checking at the `fcheck` entry from the `files` section 
specified at the `config.cfg` file. If that files hasn't been updated in a day 
(can be specified by the user) it will safely remove all files specified at the
`include` entry.
