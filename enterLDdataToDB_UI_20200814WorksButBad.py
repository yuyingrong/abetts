
# Yuying 20200814
# Working properly, but does not handle expected cols missing from raw data
# Not smart efficiency wise; will optimize when time allows

import sqlite3
from os import listdir
from datetime import datetime
from tkinter import *
from tkinter import filedialog


# the function enters the contents of all LD experiment output CSV in a foler into a databank

def EnterRawToDB(InDir,OutFile):

  # creates databank
  con=sqlite3.connect(OutFile)
  cur=con.cursor()

  # creates header with 18 parameters of interest in LD experiment
  cur.execute('CREATE TABLE IF NOT EXISTS TS_LD (Date TEXT,ID TEXT,SessionLength REAL,NumberOfTrial REAL,PercentCorrect REAL,NumberOfReversal REAL,TotalITITouches REAL,TotalBlankTouches REAL,MeanRewardCollectionLatency REAL,MeanCorrectTouchLatency REAL,MeanIncorrectTouchLatency REAL,SessionLengthTo1stReversal REAL,SessionLengthTo2ndReversal REAL,NumberOfTrialTo1stReversal REAL,NumberOfTrialTo2ndReversal REAL,PercentCorrectTo1stReversal REAL,PercentCorrectTo2ndReversal REAL,CorrectPosition TEXT,UNIQUE(Date,ID,SessionLength))')

  # dumps file content into memory
  for rawsheet in listdir(InDir):
    print(f'Python: working on: {rawsheet}...')
    f=open(InDir+'/'+rawsheet,'r')
    c=f.readlines()
    f.close()
    header=c[0].strip('\n').split(',')

    # indexing parameters based on raw file header names; total 18 parameters
    # if ever the touchscreen company changes its output header names
    # my parameter name predictions may stop working, and so may the script
    # please edit this part of the script accordingly, or contact yuying.rong@gmail.com
    iITITouches=[]
    iBlankTouches=[]
    iRewardCollectionLatency=[]
    iCorrectTouchLatency=[]
    iIncorrectTouchLatency=[]
    iCorrectPosition=[]
    iNumberOfCorrect=[]
    iSessionLengthToReversal=[]
    iNumberOfTrialToReversal=[]

    # vars have been created; now indexing
    for i in range(len(header)):
      if 'date' in header[i].lower():
        iDate=i
        continue
      if 'animal' in header[i].lower() and 'id' in header[i].lower():
        iID=i
        continue

      if 'end summary' in header[i].lower():
        if 'condition' in header[i].lower():
          iSessionLength=i
          continue
        if 'trials completed' in header[i].lower():
          iNumberOfTrial=i
          continue
        if 'percentage correct' in header[i].lower():
          iPercentCorrect=i
          continue
        if 'times criteria reached' in header[i].lower():
          iNumberOfReversal=i
          continue
        if 'iti touches' in header[i].lower():
          iITITouches.append(i)
          continue
        if 'blank' in header[i].lower() or 'top row' in header[i].lower():
          iBlankTouches.append(i)
          continue        

      if 'trial analysis' in header[i].lower():
        if 'reward collection latency' in header[i].lower():
          iRewardCollectionLatency.append(i)
          continue
        if 'correct image response latency' in header[i].lower():
          iCorrectTouchLatency.append(i)
          continue
        if 'incorrect image latency' in header[i].lower():
          iIncorrectTouchLatency.append(i)
          continue
        if 'correct position' in header[i].lower():
          iCorrectPosition.append(i)
          continue
        if 'no. correct' in header[i].lower():
          iNumberOfCorrect.append(i)# this may be a good var to include in the db, consider add?
          continue

      if 'no trials to criterion' in header[i].lower():
        if 'condition' in header[i].lower():
          iSessionLengthToReversal.append(i)
          continue
        if 'generic evaluation' in header[i].lower():
          iNumberOfTrialToReversal.append(i)
          continue

        
    # quality check: if expected number of parameters have been indexed
    print(f'ITITouches has {len(iITITouches)} entries (should be 2).')
    print(f'BlankTouches has {len(iBlankTouches)} entries (should be 3).')
    # ADD ANOTHER QUAL CTRL FOR TOT N TRIALS AND TRIAL ANALYSIS COUNT
    # print(' '.join('Total number of trials recorded:',f'{len(iRewardCollectionLatency)}')


    # entering data to databank
    print(f'Python: Creating databank from: {rawsheet}.')

    # the number of rows added to the databank, excluding empty rows but including duplicate entries
    count_added=0
    # the number of rows read from the raw file, including empty rows
    count_original=0
    
    for row in c[1:]:
      row=row.strip('\n').split(',')

      # eliminates invalid rows
      if str(row[iDate]).strip('"')=='' or str(row[iID]).strip('"')=='':
        count_original+=1
        print('WARNING: original row %d discarded due to empty Date or ID: %s'%(count_original+1,row))
        continue

      #1 enters Date
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
      # if SessionLength has a non numerical value, 'NaN' will be entered
      except ValueError:
        SessionLength='NaN'

      #4 enters Number Of Trial
      try:
        NumberOfTrial=int(str(row[iNumberOfTrial]).strip('"'))
      except ValueError:
        NumberOfTrial='NaN'

      #5 enters Percent Correct
      try:
        PercentCorrect=float(str(row[iPercentCorrect]).strip('"'))
      except ValueError:
        PercentCorrect='NaN'

      #6 enters Number Of Reversal
      try:
        NumberOfReversal=int(str(row[iNumberOfReversal]).strip('"'))
      except ValueError:
        NumberOfReversal='NaN'
      # "NoData" would be writen to the Number Of Reversal column if the raw data lacks this parameter, which should not be the case with LD raw files
      except NameError:
        NumberOfReversal='NoData'
        
      #7 calcs and enters Total ITI Touches
      ###### added isdigit() check ###
      # if any value other than integers exists in the ITI Touches columns, it will not be summed
      try:
        TotalITITouches=sum(int(str(row[i]).strip('"')) for i in iITITouches if str(row[i]).strip('"').isdigit())
      except IndexError:
        print(f'ERROR: Could not calculate and enter Total ITI Touches for row {count_original}, due to indexing errors. Please check back the raw file.')
        TotalITITouches='ERROR'
      
      #8 calcs and enters Total Blank Touches
      # if any value other than integers exists in the ITI Touches columns, it will not be summed
      try:
        TotalBlankTouches=sum(int(str(row[i]).strip('"')) for i in iBlankTouches if str(row[i]).strip('"').isdigit())
      except IndexError:
        print(f'ERROR: Could not calculate and enter Total Blank Touches for row {count_original}, due to indexing errors. Please check back the raw file.')
        TotalBlankTouches='ERROR'
        
      # Cleaning invalid single trial records from Trial Analysis
      
      # First, a single trial record is invalid when CorrectPosition==0
      # The first evaluation: row[iCorrectPosition[i]]==0, does the above
      # Second, need to delete indices of the empty cells at the end of the session for each Animal ID
      # The second evaluation (after OR): row[iCorrectPosition[i]]=='""', takes a big assumption that the end of each of the Trial Analysis have the same empty cells
      # may need to add another quality control step in the future...##########
      iZeroVals=[i for i in range(len(iCorrectPosition)) if (str(row[iCorrectPosition[i]]).strip('"')=='0' or str(row[iCorrectPosition[i]]).strip('"')=='')]

      # No need to subtract len(iZeroVals), or "the Number of Invalid Trial Records", from NumberOfTrial, as ABET II Software has already taken care of it.

      #9 calcs and enters Mean Reward Collection Latency
      # if any value other than positive numbers exists in Reward Collection Latency columns, it will not be summed
      try:
        MeanRewardCollectionLatency=sum(float(str(row[i]).strip('"')) for i in iRewardCollectionLatency if not iRewardCollectionLatency.index(i) in iZeroVals and str(row[i]).strip('"').replace('.','',1).isdigit())/len([i for i in iRewardCollectionLatency if not iRewardCollectionLatency.index(i) in iZeroVals and str(row[i]).strip('"').replace('.','',1).isdigit()])
      except IndexError:
        print(f'ERROR: Could not calculate and enter Mean Reward Collection Latency for row {count_original}, due to indexing errors. Please check back the raw file.')
        MeanRewardCollectionLatency='ERROR'
      # in case CorrectTouchLatency is 0
      except ZeroDivisionError:
        MeanRewardCollectionLatency='#DIV/0!'
        
      #10 calcs and enters Mean Correct Touch Latency
      try:
        MeanCorrectTouchLatency=sum(float(str(row[i]).strip('"')) for i in iCorrectTouchLatency if not iCorrectTouchLatency.index(i) in iZeroVals and str(row[i]).strip('"').replace('.','',1).isdigit())/len([i for i in iCorrectTouchLatency if not iCorrectTouchLatency.index(i) in iZeroVals and str(row[i]).strip('"').replace('.','',1).isdigit()])
      except IndexError:
        print(f'ERROR: Could not calculate and enter Mean Correct Touch Latency for row {count_original}, due to indexing errors. Please check back the raw file.')
        MeanCorrectTouchLatency='ERROR'# in case where CorrectTouchLatency is 0
      except ZeroDivisionError:
        MeanCorrectTouchLatency='#DIV/0!'
        
      #11 calcs and enters the Mean Incorrect Touch Latency
      try:
        MeanIncorrectTouchLatency=sum(float(str(row[i]).strip('"')) for i in iIncorrectTouchLatency if not iIncorrectTouchLatency.index(i) in iZeroVals and str(row[i]).strip('"').replace('.','',1).isdigit())/len([i for i in iIncorrectTouchLatency if not iIncorrectTouchLatency.index(i) in iZeroVals and str(row[i]).strip('"').replace('.','',1).isdigit()])
      except IndexError:
        print(f'ERROR: Could not calculate and enter Mean Correct Touch Latency for row {count_original}, due to indexing errors. Please check back the raw file.')
        MeanIncorrectTouchLatency='ERROR'# in case where CorrectTouchLatency is 0
      except ZeroDivisionError:
        MeanIncorrectTouchLatency='#DIV/0!'
  
      #12 Session Length To 1st Reversal
      if str(row[iSessionLengthToReversal[0]]).strip('"')!='':
        try:
          SessionLengthTo1stReversal=float(str(row[iSessionLengthToReversal[0]]).strip('"'))
        except ValueError:
          SessionLengthTo1stReversal='NaN'
      elif str(row[iSessionLengthToReversal[0]]).strip('"')=='':
        SessionLengthTo1stReversal=0

      #13 Session Length To 2nd Reversal
      if str(row[iSessionLengthToReversal[1]]).strip('"')!='':
        try:
          SessionLengthTo2ndReversal=float(str(row[iSessionLengthToReversal[1]]).strip('"'))
        except ValueError:
          SessionLengthTo2ndReversal='NaN'
      elif str(row[iSessionLengthToReversal[1]]).strip('"')=='':
        SessionLengthTo2ndReversal=0
        
      #14 Number Of Trial To 1st Reversal
      if str(row[iNumberOfTrialToReversal[0]]).strip('"').isnumeric():
        NumberOfTrialTo1stReversal=int(str(row[iNumberOfTrialToReversal[0]]).strip('"'))
      else:
        if str(row[iNumberOfTrialToReversal[0]]).strip('"')=='':
          NumberOfTrialTo1stReversal=0
        else:
          NumberOfTrialTo1stReversal='NaN'

      #15 Number Of Trial To 2nd Reversal
      if str(row[iNumberOfTrialToReversal[1]]).strip('"').isnumeric():
        NumberOfTrialTo2ndReversal=int(str(row[iNumberOfTrialToReversal[1]]).strip('"'))
      else:
        if str(row[iNumberOfTrialToReversal[1]]).strip('"')=='':
          NumberOfTrialTo2ndReversal=0
        else:
          NumberOfTrialTo2ndReversal='NaN'

      #16 Percent Correct To 1st Reversal
      if NumberOfTrialTo1stReversal!=0:
        try:
          PercentCorrectTo1stReversal=float(sum(int(row[i].strip('"')) for i in iNumberOfCorrect[:NumberOfTrialTo1stReversal] if str(row[i]).strip('"').isdigit())/NumberOfTrialTo1stReversal)
        except ValueError:
          PercentCorrectTo1stReversal='NaN'
      elif NumberOfTrialTo1stReversal==0:
        PercentCorrectTo1stReversal=PercentCorrect

      #17 Percent Correct To 2nd Reversal
      if NumberOfTrialTo2ndReversal!=0:
        try:
          PercentCorrectTo2ndReversal=float(sum(int(row[i].strip('"')) for i in iNumberOfCorrect[NumberOfTrialTo1stReversal:sum((NumberOfTrialTo1stReversal,NumberOfTrialTo2ndReversal))] if str(row[i]).strip('"').isdigit())/NumberOfTrialTo2ndReversal)
        except ValueError:
          PercentCorrectTo2ndReversal='NaN'
      elif NumberOfTrialTo2ndReversal==0:
        PercentCorrectTo2ndReversal=0
      
      #18 enters Correct Position as a comma separated string
      CorrectPosition=','.join([str(row[i]).strip('"') for i in iCorrectPosition if not iCorrectPosition.index(i) in iZeroVals and str(row[i]).strip('"').isdigit()])

      # enters all data to databank; rows with the same Date, ID, and SessionLength are not entered
      cur.execute('INSERT OR IGNORE INTO TS_LD (Date,ID,SessionLength,NumberOfTrial,PercentCorrect,NumberOfReversal,TotalITITouches,TotalBlankTouches,MeanRewardCollectionLatency,MeanCorrectTouchLatency,MeanIncorrectTouchLatency,SessionLengthTo1stReversal,SessionLengthTo2ndReversal,NumberOfTrialTo1stReversal,NumberOfTrialTo2ndReversal,PercentCorrectTo1stReversal,PercentCorrectTo2ndReversal,CorrectPosition) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(Date,ID,SessionLength,NumberOfTrial,PercentCorrect,NumberOfReversal,TotalITITouches,TotalBlankTouches,MeanRewardCollectionLatency,MeanCorrectTouchLatency,MeanIncorrectTouchLatency,SessionLengthTo1stReversal,SessionLengthTo2ndReversal,NumberOfTrialTo1stReversal,NumberOfTrialTo2ndReversal,PercentCorrectTo1stReversal,PercentCorrectTo2ndReversal,CorrectPosition))

      # counts how many rows are read and entered
      count_original+=1
      count_added+=1

    con.commit()
    print('SQLite: Read %d valid rows. Entries with the same Date, Animal ID, and Session Length have been removed.\nCreated %s.'%(count_added,OutFile))

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
  InDirEntry=filedialog.askdirectory(initialdir='/',title='Select a file...')
  PathLabel=Label(root,text=f'Merging from folder: {InDirEntry}.\nThe date format must be MM/DD/YYYY or MM/DD/YY.').pack()
  return None

InDirButton=Button(root,text='Select folder to enter',command=SelectInDir).pack()

def SelectOutFile():
  global OutFileEntry
  try:
    OutFileEntry=filedialog.asksaveasfilename(initialdir=InDirEntry,title='Select a file...',filetypes=(('databank files','*.db'),('all files','*.*')),defaultextension='.db')
    PathLabel=Label(root,text=f'Output file name: {OutFileEntry}.\nMake sure the above filename has a proper extension.').pack()
    return None
  except NameError:
    print('Please enter the input folder first.')

OutFileButton=Button(root,text='Output file name',command=SelectOutFile).pack()

RunButton=Button(root,text='Run',command=Run).pack()
ExitButton=Button(root,text='Exit',command=root.destroy).pack()

root.mainloop()

print('Task closed.')

