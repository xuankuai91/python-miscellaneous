# Import modules
import urllib
import urllib2
import json
import sys
import os
import arcpy
import pprint

def get_token(server, port, username, password, expiration=60):
	# Get a token required for Admin changes
	query_dict = {'username':   username,
				  'password':   password,
				  'expiration': str(expiration),
				  'client':	 'requestip'}
	
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
		print "Action " + action.upper() + " successfully performed on " + service
	else: 
		print "Failed to perform operation. Returned message from the server:"
		print status
	
	return

if __name__ == "__main__":
	server = 'gismaps.brgov.net'
	port = '6080'
	username = 'username'
	password = 'p@$$w0rd'
	service_name = 'TEST_Point_Address_Locator'
	service_type = 'GeocodeServer'
	
	service = service_name + '.' + service_type

	# Stop services
	toggle_service(server, port, username, password, 'stop', service, token=None)

	# Set environment
	service_path = r'//GISMaps/E/WebServices/LocatorServices'
	arcpy.env.workspace = service_path
	arcpy.env.overwriteOutput = True # Overwrite any existing outputs

	# Rebuild services
	arcpy.RebuildAddressLocator_geocoding(service_name)
	print "Service " + service_name + " successfully rebuilt"

	# Start services
	toggle_service(server, port, username, password, 'start', service, token=None)

	# Create GIS server connection
	connection_file_path = os.path.dirname(os.path.abspath(__file__))
	connection_file = 'GIS_Server_Connection.ags'
	server_url = 'https://gismaps.brgov.net:6443/arcgis/admin'
	arcpy.mapping.CreateGISServerConnectionFile('PUBLISH_GIS_SERVICES', connection_file_path, connection_file, server_url, 'ARCGIS_SERVER', username, password, save_username_password=True)
	print "Connection to " + server_url + " successfully built"

	# Overwrite services
	locator = os.path.join(service_path, service_name)
	sd_draft_file = os.path.join(service_path, service_name + '.sddraft')
	sd_file = os.path.join(service_path, service_name + '.sd')
	server_connection = os.path.join(connection_file_path, 'GIS_Server_Connection')

	analyze_messages = arcpy.CreateGeocodeSDDraft(locator, sd_draft_file, service_name, connection_file_path=server_connection) # Create SD (service definition) draft file
	print "SD draft file " + sd_draft_file +" successfully created"

	if analyze_messages['errors'] == {}:
		try:
			arcpy.server.StageService(sd_draft_file, sd_file) # Convert SD draft file to a SD file 
			arcpy.server.UploadServiceDefinition(sd_file, server_connection) # Publish the SD file as a service
			print "Geocode service successfully published"

		except arcpy.ExecuteError:
			print("An error occurred")
			print(arcpy.GetMessages(2))

	else: 
		# If the sddraft analysis contained errors, display them
		print "Error returned when creating service definition draft"
		pprint.pprint(analyze_messages['errors'], indent=2)
