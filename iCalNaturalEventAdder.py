#!/usr/bin/env python

import os
import sys
import re
import datetime
import wx

from appscript import *

class Event:
   def __init__(self, eventDate, eventTitle, alerts=[], eventCalendar=None, eventLocation=None):
      self.iCal = app('iCal')
      self.eventDate = eventDate
      self.eventTitle = eventTitle
      self.alerts = alerts
      self.eventCalendar = self.iCal.calendars[0].name() if eventCalendar is None else eventCalendar
      self.eventLocation = "" if eventLocation is None else eventLocation
      self.alldayEvent = not eventDate.hasTime()

   def createInIcal(self):
      """Create this event in iCal"""
      newEvent = self.iCal.calendars[self.eventCalendar].make( \
         at=app.calendars[self.eventCalendar].end,
         new=k.event,
         with_properties={ \
            k.start_date: datetime.datetime(self.eventDate.year, self.eventDate.month, self.eventDate.day, self.eventDate.hour, self.eventDate.minute, self.eventDate.second),
            k.location: self.eventLocation, k.allday_event: self.alldayEvent, k.summary: self.eventTitle})
      if len(self.alerts) == 1:
         newEvent.make(at=newEvent.beginning, new=k.display_alarm, with_properties={k.trigger_interval: -self.alerts[0].minutesBefore()} )

   def toString(self):
      """string representation of the event details"""
      eventString = ""
      eventString += "Event Title: " + self.eventTitle + "\n"
      eventString += "Date: " + self.eventDate.dateString() + "\n"
      eventString += "Time: " + self.eventDate.timeString() + "\n"
      eventString += "In Calendar: " + self.eventCalendar + "\n"
      eventString += "Alert: "
      if len(self.alerts) == 1:
         eventString += "%s %s before" % (self.alerts[0].magnitude, self.alerts[0].units)
      else:
         eventString += "none"
      eventString += "\n"
         
      return eventString

class Alert:
   def __init__(self, units='day', magnitude=1):
      # strip trailing characters
      self.magnitude = int(magnitude)
      self.units = units

   def minutesBefore(self):
      """convert the magnitude and units into 'minutes'"""
      unitsMultiplier = {'minute':1,'minutes':1,'hour':60,'hours':60,'day':1440,'days':1440,'week':10080,'weeks':10080}
      multiplier = unitsMultiplier[self.units]
      return self.magnitude * multiplier

class EventDate:
   def __init__(self, year, month, day, hour=0, minute=0, second=0):
      self.year = year
      self.month = month
      self.day = day
      self.hour = hour
      self.minute = minute
      self.second = second
   
   def hasTime(self):
      """whether or not this date has a time component"""
      return self.hour > 0
      
   def dateString(self):
      """string of date"""
      return str(self.month) + "/" + str(self.day) + "/" + str(self.year)

   def timeString(self):
      """string of time"""
      if self.hasTime():
         return "%i:%02i" % (self.hour, self.minute)
      else:
         return "All day"

def stringToEvent(eventString, createForReal = True):
   """parse the event string and save a new event in iCal"""
   new_event = parseEventString(eventString)
   if createForReal: new_event.createInIcal()
   return new_event

def parseEventString(eventString,currentDate = datetime.date.today()):
   """turn a string into a new event object"""
   alerts, eventString = parseAlerts(eventString)
   eventDate, eventString = parseEventDate(eventString,currentDate)
   eventCalendar, eventString = parseEventCalendar(eventString)
   eventTitle = eventString
   new_event=Event(eventDate,eventTitle,alerts,eventCalendar)
   return new_event
   
def parseAlerts(eventString):
   """parse alerts from event string"""
   alerts = []
   alertListPattern = re.compile(r'^(.*) alert (.* before).*$')
   alertPattern = re.compile(r'^\W*(.+) (.+) before.*$')
   matchResult = alertListPattern.search(eventString)
   if matchResult:
      (eventString, alertsString) =  matchResult.groups()
      alerts = [Alert(alertPattern.search(alertString).groups()[1],alertPattern.search(alertString).groups()[0]) for alertString in alertsString.split(',')]
   return alerts, eventString

