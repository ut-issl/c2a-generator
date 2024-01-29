import csv
import ntpath
import os

def generate_cmd_csv_for_wings(src_file_path, dest_file_path):
    compo_list = ['CORE', 'CDH', 'POWER', 'COMM', "MISSION", 'Thermal', 'Other', 'Nonorder']
    compo_comut = 0
    dest_line_len = 21
    line_index = 4
    dest_line_max = 1000
    prev_is_none = False

    with open(src_file_path, 'r', encoding='utf-8') as src_file, \
        open(dest_file_path, 'w', encoding='utf-8') as dest_file:
        dest_file.write("""
Component,Name,Target,Code,Params,,,,,,,,,,,,,Danger Flag,Is Restricted,Description,Note
MOBC,,,,Num Params,Param1,,Param2,,Param3,,Param4,,Param5,,Param6,,,,,
Comment,,,,,Type,Description,Type,Description,Type,Description,Type,Description,Type,Description,Type,Description,,,,
*,EXAMPLE,OBC,,2,uint32_t,address,int32_t,time [ms],,,,,,,,,,,例,引数の説明と単位を書くこと！（例：time [ms]）
"""[1:])
        reader = csv.reader(src_file)
        next(reader)

        for row in reader:
            row = [row[i].replace('\n', '##') for i in range(len(row))]
            row = [row[i].replace(',', '@@') for i in range(len(row))]
            if not any(row):
                prev_is_none = True
                dest_file.write(f"**")
                dest_file.write(',' * (dest_line_len-2) + '\n')
                line_index += 1
                continue

            if row[1]:
                num_params = (len(list(filter(None, row[2:15]))) - 1) / 2
                if row[3]:
                    row[3] = 'danger'
                if row[0]:
                    dest_file.write(
f",\
{row[2]},\
{row[1]},\
0x{int(row[0]):04X},\
{int(num_params)},\
{row[4]},\
{row[5]},\
{row[6]},\
{row[7]},\
{row[8]},\
{row[9]},\
{row[10]},\
{row[11]},\
{row[12]},\
{row[13]},\
{row[14]},\
{row[15]},\
{row[3]},\
restricted,\
{row[16]},\
{row[17]}\n")
                else:
                    dest_file.write(
f"*,\
{row[2]},\
{row[1]},\
,\
{int(num_params)},\
{row[4]},\
{row[5]},\
{row[6]},\
{row[7]},\
{row[8]},\
{row[9]},\
{row[10]},\
{row[11]},\
{row[12]},\
{row[13]},\
{row[14]},\
{row[15]},\
{row[3]},\
restricted,\
{row[16]},\
{row[17]}\n")
            else:
                if(prev_is_none or compo_comut==0):
                    dest_file.write(f'*{compo_list[compo_comut]},')
                    compo_comut += 1
                else:
                    dest_file.write('**,')
                dest_file.write(f"{row[2]}")
                dest_file.write(',' * (dest_line_len-2) + '\n')
                
            prev_is_none = False
            line_index += 1
            
        dest_file.write((','*(dest_line_len-1) + '\n') * (dest_line_max - line_index))

def generate_bct_csv_for_wings(src_file_path, dest_file_path):
    prev_row0_is_none = False
    dest_line_len = 12
    dest_line_max = 300
    line_index = 2

    with open(src_file_path, 'r', encoding='utf-8') as src_file, \
        open(dest_file_path, 'w', encoding='utf-8') as dest_file:
        dest_file.write("""
Comment,Name,ShortName,BCID,エイリアス,,,,,Danger Flag,Description,Note
,,,,Deploy,SetBlockPosition,Clear,Activate,Inactivate,,,
"""[1:])
        reader = csv.reader(src_file)
        next(reader)

        for row in reader:
            row = [row[i].replace('\n', '##') for i in range(len(row))]
            row = [row[i].replace(',', '@@') for i in range(len(row))]
            if not any(row):
                continue

            if row[0]:
                num_params = (len(list(filter(None, row[2:15]))) - 1) / 2
                dest_file.write(f',{row[1]},,{row[0]},,,,,,,{row[2]}\n')
                prev_row0_is_none = False
            else:
                if(prev_row0_is_none):
                    dest_file.write(f'*,{row[1]}')
                    dest_file.write(',' * (dest_line_len-2) + '\n')
                else:
                    dest_file.write(f'**,{row[1]}')
                    dest_file.write(',' * (dest_line_len-2) + '\n')
                prev_row0_is_none = True
            line_index += 1
        
        dest_file.write((','*(dest_line_len-1) + '\n') * (dest_line_max - line_index))

