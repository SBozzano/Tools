from tkinter import filedialog
import numpy as np
import openpyxl


def find (Stringa, Carattere):
    for Indice in range( len(Stringa)):
        if Stringa[Indice:len(Carattere)+Indice] == Carattere:
            return 1
    return -1

def trasp(Matrix):
    Matrix_temp = []
    for i in range(len(Matrix[0])):
        Matrix_temp.append([])

    for k in range(len(Matrix)-1):
        for j in range(len(Matrix[k])):

            Matrix_temp[j].append(Matrix[k][j])
    return Matrix_temp

Text_intro =     ( '<?xml version="1.0"?>\n'
                  '<configuration template="%APPPATH%\\templates\SoftScope.pct" version="3"><data><softScopeSession>\n'
                  '			<commSettings>Modbus:1,1000,J#COM:4,38400,N,8,1,H</commSettings>\n'
                  '			<target>\n'
                  '				<maxTracks>20</maxTracks>\n'
                  '				<maxSamples>1</maxSamples>\n'
                  '				<sampleTimeBase>125000</sampleTimeBase>\n'
                  '				<targetConfig><AxX_402p1 template="AxX\AxX_402p1\AxX_402p1.pct" version="1"/>\n'
                  '				</targetConfig>\n'
                  '			</target>\n'
                  '			<session>\n'
                  '				<acquisitionId>405</acquisitionId>\n'
                  '				<numSamples>585</numSamples>\n'
                  '				<triggerSource>varILoopIdRef</triggerSource>\n'
                  '				<triggerSlope>1</triggerSlope>\n'
                  '				<triggerValue>99</triggerValue>\n'
                  '				<preTriggerTime>320</preTriggerTime>\n'
                  '				<tracks>\n')
TextCentral =    (  '            </tracks>\n'
                   '				<timePrescaler>1</timePrescaler>\n'
                   '				<PLCSymTab/>\n'
                   '			</session>\n'
                   '			<data>\n'
                   '				<graph hscale="2" triggerpos="40"><tracks>\n')
TextEnd = ( '</tracks></graph>\n'
               '			</data>\n'
               '		</softScopeSession>\n'
               '	</data></configuration>\n')
Text00 ='<track><DictObject name="'
Text01 = '" index="0" subindex="0" type="5" um="V" scale="10" offs="0" shortdescr="" descr="Effective Vu" bitNumber=""><origin deviceid="AxX_402p1"/></DictObject></track>\n'

Text10 = '<track name="'
Text11 ='" um="V" vscale="1" offset="0" color="'
Text12 ='" note="" timeshift="0">\n<samples>\n'
Text13 = '<sample time="'
Text14 ='">'
Text15 ='</sample>\n'
Text16 = '</samples></track>>\n'

ColorString = ['65535', '16776960', '16711935', '65280', '255', '16711680', '16744576', '33023']


#***************************Excel************************************+
ExcelPath = filedialog.askopenfilename(title="Select file", filetypes=(("Excel files", "*.xlsx"),("Excel files", ".xls")))
#ExcelPath = filedialog.askopenfilename(title="Select file", filetypes=(("Text files", "*.txt"),("Text files", ".txt")))
print("Reading Excel file...")

wb = openpyxl.load_workbook(ExcelPath)
sheet = wb.worksheets[0]
allCells =np.array([[cell.value for cell in row] for row in sheet.iter_rows()])
allCells = allCells.T



print("Creating file.SSC...")

fileSSC = open(ExcelPath[:-5] + '.SSC', "w")
fileSSC.write(Text_intro)

for name in range(1 , len(allCells)):
  #  String0 += Text00 + allCells[name][0] + Text01
    fileSSC.write(Text00 + allCells[name][0] + Text01)

fileSSC.write(TextCentral)

for name in range(1 , len(allCells)):
   # String1 += Text10 + allCells[name][0] + Text11 + ColorString[name-1] + Text12
    fileSSC.write(Text10 + allCells[name][0] + Text11 + ColorString[name-1] + Text12)
    for sample in range(1 , len(allCells[0])):
        #String1 += Text13 + str(allCells[0][sample]) + Text14 + str(allCells[name][sample]) + Text15
        fileSSC.write( Text13 + str(allCells[0][sample]) + Text14 + str(allCells[name][sample]) + Text15)
   # String1 += Text16
    fileSSC.write(Text16)

fileSSC.write(TextEnd)
#index = String0
#samples = String1

#file = open("esempio_uno.txt", "w")


#Text_tot = Text_intro + String0 + TextCentral + String1 + TextEnd

# with open(ExcelPath[:-5] + '.SSC', mode='wt', encoding='utf-8') as f:
#     f.write(Text_tot)

fileSSC.close()
#
# #file = open("esempio_uno.txt", "w")
# with open('null.txt') as file:
#     lines = [line.rstrip() for line in file]
#
#     j=0
#     for i in lines:
#         j += 1
#         if find(i,"tracks") == 1:
#             line1 = lines[j]
#             new_line1 = line1 + index
#             lines[j] = new_line1
#             break
#
#     j=0
#     for i in lines:
#         j += 1
#         if find(i,"graph") == 1:
#             line1 = lines[j]
#             new_line1 = line1 + samples
#             lines[j] = new_line1
#             break
#
# with open(ExcelPath[:-5] + '.SSC', mode='wt', encoding='utf-8') as f:
#     f.write('\n'.join(lines))