def parseEventDate(eventString,currentDate = datetime.date.today()):
   """parse the date and time from an event string"""
   # initialize the date to today
   # currentDate = datetime.date.today()
   year = currentDate.year
   month = currentDate.month
   day = currentDate.day
   (hour,minute,seconds) = (0,0,0)
   
   # time - with am/pm
   timePattern = re.compile(r'^(.*) (\d{1,2}):?(\d{2})? ?(am\b|pm\b|a\b|p\b)\b(.*)$', re.IGNORECASE)
   matchResult = timePattern.search(eventString)
   if matchResult and len(matchResult.groups()) == 5:
      (eventStringPre, hourString, minutesString, ampm, eventStringPost) = matchResult.groups()
      hour = int(hourString)
      if minutesString:
         minute = int(minutesString)
      if (ampm == 'p' or ampm == 'pm'):
         hour += 12
      eventStringPre = re.sub(r' *at *$','',eventStringPre) # remove leftover ' at'
      eventString = eventStringPre + eventStringPost
      
   # date - month and day number
   foundDate = False
   monthPattern = re.compile(r'^(.*) ?(january|february|march|april|may|june|july|august|september|october|november|december) (\d+)(?:st|nd|rd|th|\b)(.*)$', re.IGNORECASE)
   matchResult = monthPattern.search(eventString)
   if matchResult and len(matchResult.groups()) == 4:
      foundDate = True
      (eventStringPre, monthString, dayString, eventStringPost) = matchResult.groups()
      newMonth = int(monthIntFromName(monthString))
      if (newMonth < month): year += 1
      month = newMonth
      day = int(dayString)
      eventString = eventStringPre + eventStringPost
   
   # date - YYYY/MM/DD
   if foundDate is False:
      datePattern = re.compile(r'^(.*) ?(\d{4}).(\d{1,2}).(\d{1,2})\b(.*)$', re.IGNORECASE)
      matchResult = datePattern.search(eventString)
      if matchResult and len(matchResult.groups()) == 5:
         foundDate = True
         (eventStringPre, yearString, monthString, dayString, eventStringPost) = matchResult.groups()
         month = int(monthString)
         day = int(dayString)
         eventString = eventStringPre + eventStringPost

   # date - MM/DD/YYYY
   if foundDate is False:
      datePattern = re.compile(r'^(.*) (\d{1,2}).(\d{1,2}).?(\d{4})?\b(.*)$', re.IGNORECASE)
      matchResult = datePattern.search(eventString)
      if matchResult and len(matchResult.groups()) == 5:
         foundDate = True
         (eventStringPre, monthString, dayString, yearString, eventStringPost) = matchResult.groups()
         month = int(monthString)
         day = int(dayString)
         eventString = eventStringPre + eventStringPost

   # date - relative ('today', 'tomorrow', etc.)
   if foundDate is False:
      reldayPattern = re.compile(r'^(.*) (today|tomorrow)\b(.*)$', re.IGNORECASE)
      matchResult = reldayPattern.search(eventString)
      if matchResult and len(matchResult.groups()) == 3:
         foundDate = True
         (eventStringPre, reldayString, eventStringPost) = matchResult.groups()
         if reldayString.lower() == 'today':
            pass
         elif reldayString.lower() == 'tomorrow':
            tomorrowDate = currentDate + datetime.timedelta(days=1)
            year = tomorrowDate.year
            month = tomorrowDate.month
            day = tomorrowDate.day
         eventString = eventStringPre + eventStringPost

   # date - day of week
   if foundDate is False:
      dowPattern = re.compile(r'^(.*) ?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b(.*)$', re.IGNORECASE)
      matchResult = dowPattern.search(eventString)
      if matchResult and len(matchResult.groups()) == 3:
         foundDate = True
         (eventStringPre, dowString, eventStringPost) = matchResult.groups()
         nextDow = getNextDow(currentDate,dowString)
         year = nextDow.year
         month = nextDow.month
         day = nextDow.day

         eventString = eventStringPre + eventStringPost

   eventDate = EventDate(year,month,day,hour,minute,seconds)
   eventString = eventString.replace("  "," ").strip()
   return eventDate, eventString

def parseEventCalendar(eventString):
   """parse the calendar name from event string"""
   calendarName = None

   #TODO: use same 'iCal' object as in the Event class
   iCal = app('iCal')
   
   # default to 'first' calendar
   calendarName = iCal.calendars.get()[0].name()
   
   for c in iCal.calendars.get():
      cName = c.name()
      calnamePattern = re.compile('^(.*) ?in ' + cName + ' ?(.*)$', re.IGNORECASE)
      matchResult = calnamePattern.search(eventString)
      if matchResult and len(matchResult.groups()) == 2:
         (eventStringPre, eventStringPost) = matchResult.groups()
         eventString = eventStringPre + eventStringPost
         calendarName = cName
         break
      
   return calendarName, eventString

def monthIntFromName(monthName):
   """return the int number from month name"""
   months = ('january','february','march','april','may','june','july','august','september','october','november','december')
   return (months.index(monthName.lower())+1)

def getNextDow(currentDate,nextDowString):
   """get a date object for the day-of-week string passed in"""
   nextDowDate = currentDate
   for i in range(7):
      evalDate = currentDate + datetime.timedelta(days=i)
      if evalDate.strftime("%A").lower() == nextDowString.lower():
         nextDowDate = evalDate
         break
   return nextDowDate

class MyApp(wx.App):
    def OnInit(self):
        return True

def openDialogBox(oldDialog=''):
   """open the window for input string"""
   eventString = None
   dlg = wx.TextEntryDialog(None, "Enter the description of your new event", 'New Event', oldDialog)
   if dlg.ShowModal() == wx.ID_OK:
      eventString = dlg.GetValue()
      newEvent = stringToEvent(eventString,False)
      dlgConfirm = wx.MessageDialog(dlg, newEvent.toString() + "\nAre you sure? Click No to edit.", 'Confirm new event', wx.YES_NO | wx.ICON_QUESTION)
      result = dlgConfirm.ShowModal()
      if result == wx.ID_YES:
         pass
      else:
         eventString = openDialogBox(eventString)
      dlgConfirm.Destroy()
   dlg.Destroy()
   return eventString

def getStringFromDialog():
   """open up a dialog box and prompt the user for an event string"""
   eventString = None
   dialogApp = MyApp(0)
   dialogApp.MainLoop()
   eventString = openDialogBox()
   return eventString

if __name__ == "__main__":
   """main driver - called from command line"""
   if len(sys.argv) > 1:
      eventString = sys.argv[1]
   else:
      eventString = getStringFromDialog()
   if eventString: stringToEvent(eventString)
