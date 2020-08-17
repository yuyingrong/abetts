
# Yuying 20200816
# Update: 

import sqlite3
from tkinter import *
from tkinter import filedialog


# the function below fetches Date based on input TrialNumber

def ComputeLeadLagDates(InDB):
  con=sqlite3.connect(InDB)
  cur=con.cursor()
  # dict of all Dates (Aminal ID: Date1, Date2, Date3, ...)
  d={}
  # dict of Dates after applying ax+b (Aminal ID: Date2, Date6, Date10, ...)
  d1={}
  d2={}
  l=[]

  cur.execute('SELECT DISTINCT ID,Date FROM TS_LD')
  for tup in cur.fetchall():
    if not tup[0] in d:
      d[tup[0]]=[]
    d[tup[0]]+=[tup[1]]
    # the data structure of d： {'Animal ID': [MM/DD/YYYY,MM/DD/YYYY]}

  for ID in d:
    d[ID].sort()
    n=0
    d1[ID]=[]
    d2[ID]=[]
    while n in list(range(len(d[ID])//4)):###############
      try:
        d1[ID].append(d[ID][4*n+2])
        d2[ID].append(d[ID][4*n+4])
        n+=1
        #d[ID]=d[ID][i] for i in ((4n+2) for n in list(range(7)))
      except IndexError:
        break

  cur.close()
  con.close()
  print('Below are Leading/Lagging Dates for each animal:\n')

  return (d1,d2)


# the function below writes a CSV based on the Dates and DB given

def SelectEntryWriteCSV(InDB,OutFile):
  # gets identifiers, Animal IDs and Dates, from the previous function
  (d1,d2)=ComputeLeadLagDates(InDB)

  # creates output CSV
  wr=open(OutFile,'a+')

  # writes header
  wr.write('Date,ID,Type,SessionLength,NumberOfTrial,PercentCorrect,NumberOfReversal,TotalITITouches,TotalBlankTouches,MeanRewardCollectionLatency,MeanCorrectTouchLatency,MeanIncorrectTouchLatency,SessionLengthTo1stReversal,SessionLengthTo2ndReversal,NumberOfTrialTo1stReversal,NumberOfTrialTo2ndReversal,PercentCorrectTo1stReversal,PercentCorrectTo2ndReversal\n')
  # opens DB
  con=sqlite3.connect(InDB)
  cur=con.cursor()

  # using identifiers, here - ID and dates, to search the DB for other parameters
  # and write the parameters with specific modifications to the output CSV

  for d in (d1,d2):
    for ID in d:
      for Date in d[ID]:
        cur.execute('SELECT CorrectPosition,SessionLength,NumberOfTrial,PercentCorrect,NumberOfReversal,TotalITITouches,TotalBlankTouches,MeanRewardCollectionLatency,MeanCorrectTouchLatency,MeanIncorrectTouchLatency,SessionLengthTo1stReversal,SessionLengthTo2ndReversal,NumberOfTrialTo1stReversal,NumberOfTrialTo2ndReversal,PercentCorrectTo1stReversal,PercentCorrectTo2ndReversal FROM TS_LD WHERE Date=? AND ID=?',(Date,ID))
        for tuplerow in cur.fetchall():
          if '7' in tuplerow[0] or '12' in tuplerow[0]:
            wr.write(f'{Date},{ID},hard,{",".join((str(x) for x in tuplerow[1:]))}\n')
          elif '9' in tuplerow[0] or '10' in tuplerow[0]:
            wr.write(f'{Date},{ID},easy,{",".join((str(x) for x in tuplerow[1:]))}\n')
          elif '8' in tuplerow[0] or '11' in tuplerow[0]:
            wr.write(f'{Date},{ID},intermediate,{",".join((str(x) for x in tuplerow[1:]))}\n')
          else:
            wr.write(f'{Date},{ID},undetermined,{",".join((str(x) for x in tuplerow[1:]))}\n')

  wr.close()
  print('Done.')

  cur.close()
  con.close()
  return None



def Run():
  SelectEntryWriteCSV(InDBEntry,OutFileEntry)
  print('Done! Please click Exit to exit.')
  return None



# create UI

root=Tk()
root.title('Make CSV by trial number')

def SelectInFileDB():
  global InDBEntry
  InDBEntry=filedialog.asksaveasfilename(initialfile='/',title='Select a file...',filetypes=(('databank files','*.db'),('all files','*.*')))
  PathLabel=Label(root,text=f'Input DB: {InDBEntry}').pack()
  return None

InDBButton=Button(root,text='Select DB to enter',command=SelectInFileDB).pack()

def SelectOutFile():
  global OutFileEntry
  try:
    OutFileEntry=filedialog.asksaveasfilename(initialfile=InDBEntry,title='Select a file...',filetypes=(('csv files','*.csv'),('all files','*.*')),defaultextension='.csv')
    PathLabel=Label(root,text=f'Output file name: {OutFileEntry}.\nMake sure the above filename has a proper extension!').pack()
    return None
  except NameError:
    print('Please enter the input DB first.')

OutFileButton=Button(root,text='Output file name',command=SelectOutFile).pack()


RunButton=Button(root,text='Run',command=Run).pack()
ExitButton=Button(root,text='Exit',command=root.destroy).pack()

root.mainloop()

print('Task closed.')
