#!/usr/bin/env python3

from rf95 import RF95, Bw31_25Cr48Sf512

# Example, send two strings and (uncomment to) receive and print a reply
if __name__ == "__main__":
    rf95 = RF95(0, 25, 22)
    if not rf95.init():
        print("RF95 not found")
        rf95.cleanup()
        quit(1)
    else:
        print("RF95 LoRa mode ok")

        # set frequency and power
    rf95.set_frequency(868.5)
    rf95.set_tx_power(5)
        # Custom predefined mode
    #rf95.set_modem_config(Bw31_25Cr48Sf512)

    telemetry_string2 = "$$ASHAB!4331.52N/00540.05WO0/0.020/A=154.3/V=8.12/P=1002.0/TI=21.40/TO=19.83/23-04-2016/19:52:49/GPS=43.525415N,005.667503W/SATS=7/AR=2.3/EA1IDZ test baliza APRS/SSTV ea1idz@ladecadence.net"
    telemetry_string = "$$ASHAB!4331.52N/00540.05WO0/0.020/A=37.2/V=7.64/P=1018.0/TI=29.50/TO=26.94/23-04-2016/19:52:49/GPS=43.525415N,005.667503W/SATS=4/AR=1.5/EA1IDZ test baliza APRS/SSTV ea1idz@ladecadence.net"

    #print("Sending...")
    #rf95.send(rf95.str_to_data(telemetry_string))
    #rf95.wait_packet_sent()
    #print("Sent!")
    #time.sleep(5);
    #rf95.send(rf95.str_to_data(telemetry_string2))
    #rf95.wait_packet_sent()
    #print("Sent!")

    # now wait for reply
        #while not rf95.available():
    #   pass
    #data = rf95.recv()
    #print (data)
    #for i in data:
    #   print(chr(i), end="")
    #print()
    rf95.set_mode_idle()
    rf95.cleanup()
