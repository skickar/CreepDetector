import sys
import xml.etree.ElementTree as etree

__author__ = "Michael Caraccio"

if __name__ == '__main__':

    # Check if number of arguments is correct, otherwise print usage
    if len(sys.argv) < 3:
        print("Usage: %s <NetXML File> <Output File Name> <Filter> (Filter is optional)" % sys.argv[0])
        sys.exit(1)

    # Store args
    inputFilename = sys.argv[1]
    outputFilename = str(sys.argv[2])
    mode = sys.argv[3] if len(sys.argv) == 4 is not None else ""

    tree = etree.parse(inputFilename)
    root = tree.getroot()

    # Open csv file (or create it if not exist)
    outfile = open(outputFilename, "w")

    # Create columns in csv
    outfile.write("name,mac address,encryption,lat,lon")

    # For each network
    for child in root:
        if child.tag == "wireless-network":

            essid = ""
            bssid = ""
            encryption = []
            gpslat = ""
            gpslng = ""

            # Parse each network
            for element in child:

                # Get ESSID and Encryption type
                if element.tag == "SSID":
                    for subelement in element:
                        if subelement.tag == "encryption":
                            encryption.append(str(subelement.text))
                        elif subelement.tag == "essid":
                            essid = str(subelement.text)

                # Get MAC Address
                if element.tag == "BSSID":
                    bssid = str(element.text)

                # Get GPS informations
                if element.tag == "gps-info":
                    for gps in element:
                        if gps.tag == "avg-lat":
                            gpslat = str(gps.text)
                        if gps.tag == "avg-lon":
                            gpslng = str(gps.text)

                encryption.sort()

            # Store network to csv file
            # If MODE is not specified
            if mode == "" and essid != "":
                    outfile.write("\n" + essid + "," + bssid + "," + ' '.join(encryption) + "," + gpslat + "," + gpslng)
            elif essid != "" and mode == encryption[0]:
                    outfile.write("\n" + essid + "," + bssid + "," + ' '.join(encryption) + "," + gpslat + "," + gpslng)