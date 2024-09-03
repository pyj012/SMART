
import time
CMD_CONTROL=0xC0
STX = 0x02
ETX = 0x03

# def contorol_motor(idList=[],angleList=[]):
#     protocol_arry=[]
#     protocol_arry.append(STX)
#     id_len = len(idList)
#     angle_len= len(angleList)
#     data_len = id_len+angle_len
    
#     length_H = (data_len)// 10 + 0x30
#     length_L = (data_len) % 10 + 0x30
#     protocol_arry.append(length_H)
#     protocol_arry.append(length_L)
#     protocol_arry.append(CMD_CONTROL)
    
#     CRC_SUM = CMD_CONTROL
    
#     for id_num in range(len(idList)):
#         protocol_arry.append(idList[id_num])    
#         CRC_SUM += idList[id_num]
#         place100 = angleList[id_num] // 100 + 48
#         place10  = (angleList[id_num] - (angleList[id_num]//100) * 100) // 10 + 48
#         place1   = angleList[id_num] % 10 + 48
#         protocol_arry.append(place100)
#         protocol_arry.append(place10)
#         protocol_arry.append(place1)
#         CRC_SUM +=place100
#         CRC_SUM +=place10
#         CRC_SUM +=place1

#     CRC_SUM += 0x01
#     CRC_SUM = bin(CRC_SUM)[2:]
#     CRC_H = int(CRC_SUM,2) & 0xff00
#     CRC_H = CRC_H>>8
#     CRC_H = 0xff - CRC_H
#     CRC_L = int(CRC_SUM,2) & 0x00ff
#     protocol_arry.append(CRC_H)
#     protocol_arry.append(CRC_L)
#     protocol_arry.append(ETX)
#     return protocol_arry

def contorol_motor(idList=[],angleList=[]):
    protocol_arry=[hex(STX)]
    id_len = len(idList)
    angle_len= len(angleList)
    data_len = id_len+angle_len
    length_H = hex((data_len)// 10 + 0x30)
    length_L = hex((data_len) % 10 + 0x30)
    protocol_arry.extend([length_H, length_L, hex(CMD_CONTROL)])
    CRC_SUM = CMD_CONTROL
    for id_num in range(len(idList)):
        place100 = angleList[id_num] // 100 + 48
        place10  = (angleList[id_num] - (angleList[id_num]//100) * 100) // 10 + 48
        place1   = angleList[id_num] % 10 + 48
        CRC_SUM += idList[id_num]
        CRC_SUM = CRC_SUM + place100 + place10 + place1
        place100=hex(place100)
        place10= hex(place10)
        place1= hex(place1)
        protocol_arry.append(hex(idList[id_num]))    
        protocol_arry.extend([place100, place10, place1])


    CRC_SUM += 0x01
    CRC_SUM = bin(CRC_SUM)[2:]
    CRC_H = int(CRC_SUM,2) & 0xff00
    CRC_H = CRC_H>>8
    CRC_H = hex(0xff - CRC_H)
    CRC_L = hex(int(CRC_SUM,2) & 0x00ff)

    protocol_arry.extend([CRC_H, CRC_L, hex(ETX)])

    return protocol_arry

if __name__ == "__main__":
    id_list=[0x31, 0x32, 0x33]
    angle_list=[100, 101, 132]
    packet = contorol_motor(id_list, angle_list)
    print(packet)
