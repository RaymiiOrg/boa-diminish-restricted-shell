# bdsh - Whitelist Restricted Shell

A shell where you whitelist commands and only those commands can be executed. Either via ssh, as an interactive shell or launched with commands. Logs everything and escapes "dangerous" characters.

bdsh stands for Boa Diminish SHell. You can probably guess why. It might have to to with snakes and restricting users, no pun intended.

##  What is the reason you wrote bdsh?
Sometimes sysadmins are forced to work with insecure systems or badly written applications. Critical systems working with a push model instead of a pull model, things that use ssh and break when stuff changes or users that need to be audit trailed. 

I couldn't find an easy way to set a shell for a user that both logs and is configurable via a whitelist. I tried scripts in `auhorized_keys` but then things `scp` and `sftp` break. bdsh tries to solve that and is fairly successfull in that.

## Requirements

- Python 2.6+
  - Python 3 is supported!

bdsh is tested on Ubuntu, CentOS, OpenSUSE and Debian all with Python 2.7 or above.

## Installation

- Clone the git repo && cd in
- Install bdsh sytemwide
  - `sudo cp bdsh.py /usr/bin/bdsh`
  - `sudo chmod +x /usr/bin/bdsh`
- Edit and place whitelist
  - `vi example_whitelist.conf && sudo cp example_whitelist.conf /etc/bdsh_whitelist.conf`
- Edit `/etc/shells` and add `/usr/bin/bdsh`
- Set the shell for the user, either via:
  - `sudo chsh -s /usr/bin/bdsh $USERNAME`
  - or
  - `vi /etc/passwd`

## Tips

### Enable SFTP/SCP

Put these two lines in the whitelist file:

    scp
    /usr/lib/openssh/sftp-server

Note that you might have to change `scp` to `/usr/bin/scp`.

## Important

bdsh only checks if the command is whitelisted, not the arguments. So if you allow `ls`, you also allow `ls -la`, and `ls -d` and such. 

bdsh is not 100% safe, but it does provide a layer of security.

Read this article about restriced shells: http://pen-testing.sans.org/blog/2012/06/06/escaping-restricted-linux-shells

Don't change the "Dangerous Characters" array, if you for example remove the `&` then you can do something like this: `ssh user@host "ls && perl -e 'exec "/bin/bash"'"`. 

It does try its best to catch restriction-escaping:

    Jun 29 17:41:07 localhost bdsh: [RESTRICTED SHELL]: user "testshell" executed vim
    Jun 29 17:41:11 localhost bdsh: [RESTRICTED SHELL]: user "testshell" NOT allowed for /usr/bin/bdsh -c bash

## See Also

Another way to restrict ssh, written by me: https://github.com/RaymiiOrg/restrict_ssh

