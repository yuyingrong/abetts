
# Yuying 202001007
# Added evaluation to prevent reading empty rows

# Yuying 20200717
# Added more datetime entry options
# Added more annotations; eliminated the usage of [1:-1] to eliminate quotations marks in case the CSV does not have quotation marks around every entry
# Updated Date format to YYYY-MM-DD

import sqlite3
from os import listdir
from datetime import datetime
from tkinter import *
from tkinter import filedialog


# the function enters the contents of all extinction experiment output CSV in a foler into a databank

def EnterRawToDB(InDir,OutFile):

  # creates databank
  con=sqlite3.connect(OutFile)
  cur=con.cursor()

  # creates header with 13 parameters of interest in an extinction experiment
  cur.execute('CREATE TABLE IF NOT EXISTS TSData (Date TEXT,ID TEXT,SessionLength REAL,Corrects REAL,Responses REAL,Omissions REAL,BlankTouches REAL,TotalITITouches REAL,MeanCorrectTouchLatency REAL,MeanResponseTouchLatency REAL,MeanBlankTouchLatency REAL,MeanCorrectRewardCollectionLatency REAL,MeanTrayEntryLatency REAL,UNIQUE(Date,ID,SessionLength))')

  # dumps file content into memory
  for rawsheet in listdir(InDir):
    print(f'Python: working on: {rawsheet}')
    f=open(f'{InDir}/{rawsheet}','r')
    c=f.readlines()
    f.close()
    header=c[0].strip('\n').split(',')

    # indexing parameters based on raw file header names; total 13 parameters
    # if ever the touchscreen company changes its output header names
    # my parameter name predictions may stop working, and so may the script
    # please edit this part of the script accordingly, or contact yuying.rong@gmail.com
    iITITouches=()
    iCorrectTouchLatency=()
    iResponseTouchLatency=()
    iBlankTouchLatency=()
    iCorrectRewardCollectionLatency=()
    iTrayEntryLatency=()

    for i in range(len(header)):
      if 'date' in header[i].lower() or 'schedule_start_time' in header[i].lower():
        iDate=i
        continue
      if 'animal' in header[i].lower() and 'id' in header[i].lower():
        iID=i
        continue
      if 'end summary' in header[i].lower():
        if 'condition' in header[i].lower():
          iSessionLength=i
          continue
        # using 'corrects' here only because it distinguishes from 'correct'; this step may not work if output header name changes
        if 'corrects' in header[i].lower():
          iCorrects=i
          continue
        if 'responses' in header[i].lower():
          iResponses=i
          continue
        if 'omissions' in header[i].lower():
          iOmissions=i
          continue
        if 'blank touches' in header[i].lower():
          iBlankTouches=i
          continue
        if 'iti touches' in header[i].lower():
          iITITouches+=(i,)
          if len(iITITouches)>3:
            print('ERROR: len(iITITouches)>3;should=3 max.')
          continue
      if 'correct touch latency' in header[i].lower():
        iCorrectTouchLatency+=(i,)
        continue
      if 'response touch latency' in header[i].lower():
        iResponseTouchLatency+=(i,)
        continue
      if 'blank touch latency' in header[i].lower():
        iBlankTouchLatency+=(i,)
        continue
      if 'reward collection' in header[i].lower():
        iCorrectRewardCollectionLatency+=(i,)
        continue
      if 'tray entry latency' in header[i].lower():
        iTrayEntryLatency+=(i,)
        
    print('ITITouches has %d entries (should be 3).'%(len(iITITouches)))
    print('CorrectTouchLatency has %d entries.'%(len(iCorrectTouchLatency)))
    print('ResponseTouchLatency has %d entries.'%(len(iResponseTouchLatency)))
    print('BlankTouchLatency has %d entries.'%(len(iBlankTouchLatency)))
    print('CorrectRewardCollectionLatency has %d entries.'%(len(iCorrectRewardCollectionLatency)))
    print('TrayEntryLatency has %d entries.'%(len(iTrayEntryLatency)))

    # entering data to databank
    print('Python: creating databank from: %s.'%(rawsheet))

    count_added=0
    count_original=0
    for row in c[1:]:
      if len(row)<5:
        print(f'Warning: row {count_original} has less than 5 characters. Skip.')
        continue
      row=row.strip('\n').split(',')

      # skips invalid rows
      if str(row[iDate]).strip('"')=='' or str(row[iID]).strip('"')=='':
        count_original+=1
        print('WARNING: original row %d skipped due to empty Date or ID: %s'%(count_original+1,row))
        continue

      #1 enters Date
      if 'T' in str(row[iDate]):
        Date=str(row[iDate]).strip('"').split('T')[0]
      else:
        Date=str(row[iDate]).strip('"').split(' ')[0]
        # for the below code to work, the input date format must be MM/DD/YYYY or MM/DD/YY
        try:
          # in case the format is MM/DD/YYYY
          Date=datetime.strptime(Date,'%m/%d/%Y').strftime('%Y-%m-%d')
        except ValueError:
          # in case the format is MM/DD/YY
          Date=datetime.strptime(Date,'%m/%d/%y').strftime('%Y-%m-%d')
          # if a third datetime format or an invalid format is entered, the following error message will be printed:
          # 'During handling of the above exception, another exception occurred'
   
      #2 enters Animal ID
      ID=str(row[iID]).strip('"')

      #3 enters Session Length
      try:
        SessionLength=float(str(row[iSessionLength]).strip('"'))
      # in case where the Omissions entry has a non numerical value, 0 will be entered
      except ValueError:
        SessionLength=float(0)

      #4 enters number of Corrects
      try:
        Corrects=int(str(row[iCorrects]).strip('"'))
      except ValueError:
        Corrects=float(0)
      # in case, such as in Extinction, where the experiment does not have the Corrects parameter, - will be entered
      except NameError:
        Corrects='-'

      #5 enters number of Responses
      try:
        Responses=int(str(row[iResponses]).strip('"'))
      except ValueError:
        Responses=float(0)
      except NameError:
        Responses='-'
        
      #6 enters number of Omissions
      try:
        Omissions=int(str(row[iOmissions]).strip('"'))
      except ValueError:
        Omissions=float(0)
      except NameError:
        Omissions='-'
        
      #7 enters number of Blank Touches
      try:
        BlankTouches=int(str(row[iBlankTouches]).strip('"'))
      except ValueError:
        BlankTouches=float(0)
        
      #8 calcs and enters the sum of all ITI Touches
      tITITouches=()
      for i in iITITouches:
        try:
          tITITouches+=(int(str(row[i]).strip('"')),)
        except ValueError:
          tITITouches+=0
      TotalITITouches=sum(tITITouches)
      
      #9 calcs and enters the Mean of Correct Touch Latency
      tCorrectTouchLatency=()
      if not iCorrectTouchLatency==():
        for i in iCorrectTouchLatency:
          try:
            tCorrectTouchLatency+=(float(str(row[i]).strip('"')),)
          except ValueError:
            pass
        try:
          MeanCorrectTouchLatency=float(sum(tCorrectTouchLatency)/len(tCorrectTouchLatency))
        # in case where CorrectTouchLatency is 0
        except ZeroDivisionError:
          MeanCorrectTouchLatency='#DIV/0!'
      elif iCorrectTouchLatency==():
        MeanCorrectTouchLatency='-'
        
      #10 calcs and enters the Mean of Response Touch Latency
      tResponseTouchLatency=()
      if not iResponseTouchLatency==():
        for i in iResponseTouchLatency:
          try:
            tResponseTouchLatency+=(float(str(row[i]).strip('"')),)
          except ValueError:
            pass
        try:
          MeanResponseTouchLatency=float(sum(tResponseTouchLatency)/len(tResponseTouchLatency))
        except ZeroDivisionError:
          MeanResponseTouchLatency='#DIV/0!'
      elif iResponseTouchLatency==():
        MeanResponseTouchLatency='-'
        
      #11 calcs and enters the Mean of Blank Touch Latency
      tBlankTouchLatency=()
      for i in iBlankTouchLatency:
        try:
          tBlankTouchLatency+=(float(str(row[i]).strip('"')),)
        except ValueError:
          pass
      try:
        MeanBlankTouchLatency=float(sum(tBlankTouchLatency)/len(tBlankTouchLatency))
      except ZeroDivisionError:
        MeanBlankTouchLatency='#DIV/0!'
        
      #12 calcs and enters the Mean of Correct Reward Collection Latency
      tCorrectRewardCollectionLatency=()
      if not iCorrectRewardCollectionLatency==():
        for i in iCorrectRewardCollectionLatency:
          try:
            tCorrectRewardCollectionLatency+=(float(str(row[i]).strip('"')),)
          except ValueError:
            pass
        try:
          MeanCorrectRewardCollectionLatency=float(sum(tCorrectRewardCollectionLatency)/len(tCorrectRewardCollectionLatency))
        except ZeroDivisionError:
          MeanCorrectRewardCollectionLatency='#DIV/0!'
      elif iCorrectRewardCollectionLatency==():
        MeanCorrectRewardCollectionLatency='-'
        
      #13 calcs and enters the Mean of Tray Entry Latency
        tTrayEntryLatency=()
      if not iTrayEntryLatency==():
        for i in iTrayEntryLatency:
          try:
            tTrayEntryLatency+=(float(str(row[i]).strip('"')),)
          except ValueError:
            pass
        try:
          MeanTrayEntryLatency=float(sum(tTrayEntryLatency)/len(tTrayEntryLatency))
        except ZeroDivisionError:
          MeanTrayEntryLatency='#DIV/0!'
      elif iTrayEntryLatency==():
        MeanTrayEntryLatency='-'
        
      # enters all data to databank; rows with the same Date, ID, and SessionLength are not entered
      cur.execute('INSERT OR IGNORE INTO TSData (Date,ID,SessionLength,Corrects,Responses,Omissions,BlankTouches,TotalITITouches,MeanCorrectTouchLatency,MeanResponseTouchLatency,MeanBlankTouchLatency,MeanCorrectRewardCollectionLatency,MeanTrayEntryLatency) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',(Date,ID,SessionLength,Corrects,Responses,Omissions,BlankTouches,TotalITITouches,MeanCorrectTouchLatency,MeanResponseTouchLatency,MeanBlankTouchLatency,MeanCorrectRewardCollectionLatency,MeanTrayEntryLatency))

      # counts how many rows are read and entered
      count_original+=1
      count_added+=1

    con.commit()
    print('SQLite: read %d rows (duplicates included) for entry (duplicates excluded) to %s.'%(count_added,OutFile))

  cur.close()
  con.close()
  return None


