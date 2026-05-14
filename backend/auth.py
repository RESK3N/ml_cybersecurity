from flask_login import UserMixin
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPBindError

# Configuration for testing LDAP server
LDAP_SERVER = 'ldap://ldap.forumsys.com:389'
LDAP_BASE_DN = 'dc=example,dc=com'

class User(UserMixin):
    def __init__(self, username):
        self.id = username

def authenticate_user(username, password):
    """
    Authenticate against OpenLDAP server.
    """
    if not username or not password:
        return False
        
    try:
        # For forumsys, the bind DN is typically uid=<username>,dc=example,dc=com
        user_dn = f"uid={username},{LDAP_BASE_DN}"
        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        
        # If auto_bind succeeds, credentials are valid
        return True
    except LDAPBindError:
        return False
    except Exception as e:
        print(f"LDAP Error: {e}")
        return False
