import cherrypy
import helpers
import homepage
import traceback
import os
import sys
from importlib.machinery import SourceFileLoader

APPS_PATH = '../apps/'
USER_PATH = os.getenv('USER_DIR', '/usbdrive')
APPS_PATH_USER = USER_PATH+'/Web/'

port = 80
try :
    port = int(sys.argv[1])
except:
    pass

print("port: " + str(port))
print("USER_PATH:" +USER_PATH)
print("APPS_PATH_USER:" +APPS_PATH_USER)



# global config
cherrypy.config.update({    'environment': 'production',
                            'log.error_file': '/tmp/site.log',
                            'log.screen': True,
                            'server.socket_host': '0.0.0.0',
                            'server.socket_port': port,
                            'server.max_request_body_size' : 0,  # don't limit file upload size
                            'server.socket_timeout' : 60,
                            'tools.encode.text_only' : False
                        })
# load apps
print("loading apps...")
app_folders = sorted(helpers.get_immediate_subdirectories(APPS_PATH), key=lambda s: s.lower() )
apps = []
for app_folder in app_folders :
    app_name = str(app_folder)
    app_path = APPS_PATH+app_name+'/app.py'
    print('loading: ' + app_path)
    try :
        app = SourceFileLoader(app_name, app_path).load_module()
        cherrypy.tree.mount(app.Root(), app.base, app.config)
        apps.append(app)
    except Exception as e:
        print(traceback.format_exc())

print("loading user apps...")
app_folders = sorted(helpers.get_immediate_subdirectories(APPS_PATH_USER), key=lambda s: s.lower() )
for app_folder in app_folders :
    app_name = str(app_folder)
    app_path = APPS_PATH_USER+app_name+'/app.py'
    print('loading: ' + app_path)
    try :
        app = SourceFileLoader(app_name, app_path).load_module()
        cherrypy.tree.mount(app.Root(), app.base, app.config)
        apps.append(app)
    except Exception as e:
        print(traceback.format_exc())

# load home
cherrypy.tree.mount(homepage.Root(apps), homepage.base, homepage.config)

# start webserver
cherrypy.engine.start()
cherrypy.engine.block()
