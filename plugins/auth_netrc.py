"""
Implement credentials lookup using the ~/.netrc(5) file
"""

from netrc import netrc
import os.path

from ddupdate.ddplugin import AuthPlugin, AuthError

class AuthNetrc(AuthPlugin):
    """ Get credentials stored in the .netrc(5) file
    This is the original storage used before 0.7.0. It is less secure
    than for example the keyring but is convenient and, since it does
    not require anything to be unlocked, a good candidate for servers.
    """
    _name = 'netrc'
    _oneliner = 'Store credentials in .netrc(5)'
    __version__ = '0.7.0'


    def get_auth(self, machine):

        if os.path.exists(os.path.expanduser('~/.netrc')):
            path = os.path.expanduser('~/.netrc')
        elif os.path.exists('/etc/netrc'):
            path = '/etc/netrc'
        else:
            raise AuthError("Cannot locate the netrc file (see manpage).")
        auth = netrc(path).authenticators(machine)
        if not auth:
            raise AuthError("No .netrc data found for " + machine)
        if not auth[2]:
            raise AuthError("No password found for " + machine)
        return auth[0], auth[2]
    

    def set_password(self, machine, username, password):

        def update(lines):
            """ Either update existing line matching machine or add a new """
            line_found = False
            new_lines = []
            for line in lines:
                words = line.split(' ')
                for i in range(0, len(words) - 1):
                    if words[i] == 'machine' and \
                            words[i+1].lower() ==  machine.lower():
                        line_found = True
                if not line_found:
                    new_lines.append(line)
                    continue
                for i in range(0, len(words) - 1):
                    if words[i] == 'password':
                        words[i+1] = password
                    if words[i] == 'login' and username:
                        words[i+1] = username
                new_lines.append(' '.join(words))
            if not line_found:
                line = 'machine ' + machine.lower()
                if username:
                    line += ' login ' + username
                line += ' password ' + password
                new_lines.append(line)
            new_lines = [l.strip() for l in new_lines]
            return '\n'.join(new_lines)

        if os.path.exists(os.path.expanduser('~/.netrc')):
            path = os.path.expanduser('~/.netrc')
        elif os.path.exists('/etc/netrc'):
            path = '/etc/netrc'
        else:
            raise AuthError("Cannot locate the netrc file (see manpage).")
        with open(path, 'r') as f:
            lines = f.readlines()
        lines = update(lines)
        with open(path, 'w') as f:
            f.writelines(lines)
