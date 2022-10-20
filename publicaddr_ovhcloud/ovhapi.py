
import ovh

class Client():
    def __init__(self, endpoint, application_key, application_secret, consumer_key):
        """constructor"""
        self.ovhclient = ovh.Client(
                endpoint=endpoint,
                application_key=application_key,
                application_secret=application_secret,
                consumer_key=consumer_key,
            )

    def add_records(self, zone, subdomains, rdata, rtype="A" ):
        """add multiple records or overwrite them"""

        # iter over subdomains to add or overwrite
        for sd in subdomains:
            # searching if subdomain exists
            uri = '/domain/zone/%s/record' % zone
            rr_id = self.ovhclient.get(uri, fieldType=rtype, subDomain=sd)
            
            # updating subdomain with rdata
            if len(rr_id):
                uri = '/domain/zone/%s/record/%s' % (zone, rr_id[0])
                self.ovhclient.put(uri, subDomain=sd, target=rdata)

            # creating subdomain
            else:
                uri = '/domain/zone/%s/record' % zone
                self.ovhclient.post(uri, fieldType=rtype, subDomain=sd, target=rdata)

        # refresh    
        uri = '/domain/zone/%s/refresh' % zone
        self.ovhclient.post(uri)

    def del_records(self, zone, subdomains, rtype="A"):
        """delete multiple records"""
        # iter over subdomains to delete
        for sd in subdomains:
            # searching if subdomain exists
            uri = '/domain/zone/%s/record' % zone
            rr = self.ovhclient.get(uri, fieldType=rtype, subDomain=sd)

            # updating subdomain with rdata
            if len(rr):
                uri = '/domain/zone/%s/record/%s' % (zone, rr[0])
                self.ovhclient.delete(uri)
