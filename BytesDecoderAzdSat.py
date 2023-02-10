import struct
from datetime import datetime
import os




constants = {"message_type": {"1": {"name": "Satellite info",
                                    "struct": '<HBBBfffffB',
                                    "parameters": ["Boot Count",
                                                   "Deployment Status",
                                                   "Arm Deployement Percentage",
                                                   "Expansion Deployement Percentage",
                                                   "OBC Temperature",
                                                   "Bus Voltage",
                                                   "Bus Current",
                                                   "Battery Temperature",
                                                   "Radiation",
                                                   "Checksum"
                                                   ],
                                    },
                              "2": {"name": "Store and forward message", "struct": ''},

                              "3": {"name": "Uplink command response",
                                    "struct": '<BfB',
                                    "parameters": ["Uplink Response",
                                                   "RSSI", "Checksum",
                                                   ],
                                    },

                              "4": {"name": "OBC Sensors health",
                                    "struct": '<2B',
                                    "parameters": ["Sub Systems Health",
                                                   "Checksum",
                                                   ]
                                    },
                              "5": {"name": "Student experiment board data", "struct": '<b8fB'},

                              "6": {"name": "OBC current time",
                                    "struct": '<LB',
                                    "parameters": ["Satellite's Unix Time",
                                                   "Checksum",
                                                   ],
                                    },
                              "7": {"name": "OBC IMU data",
                                    "struct": '<18fB',
                                    "parameters": [
                                        "Accl X",
                                        "Accl Y",
                                        "Accl Z",
                                        "Gyro X",
                                        "Gyro Y",
                                        "Gyro Z",
                                        "Mag X",
                                        "Mag Y",
                                        "Mag Z",
                                        "Linear Accl X",
                                        "Linear Accl Y",
                                        "Linear Accl Z",
                                        "Orient X",
                                        "Orient Y",
                                        "Orient Z",
                                        "Gravity X",
                                        "Gravity Y",
                                        "Gravity Z",
                                        "Checksum",
                                    ]
                                    },
                              "8": {"name": "EEPROM dump", "struct": '<52B'},
                              "9": {"name": "Deployment Status", "struct": ''},
                              "10": {"name": "HMS current data", "struct": '<L5fB', "parameters": ["Recorded At", "Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4", "Sensor 5", "Checksum"]},
                              "11": {"name": "HMS voltage data", "struct": '<L5fB', "parameters": ["Recorded At", "Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4", "Sensor 5", "Checksum"]},
                              "12": {"name": "HMS temperature data", "struct": '<L8fB',
                                     "parameters": ["Recorded On", "Probe 1", "Probe 2", "Probe 3", "Probe 4", "Probe 5", "Probe 6", "Probe 7", "Probe 8", "Checksum"]},
                              "13": {"name": "Radiation data", "struct": '<LfB', "parameters": ["Recorded At", "Sievert", "Checksum"]},
                              },
             "transmitter": {"0": "100mW Transmitter",
                             "1": "1W Transmitter"},
             "uplink_response_codes": {"0": "Success",
                                       "1": "Invalid Command",
                                       "2": "Invalid satellite ID",
                                       "3": "Max length error",
                                       "4": "Invalid arguments",
                                       "5": "Checksum error"
                                       },

             }


def DecodeBytesToMessages(data):
    try:
        headerBytes = data[:9]
        # print(headerBytes)
        # try:
        header = struct.unpack('6c3B', headerBytes)
        # print(header)
        print("--------------------------------------------------")
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("RECEIVED PACKET at "+current_time+"! \n")
        callsign = ""
        checksum = 0

        for i in range(6):
            callsign += header[i].decode()

        if (callsign[0] == ">"):
            return

        frame_number = header[6]
        message_type = header[7]
        frame_number_txt = str(frame_number)
        message_type_txt = "Unknown"
        if (message_type > -1 and message_type < 18):
            message_type_txt = constants["message_type"][str(
                message_type)]["name"]

        transmitter = header[8]
        transmitter_txt = constants["transmitter"][str(transmitter)]

        print("Callsign     : "+callsign)
        print("Message Type : "+message_type_txt)
        print("Transmitter  : "+transmitter_txt)
        print("Frame Number : "+frame_number_txt)

        if (message_type == 2):
            print("")
            messageDataBytes = data[9:]
            messageSlotNumber = messageDataBytes[0]
            sfmSize = messageDataBytes[1]
            sfmbytes = messageDataBytes[2:sfmSize+2]
            sfmStruct = '<'+(sfmSize*'c')
            sfmData = struct.unpack(sfmStruct, sfmbytes)
            sfm = ""

            for val in sfmData:
                sfm += (val).decode("ascii")
            print("Received message from satellite!")
            print("Message Slot Number: "+str(messageSlotNumber))
            print("Message Size: "+str(sfmSize))
            print("Message: "+sfm)
            return
        messageSize = struct.calcsize(
            constants["message_type"][str(message_type)]['struct'])

        checksum = 0
        for i in range(9+messageSize-1):
            x = data[i]
            checksum = checksum ^ x
        messageDataBytes = data[9:messageSize+9]
        print("")
        temp_str = messageDataBytes.hex()

        print("Data Bytes: ", end="")
        for i in range(len(temp_str)):
            print(temp_str[i], end="")
            if ((i+1) % 2 == 0):
                print(" ", end="")
        print("")
        print("")

        messageStruct = struct.unpack(
            constants["message_type"][str(message_type)]['struct'], messageDataBytes)

        if (message_type == 8):
            print("EEPROM Frame Number: "+str(messageStruct[0]))

            eepromDataByte = data[11:60]
            eepromVals = eepromDataByte.hex()

            print("EEPROM Values:")
            print("00 01 02 03 04 05 06 07 08 09")
            print("-----------------------------")
            for i in range(len(eepromVals)):
                print(eepromVals[i], end="")
                if ((i+1) % 2 == 0):
                    print(" ", end="")
                if ((i+1) % 20 == 0):
                    print("")
            print("")

            print("Calculated Checksum: "+str(checksum))
            return

        for i, parameter in enumerate(constants["message_type"][str(message_type)]['parameters']):
            print(parameter+": "+str(messageStruct[i]))
        if (message_type == 3):
            print("Status: " +
                  constants["uplink_response_codes"][str(messageStruct[0])])

        print("Calculated Checksum: "+str(checksum))

    except KeyboardInterrupt:
        os._exit(0)
    except Exception as e:
        print("Error decoding!")
        print(e)


rawData = b'AZDST2\x03\x01\x00\x01\x00\x06\x05\x02\x00\x80\x85A=\nJA\x00\x00\xaaB\x00\x80\x80A\x11\xc7\xba<\xe9'

# if raw data is in hex use the following converter
# rawData = bytes.fromhex('415A445354320301000100060502008085413D0A4A410000AA420080804111C7BA3CE9')
DecodeBytesToMessages(rawData)
