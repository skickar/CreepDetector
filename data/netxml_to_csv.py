#!/usr/bin/python
from lxml import etree
import os
import sys

def run():
    print "[*] NETXML to CSV Converter by Meatballs"

    if len(sys.argv) != 3:
        print "[*] Usage: %s input output" % sys.argv[0]
    else:
        output_file_name = sys.argv[2]
        input_file_name = sys.argv[1]
        if input_file_name != output_file_name:
            try:
                output = file(output_file_name, 'w')
            except:
                print "[-] Unable to create output file '%s' for writing." % output_file_name
                exit()

            try:
                doc = etree.parse(input_file_name)
            except:
                print "[-] Unable to open input file: '%s'." % input_file_name
                exit()

            print "[+] Parsing '%s'." % input_file_name
            sys.stdout.write("[+] Outputting to '%s' " % output_file_name)
            output.write("BSSID,Channel,Privacy,Ciper,Auth,Power,ESSID,Lat,Lon\n")
            result, clients = parse_net_xml(doc)
            output.write(result)
            output.write("\n")
            output.write("ClientMAC, Power, BSSID, ESSID\n")
            for client_list in clients:
                for client in client_list:
                    output.write("%s,%s,%s,%s\n" % (client[0], client[1], client[2], client[3]))
            sys.stdout.write(" Complete.\r\n")

def parse_net_xml(doc):
    result = ""

    total = len(list(doc.getiterator("wireless-network")))
    tenth = total/10
    count = 0
    clients = list()

    for network in doc.getiterator("wireless-network"):
        count += 1
        if (count % tenth) == 0:
            sys.stdout.write(".")
        type = network.attrib["type"]
        channel = network.find('channel').text
        bssid = network.find('BSSID').text

        if type == "probe" or channel == "0":
            continue

        encryption = network.getiterator('encryption')
        privacy = ""
        cipher = ""
        auth = ""
        if encryption is not None:
            for item in encryption:
                if item.text.startswith("WEP"):
                    privacy = "WEP"
                    cipher = "WEP"
                    auth = ""
                    break
                elif item.text.startswith("WPA"):
                    if item.text.endswith("PSK"):
                        auth = "PSK"
                    elif item.text.endswith("AES-CCM"):
                        cipher = "CCMP " + cipher
                    elif item.text.endswith("TKIP"):
                        cipher += "TKIP "
                elif item.text == "None":
                    privacy = "OPN"

        cipher = cipher.strip()

        if cipher.find("CCMP") > -1:
            privacy = "WPA2"

        if cipher.find("TKIP") > -1:
            privacy += "WPA"


        power = network.find('snr-info')
        dbm = ""
        if power is not None:
            dbm = power.find('max_signal_dbm').text

        if int(dbm) > 1:
            dbm = power.find('last_signal_dbm').text

        if int(dbm) > 1:
            dbm = power.find('min_signal_dbm').text

        ssid = network.find('SSID')
        essid_text = ""
        if ssid is not None:
            essid_text = network.find('SSID').find('essid').text

        gps = network.find('gps-info')
        lat, lon = '', ''
        if gps is not None:
            lat = network.find('gps-info').find('avg-lat').text
            lon = network.find('gps-info').find('avg-lon').text

        # print "%s,%s,%s,%s,%s,%s,%s\n" % (bssid, channel, privacy, cipher, auth, dbm, essid_text)
        result += "%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (bssid, channel, privacy, cipher, auth, dbm, essid_text, lat, lon)

        c_list = associatedClients(network, bssid, essid_text)
        if c_list is not None:
            clients.append(c_list)

    return result, clients

def associatedClients(network, bssid, essid_text):
    clients = network.getiterator('wireless-client')

    if clients is not None:
        client_info = list()
        for client in clients:
            mac = client.find('client-mac')
            if mac is not None:
                client_mac = mac.text
                snr = client.find('snr-info')
                if snr is not None:
                    power = client.find('snr-info').find('max_signal_dbm')
                    if power is not None:
                        client_power = power.text
                        c = client_mac, client_power, bssid, essid_text
                        client_info.append(c)

        return client_info

if __name__ == "__main__":
      run()
