# Import modules
import urllib
import urllib2
import json
import sys
import os
import pprint
import arcpy
from datetime import datetime

def get_token(server, port, username, password, expiration=60):
    # Get a token required for Admin changes
    query_dict = {'username':   username,
                  'password':   password,
                  'expiration': str(expiration),
                  'client':     'requestip'}
    
    query_string = urllib.urlencode(query_dict)
    url = "http://{}:{}/arcgis/admin/generateToken?f=json".format(server, port)
   
    try:
        token = json.loads(urllib2.urlopen(url, query_string).read())
        if "token" not in token or token == None:
            print "Failed to get token, return message from server:"
            print token['messages']
            sys.exit()

        else:
            # Return the token to the function which called for it
            return token['token']
    
    except urllib2.URLError, e:
        print "Could not connect to machine {} on port {}".format(server, port)
        print e
        sys.exit()

def toggle_service(server, port, username, password, action, service, token=None):  
    '''
    Function to stop, start or delete a service.
    Requires Admin user/password, as well as server and port (necessary to construct token if one does not exist).
    stopStart = Stop|Start|Delete
    serviceList = List of services. A service must be in the <name>.<type> notation
    If a token exists, you can pass one in for use.  
    '''

    # Get and set the token
    if token is None:       
        token = get_token(server, port, username, password)
        
    # Modify the service
    op_service_url = "http://{}:{}/arcgis/admin/services/{}/{}?token={}&f=json".format(server, port, service, action, token)
    status = urllib2.urlopen(op_service_url, ' ').read()
    
    if 'success' in status:
        success_message = "Action " + action.upper() + " successfully performed on " + service
        log_file.write(success_message)
        log_file.write("\n")
        print success_message

    else: 
        fail_message = "Failed to perform operation. Returned message from the server:"
        log_file.write(fail_message)
        log_file.write("\n")
        log_file.write(status)
        log_file.write("\n")
        print fail_message
        print status
        sys.exit()
    
    return

if __name__ == "__main__":
    server = 'gismaps.brgov.net'
    port = '6080'
    username = 'username'
    password = 'p@$$w0rd'
    pointaddr_service_name = 'TEST_Point_Address_Locator'
    composite_service_name = 'TEST_Composite_Locator'
    service_type = 'GeocodeServer'
    
    # Compose the full name of web service (name form: SERVICE_NAME.ServiceType)
    pointaddr_service = pointaddr_service_name + '.' + service_type
    composite_service = composite_service_name + '.' + service_type

    # Set environment
    service_path = r'//GISMaps/E/WebServices/LocatorServices'
    arcpy.env.workspace = service_path
    arcpy.env.overwriteOutput = True # Overwrite any existing outputs

    # Create a blank log file
    log_file = open('log.txt', 'w')

    # Stop services
    toggle_service(server, port, username, password, 'stop', pointaddr_service, token=None)
    toggle_service(server, port, username, password, 'stop', composite_service, token=None)

    # Rebuild services
    try:
        arcpy.RebuildAddressLocator_geocoding(pointaddr_service_name)
        print "Service " + pointaddr_service_name + " successfully rebuilt"

        arcpy.RebuildAddressLocator_geocoding(composite_service_name)
        print "Service " + composite_service_name + " successfully rebuilt"

        rebuild_message = pointaddr_service_name + " and " + composite_service_name + " successfully rebuilt\n"

    except:
        rebuild_message = pointaddr_service_name + " and " + composite_service_name + " NOT rebuilt, please mannually run the script again to view the detailed error message\n"

    log_file.write(rebuild_message)

    # Restart services
    toggle_service(server, port, username, password, 'start', pointaddr_service, token=None)
    toggle_service(server, port, username, password, 'start', composite_service, token=None)

    # Print success message
    final_message = pointaddr_service_name + " and " + composite_service_name + " successfully refreshed on: " + str(datetime.now())
    log_file.write(final_message)
    print final_message

    log_file.close()
