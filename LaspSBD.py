import struct

class LaspSBD:
    def __init__(self):
        pass

    def decode(self, msg: bytes)->dict:

        data = dict()
        data['iridium'] = {}
        data['imet'] = {}

        SBD_GPS_ints = struct.unpack_from('>IIHBIIBBH', msg)
        Irid_GPS = [(SBD_GPS_ints[0]/1e6 - 90.0),(SBD_GPS_ints[1]/1e6 - 180.0),SBD_GPS_ints[2],SBD_GPS_ints[3]]
        IMet_GPS = [(SBD_GPS_ints[4]/1e6 - 90.0),(SBD_GPS_ints[5]/1e6 - 180.0)]
        HK = [SBD_GPS_ints[6] - 100.0,SBD_GPS_ints[7]/10.0, SBD_GPS_ints[8]]

        data['iridium']['lat']   = Irid_GPS[0]
        data['iridium']['lon']   = Irid_GPS[1]
        data['iridium']['alt']   = Irid_GPS[2]
        data['imet']['lat']      = IMet_GPS[0]
        data['imet']['lon']      = IMet_GPS[1]
        data['iridium']['intT']  = HK[0]
        data['iridium']['batV']  = HK[1]
        data['iridium']['frame'] = HK[2]

        #print(SBD_GPS_ints)
        #print('Iridium GPS Lat: ' + '{:f}'.format(Irid_GPS[0]) + ', Lon: ' + '{:f}'.format(Irid_GPS[1]) + ', Alt: '+ '{:d}'.format(Irid_GPS[2]))
        #print('iMet GPS Lat: ' + '{:f}'.format(IMet_GPS[0]) + ', Lon: ' + '{:f}'.format(IMet_GPS[1]) + ', Alt: '+ '{:d}'.format(Irid_GPS[2]))
        #print('House Keeping Iridium Modem Internal T: ' + '{:f}'.format(HK[0]) + ', Battery V: ' + '{:f}'.format(HK[1]) + ', Frame #: '+ '{:d}'.format(HK[2]))
        SBD_data = struct.unpack_from('>HHHHHHHHHHHHHHHHBBBHBBHBBHB', msg, offset=22)

        return data


