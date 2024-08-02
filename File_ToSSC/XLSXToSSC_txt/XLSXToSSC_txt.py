from tkinter import filedialog
from spire.xls import *
from spire.xls.common import *

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


workbook = Workbook()
workbook.LoadFromFile(ExcelPath)
sheet = workbook.Worksheets[0]

sheet.SaveToFile(ExcelPath[:-5] + '.SSC', '\t', Encoding.get_UTF8())
workbook.Dispose()

data = [[]]
stringData = ''
print("Creating SSC file...")
with open(ExcelPath[:-5] + '.SSC') as file:
    lines = [line.rstrip() for line in file]
    i = 0

    for line in lines:
        for element in range(len(line)):
            if line[element] != '\t' :#and element != line[len(line)-1:] :
                stringData +=  line[element].replace(',','.')
                if element == len(line)-1:
                    data[i].append(stringData)
                    stringData = ''
                    data.append([])
                    i += 1
            elif len(data[i]) < 8:
                data[i].append(stringData)
                stringData = ''
allCells = trasp(data)

print("Writing file.SSC...")

fileSSC = open(ExcelPath[:-5] + '.SSC', "w")
fileSSC.write(Text_intro)

for name in range(1 , len(allCells)):
    fileSSC.write(Text00 + allCells[name][0] + Text01)

fileSSC.write(TextCentral)

for name in range(1 , len(allCells)):
    fileSSC.write(Text10 + allCells[name][0] + Text11 + ColorString[name-1] + Text12)
    for sample in range(1 , len(allCells[0])):
        fileSSC.write( Text13 + str(allCells[0][sample]) + Text14 + str(allCells[name][sample]) + Text15)
    fileSSC.write(Text16)

fileSSC.write(TextEnd)

fileSSC.close()