def generate_tlm_csv_for_wings(src_dir_path, dest_dir_path, prefix):
    # packet_id 小さい順
    src_path_list = sorted(
        (csv_file for csv_file in src_dir_path.glob('*.csv') if (line := next(csv.reader(csv_file.open()), [None, None]))[1].isdigit()),
        key=lambda x: int(next(csv.reader(x.open()), [None, None])[1])
    )

    for src_path in src_path_list:
        dest_name = prefix + os.path.basename(src_path)
        dest_path = dest_dir_path / dest_name
        generate_tlm_csv_for_wings_(src_path, dest_path)

def generate_tlm_csv_for_wings_(src_file_path, dest_file_path):
    dest_line_len = 18
    dest_line_max = 500
    line_index = 8

    pos = 0
    bit_len = 0
    
    with open(src_file_path, 'r', encoding='utf-8') as src_file, \
        open(dest_file_path, 'w', encoding='utf-8') as dest_file:
        reader = csv.reader(src_file)
        reader = list(reader)

        row0 = reader[0]
        row0 = [row0[i].replace('\n', '##') for i in range(len(row0))]
        row0 = [row0[i].replace(',', '@@') for i in range(len(row0))]
        
        dest_file.write(f',Target,{row0[2]},Local Var')
        dest_file.write(',' * (dest_line_len-4) + '\n')
        dest_file.write(f',PacketID,0x{int(row0[1])},{row0[3]}')
        dest_file.write(',' * (dest_line_len-4) + '\n')
        dest_file.write(f',Enable/Disable,ENABLE')
        dest_file.write(',' * (dest_line_len-3) + '\n')
        dest_file.write(f',IsRestricted, {row0[0]}')
        dest_file.write(',' * (dest_line_len-3) + '\n')
        dest_file.write(',' * (dest_line_len-1) + '\n')
        dest_file.write("""
Comment,TLM Entry,Onboard Software Info.,,Extraction Info.,,,,Conversion Info.,,,,,,,,Description,Note
,Name,Var.%%##Type,Variable or Function Name,Ext.%%##Type,Pos. Desiginator,,,Conv.%%##Type,Poly (ƒ°a_i * x^i),,,,,,Status,,
,,,,,Octet%%##Pos.,bit%%##Pos.,bit%%##Len.,,a0,a1,a2,a3,a4,a5,,,
"""[1:])
                        
        reader = reader[2:]

        for row in reader:
            row = [row[i].replace('\n', '##') for i in range(len(row))]
            row = [row[i].replace(',', '@@') for i in range(len(row))]
            if not any(row):
                line_index += 1
                continue
            if (row[1]):
                if (row[1][0] == '_'):
                    row[1] = row[1][1:]
                    bit_len = int(row[2])
                else:
                    bit_len = type2bit(row[1])
            else:
                bit_len = int(row[2])
            
            pos += bit_len
            octet_pos = int(pos / 8)
            bit_pos = pos % 8

            # if (row[0][-5:] == 'DUMMY'):
            #     dest_file.write('*')

            dest_file.write(
f",\
{row[0]},\
{row[1]},\
{row[3]},\
PACKET,\
{octet_pos},\
{bit_pos},\
{bit_len},\
{row[4]},\
{row[5]},\
{row[6]},\
{row[7]},\
{row[8]},\
{row[9]},\
{row[10]},\
{row[11]},\
{row[12]},\
{row[13]}\n")
            line_index += 1
        dest_file.write((','*(dest_line_len-1) + '\n') * (dest_line_max - line_index))

def type2bit(val_type):
    if (val_type == 'uint8_t'):
        return 8
    if (val_type == 'uint16_t'):
        return 16
    if (val_type == 'uint32_t'):
        return 32
    if (val_type == 'uint64_t'):
        return 64
    if (val_type == 'int8_t'):
        return 8
    if (val_type == 'int16_t'):
        return 16
    if (val_type == 'int32_t'):
        return 32
    if (val_type == 'int64_t'):
        return 64
    if (val_type == 'float'):
        return 32
    if (val_type == 'double'):
        return 64
    print('type: ', val_type)
    raise Exception('Tlm valuable type is invalid')
             