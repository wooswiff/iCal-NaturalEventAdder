import unittest
import datetime
import iCalNaturalEventAdder

class TestICalNaturalEventAdder(unittest.TestCase):

   def setUp(self):
      self.currentDate = datetime.date(2010,3,21)

   def test_event_string_parsing(self):
      event_string_tests = (
         # month and day
         ("My dinner with Andre and guests March 23", "My dinner with Andre and guests",self.currentDate.year,3,23,0,0,0),
         ("My dinner with Andre and guests March 23rd", "My dinner with Andre and guests",self.currentDate.year,3,23,0,0,0),
         ("My dinner with Andre and guests March 23st", "My dinner with Andre and guests",self.currentDate.year,3,23,0,0,0),
         ("My dinner with Andre and guests March 23nd", "My dinner with Andre and guests",self.currentDate.year,3,23,0,0,0),
         ("My dinner with Andre and guests march 23", "My dinner with Andre and guests",self.currentDate.year,3,23,0,0,0),
         ("march 23 My dinner with Andre and guests", "My dinner with Andre and guests",self.currentDate.year,3,23,0,0,0),
         
         # 'next' year
         ("My dinner with Andre and guests January 23", "My dinner with Andre and guests",self.currentDate.year+1,1,23,0,0,0),
         
         # month, day, and year
         # ("My dinner with Andre and guests March 23nd 2012", "My dinner with Andre and guests",2012,3,23,0,0,0),
         
         # times
         ("My dinner with Andre and guests March 23 9am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,0,0),
         ("My dinner with Andre and guests March 23 9 am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,0,0),
         ("My dinner with Andre and guests March 23 9pm", "My dinner with Andre and guests",self.currentDate.year,3,23,21,0,0),
         ("My dinner with Andre and guests March 23 9p", "My dinner with Andre and guests",self.currentDate.year,3,23,21,0,0),
         ("My dinner with Andre and guests March 23 9 p", "My dinner with Andre and guests",self.currentDate.year,3,23,21,0,0),
         ("My dinner with Andre and guests March 23rd at 9pm", "My dinner with Andre and guests",self.currentDate.year,3,23,21,0,0),
         ("My dinner with Andre and guests 9pm March 23", "My dinner with Andre and guests",self.currentDate.year,3,23,21,0,0),
         # ("9pm My dinner with Andre and guests March 23", "My dinner with Andre and guests",self.currentDate.year,3,23,21,0,0),
         # ("9pm March 23 My dinner with Andre and guests", "My dinner with Andre and guests",self.currentDate.year,3,23,21,0,0),
         
         # times with minutes
         ("My dinner with Andre and guests March 23 9:30 p", "My dinner with Andre and guests",self.currentDate.year,3,23,21,30,0),
         ("My dinner with Andre and guests March 23 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         ("My dinner with Andre and guests 9:30am March 23", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         # ("9:30am My dinner with Andre and guests March 23", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         
         # SQL date format
         ("My dinner with Andre and guests 2010/3/23 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         ("My dinner with Andre and guests 2010/03/23 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         ("My dinner with Andre and guests 2010-3-23 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         ("My dinner with Andre and guests 2010-03-23 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         # ("2010-03-23 9:30am My dinner with Andre and guests", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         
         # common date format
         ("My dinner with Andre and guests 3/23/2010 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         ("My dinner with Andre and guests 03/23/2010 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         ("My dinner with Andre and guests 3-23-2010 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         ("My dinner with Andre and guests 03-23-2010 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         # ("03-23-2010 9:30am My dinner with Andre and guests", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         
         # "this year" simple date format
         ("My dinner with Andre and guests 3/23 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         ("My dinner with Andre and guests 03/23 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         ("My dinner with Andre and guests 3-23 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         ("My dinner with Andre and guests 03-23 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         # ("03-23 9:30am My dinner with Andre and guests", "My dinner with Andre and guests",self.currentDate.year,3,23,9,30,0),
         
         # # relative modifiers
         ("My dinner with Andre and guests today", "My dinner with Andre and guests",self.currentDate.year,3,21,0,0,0),
         ("My dinner with Andre and guests today 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,21,9,30,0),
         ("My dinner with Andre and guests tomorrow", "My dinner with Andre and guests",self.currentDate.year,3,22,0,0,0),
         ("My dinner with Andre and guests tomorrow 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,22,9,30,0),
         ("My dinner with Andre and guests wednesday", "My dinner with Andre and guests",self.currentDate.year,3,24,0,0,0),
         ("My dinner with Andre and guests wednesday 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,24,9,30,0),
         ("wednesday My dinner with Andre and guests 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,24,9,30,0),

         # no date and time specified
         ("My dinner with Andre and guests 9:30am", "My dinner with Andre and guests",self.currentDate.year,3,21,9,30,0),
         # ("9:30am My dinner with Andre and guests", "My dinner with Andre and guests",self.currentDate.year,3,21,9,30,0),
         ("My dinner with Andre and guests", "My dinner with Andre and guests",self.currentDate.year,3,21,0,0,0),
         
         # alerts
         ("My dinner with Andre and guests March 24 alert 1 day before", "My dinner with Andre and guests",self.currentDate.year,3,24,0,0,0,(60*24)),
         ("My dinner with Andre and guests March 24 alert 2 days before", "My dinner with Andre and guests",self.currentDate.year,3,24,0,0,0,60*48),
         ("My dinner with Andre and guests March 24 alert 1 week before", "My dinner with Andre and guests",self.currentDate.year,3,24,0,0,0,60*24*7),
         ("My dinner with Andre and guests March 24 alert 2 weeks before", "My dinner with Andre and guests",self.currentDate.year,3,24,0,0,0,60*24*14),
         ("My dinner with Andre and guests March 24 9pm alert 15 minutes before", "My dinner with Andre and guests",self.currentDate.year,3,24,21,0,0,15),
         ("My dinner with Andre and guests March 24 9pm alert 2 hours before", "My dinner with Andre and guests",self.currentDate.year,3,24,21,0,0,60*2),
         # ("March 24 9pm My dinner with Andre and guests alert 2 hours before", "My dinner with Andre and guests",self.currentDate.year,3,24,21,0,0,60*2),
         # ("March 24 9pm alert 2 hours before My dinner with Andre and guests", "My dinner with Andre and guests",self.currentDate.year,3,24,21,0,0,60*2),
      )
      for testCase in event_string_tests:
         newEvent = iCalNaturalEventAdder.parseEventString(testCase[0],self.currentDate)
         checks = [
            (newEvent.eventTitle,testCase[1],"Remaining event string"),
            (newEvent.eventDate.year,testCase[2],"Year"),
            (newEvent.eventDate.month,testCase[3],"Month"),
            (newEvent.eventDate.day,testCase[4],"Day"),
            (newEvent.eventDate.hour,testCase[5],"Hour"),
            (newEvent.eventDate.minute,testCase[6],"Minute"),
            (newEvent.eventDate.second,testCase[7],"Second"),
         ]
         if len(testCase) >= 9:
            checks.append((newEvent.alerts[0].minutesBefore(),testCase[8],"Alert - minutesBefore"),)
         for check in checks:
            self.assertEqual(check[0],check[1], check[2] + " mismatch: got(" + str(check[0]) + "), was hoping for(" + str(check[1]) + ") for string: \"" + testCase[0] + "\"")

if __name__ == '__main__':
   unittest.main()
