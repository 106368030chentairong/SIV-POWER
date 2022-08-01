from lib.Autoreport import Autoreport_Runthread
thread_autoreport = Autoreport_Runthread()
thread_autoreport.timestamp = self.timestamp
thread_autoreport.Templatepath = self.lineEdit_template.text()
thread_autoreport.testplan_path = self.lineEdit_testplan.text()
thread_autoreport.start()