# this function runs the above function

def Run():
  EnterRawToDB(InDirEntry,OutFileEntry)
  print('Done! Please click Exit to exit.')
  return None


# create UI

root=Tk()
root.title('Pool data to DB')

def SelectInDir():
  global InDirEntry
  InDirEntry=filedialog.askdirectory(initialdir='/',title='Select a folder...')
  PathLabel=Label(root,text=f'Merging from folder: {InDirEntry}\nThe date format must be MM/DD/YYYY or MM/DD/YY.').pack()
  return None

InDirButton=Button(root,text='Select folder to enter',command=SelectInDir).pack()

def SelectOutFile():
  global OutFileEntry
  try:
    OutFileEntry=filedialog.asksaveasfilename(initialdir=InDirEntry,title='Select a file...',filetypes=(('databank files','*.db'),('all files','*.*')),defaultextension='.db')
    PathLabel=Label(root,text=f'Output file name: {OutFileEntry}\nMake sure the above filename has a proper extension.').pack()
    return None
  except NameError:
    print('Please enter the input folder first.')

OutFileButton=Button(root,text='Output file name',command=SelectOutFile).pack()

RunButton=Button(root,text='Run',command=Run).pack()
ExitButton=Button(root,text='Exit',command=root.destroy).pack()

root.mainloop()

print('Task closed.')

