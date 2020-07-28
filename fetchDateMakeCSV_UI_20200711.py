
# Yuying 20200711
# Updated Date generation method: used to pull from a worksheet, now directly from ABET raw output files

import sqlite3
from tkinter import *
from tkinter import filedialog


# the function below fetches Date based on input TrialNumber

def SelectDatesByTrialNumber(InDB,n):
  print('Below are the Dates when the %d-th trials were recorded:'%(n))
  con=sqlite3.connect(InDB)
  cur=con.cursor()
  d={}
  l=[]

  cur.execute('SELECT DISTINCT ID,Date FROM TSData ORDER BY date(Date) DESC')#if ASC, then ordered by time; if DESC, then ordered by Animal ID - I am not sure why yet; I accidentally wrote DESC during a prev test
  # to the above line, if add LIMIT 8, then only returns to the 8th trial date; 
  for tup in cur.fetchall():
    if not tup[0] in d:
      d[tup[0]]=[]#changed to list so dates could be sorted; if not sorted, would be wrong - not sure why yet; this is also a remnant of previous testing
    d[tup[0]]+=[tup[1]]#changed to list
    # the data structure of d is now {'Animal ID': [MM/DD/YYYY,MM/DD/YYYY]}

  for ID in d:
    d[ID].sort()
    # below prevents less than n number of trial records
    try:
      l.append((ID,d[ID][n-1]))
      print(ID+' '+d[ID][n-1])
      #print(ID+' '+str(len(d[ID])))
    except IndexError:
      print(ID+' has only '+str(len(d[ID]))+' trial records. "NoData" is entered for '+ID+'.')
      l.append('NoData')

  cur.close()
  con.close()
  print('Selecting Dates from raw files done!')

  return l


# the function below writes a CSV based on the Dates and DB given

def SelectEntryWriteCSV(InDB,OutFile,n):
  # gets identifiers, Animal IDs and Dates, from the previous function
  l=SelectDatesByTrialNumber(InDB,n)

  # creates output CSV
  wr=open(OutFile,'a+')

  # writes header
  wr.write('Date,ID,SessionLength,Corrects,Responses,Omissions,BlankTouches,TotalITITouches,MeanCorrectTouchLatency,MeanResponseTouchLatency,MeanBlankTouchLatency,MeanCorrectRewardCollectionLatency,MeanTrayEntryLatency\n')

  # opens DB
  con=sqlite3.connect(InDB)
  cur=con.cursor()

  # using identifiers, here - ID and dates, to search the DB for other parameters
  # and enter the parameters specified below to output CSV

  for pair in l:
    ID=pair[0]
    Date=pair[1]
    if not Date=='NoData':
      cur.execute('SELECT Date,ID,SessionLength,Corrects,Responses,Omissions,BlankTouches,TotalITITouches,MeanCorrectTouchLatency,MeanResponseTouchLatency,MeanBlankTouchLatency,MeanCorrectRewardCollectionLatency,MeanTrayEntryLatency FROM TSData WHERE Date=? AND ID=?',(Date,ID))
      for tuplerow in cur.fetchall():
        for parameter in tuplerow:
          wr.write(str(parameter)+',')
          # if using python 3.6, use the code below; the current code works for python 3.8.3
          '''
          if type(parameter)==unicode:
            wr.write(parameter.encode('utf-8')+',')
          else:
            wr.write(str(parameter)+',')
          '''
        wr.write('\n')
    elif Date=='NoData':
      wr.write('%s,%s,%s\n'%(Date,ID,'NoData,'*11))

  wr.close()
  print('Writing output CSV done!')

  cur.close()
  con.close()
  return None



def Run():
  try:
    TrialNumber=int(e.get())
  except ValueError:
    print('Please enter a valid integer.')
  SelectEntryWriteCSV(InDBEntry,OutFileEntry,TrialNumber)
  print('Done! Please click Exit to exit.')
  return None



# create UI

root=Tk()
root.title('Make CSV by trial number')

# n is the Nth trial, used to grab the Date when the trial was recorded; for extinction intermediate Summer 2020, it was 8
e=Entry(root,width=10,borderwidth=5)
e.pack()
e.insert(0,'Enter n, as in the "n"th trial')

def SelectInFileDB():
  global InDBEntry
  InDBEntry=filedialog.asksaveasfilename(initialfile='/',title='Select a file...',filetypes=(('databank files','*.db'),('all files','*.*')))
  PathLabel=Label(root,text='Input DB: '+InDBEntry).pack()
  return None

InDBButton=Button(root,text='Select DB to enter',command=SelectInFileDB).pack()

def SelectOutFile():
  global OutFileEntry
  try:
    OutFileEntry=filedialog.asksaveasfilename(initialfile=InDBEntry,title='Select a file...',filetypes=(('csv files','*.csv'),('all files','*.*')),defaultextension='.csv')
    PathLabel=Label(root,text='Output file name: '+OutFileEntry+'\nMake sure the above filename has a proper extension!').pack()
    return None
  except NameError:
    print('Please enter the input DB first.')

OutFileButton=Button(root,text='Output file name',command=SelectOutFile).pack()


RunButton=Button(root,text='Run',command=Run).pack()
ExitButton=Button(root,text='Exit',command=root.destroy).pack()

root.mainloop()

print('Task closed.')
