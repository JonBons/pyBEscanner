import datetime
import re
import os
import shutil
import pickle
import time
import string

import rcon_modules

import logging


class Scanner:
	def __init__(self, server_settings):

		logger = logging.getLogger(__name__)
		print server_settings["Filters Location"]

		self.server_settings = server_settings

		self.bans = Bans(os.path.join(self.server_settings["BattlEye Directory"], "bans.txt"))
		self.rcon = rcon_modules.Rcon(self.server_settings["ServerIP"], self.server_settings["ServerPort"], self.server_settings["RconPassword"])

		self.ban_list = []
		self.ban_reason = []
		self.kick_list = []
		self.kick_reason = []

		self.backuplog_dir = os.path.join(self.server_settings["BattlEye Directory"], "Logs", datetime.datetime.now().strftime("BattlEye Logs - %Y-%m-%d"))

		self.battleye_logs = {"addbackpackcargo": os.path.join(self.server_settings["BattlEye Directory"], "addbackpackcargo.log"),
							"addmagazinecargo": os.path.join(self.server_settings["BattlEye Directory"], "addmagazinecargo.log"),
							"createvehicle": os.path.join(self.server_settings["BattlEye Directory"], "createvehicle.log"),
							"deletevehicle": os.path.join(self.server_settings["BattlEye Directory"], "deletevehicle.log"),
							"mpeventhandler": os.path.join(self.server_settings["BattlEye Directory"], "mpeventhandler.log"),
							"publicvariable": os.path.join(self.server_settings["BattlEye Directory"], "publicvariable.log"),
							"remoteexec": os.path.join(self.server_settings["BattlEye Directory"], "remoteexec.log"),
							"scripts": os.path.join(self.server_settings["BattlEye Directory"], "scripts.log"),
							"setdamage": os.path.join(self.server_settings["BattlEye Directory"], "setdamage.log"),
							"setpos": os.path.join(self.server_settings["BattlEye Directory"], "setpos.log"),
							"setvariable": os.path.join(self.server_settings["BattlEye Directory"], "setvariable.log")}

		self.temp_logs = {"addbackpackcargo": os.path.join(self.server_settings["Temp Directory"], "addbackpackcargo.log"),
						"addmagazinecargo": os.path.join(self.server_settings["Temp Directory"], "addmagazinecargo.log"),
						"createvehicle": os.path.join(self.server_settings["Temp Directory"], "createvehicle.log"),
						"deletevehicle": os.path.join(self.server_settings["Temp Directory"], "deletevehicle.log"),
						"mpeventhandler": os.path.join(self.server_settings["Temp Directory"], "mpeventhandler.log"),
						"publicvariable": os.path.join(self.server_settings["Temp Directory"], "publicvariable.log"),
						"remoteexec": os.path.join(self.server_settings["Temp Directory"], "remoteexec.log"),
						"scripts": os.path.join(self.server_settings["Temp Directory"], "scripts.log"),
						"setdamage": os.path.join(self.server_settings["Temp Directory"], "setdamage.log"),
						"setpos": os.path.join(self.server_settings["Temp Directory"], "setpos.log"),
						"setvariable": os.path.join(self.server_settings["Temp Directory"], "setvariable.log")}

		self.backup_logs = {"addbackpackcargo": os.path.join(self.backuplog_dir, "addbackpackcargo.log"),
							"addmagazinecargo": os.path.join(self.backuplog_dir, "addmagazinecargo.log"),
							"createvehicle": os.path.join(self.backuplog_dir, "createvehicle.log"),
							"deletevehicle": os.path.join(self.backuplog_dir, "deletevehicle.log"),
							"mpeventhandler": os.path.join(self.backuplog_dir, "mpeventhandler.log"),
							"publicvariable": os.path.join(self.backuplog_dir, "publicvariable.log"),
							"remoteexec": os.path.join(self.backuplog_dir, "remoteexec.log"),
							"scripts": os.path.join(self.backuplog_dir, "scripts.log"),
							"setdamage": os.path.join(self.backuplog_dir, "setdamage.log"),
							"setpos": os.path.join(self.backuplog_dir, "setpos.log"),
							"setvariable": os.path.join(self.backuplog_dir, "setvariable.log")}

		self.banlist_filters = {"addbackpackcargo": os.path.join(self.server_settings["Filters Location"], "addbackpackcargo.banlist"),
								"addmagazinecargo": os.path.join(self.server_settings["Filters Location"], "addmagazinecargo.banlist"),
								"createvehicle": os.path.join(self.server_settings["Filters Location"], "createvehicle.banlist"),
								"deletevehicle": os.path.join(self.server_settings["Filters Location"], "deletevehicle.banlist"),
								"mpeventhandler": os.path.join(self.server_settings["Filters Location"], "mpeventhandler.banlist"),
								"publicvariable": os.path.join(self.server_settings["Filters Location"], "publicvariable.banlist"),
								"remoteexec": os.path.join(self.server_settings["Filters Location"], "remoteexec.banlist"),
								"scripts": os.path.join(self.server_settings["Filters Location"], "scripts.banlist"),
								"setdamage": os.path.join(self.server_settings["Filters Location"], "setdamage.banlist"),
								"setpos": os.path.join(self.server_settings["Filters Location"], "setpos.banlist"),
								"setvariable": os.path.join(self.server_settings["Filters Location"], "setvariable.banlist")}

		self.kicklist_filters = {"addbackpackcargo": os.path.join(self.server_settings["Filters Location"], "addbackpackcargo.kicklist"),
								"addmagazinecargo": os.path.join(self.server_settings["Filters Location"], "addmagazinecargo.kicklist"),
								"createvehicle": os.path.join(self.server_settings["Filters Location"], "createvehicle.kicklist"),
								"deletevehicle": os.path.join(self.server_settings["Filters Location"], "deletevehicle.kicklist"),
								"mpeventhandler": os.path.join(self.server_settings["Filters Location"], "mpeventhandler.kicklist"),
								"publicvariable": os.path.join(self.server_settings["Filters Location"], "publicvariable.kicklist"),
								"remoteexec": os.path.join(self.server_settings["Filters Location"], "remoteexec.kicklist"),
								"scripts": os.path.join(self.server_settings["Filters Location"], "scripts.kicklist"),
								"setdamage": os.path.join(self.server_settings["Filters Location"], "setdamage.kicklist"),
								"setpos": os.path.join(self.server_settings["Filters Location"], "setpos.kicklist"),
								"setvariable": os.path.join(self.server_settings["Filters Location"], "setvariable.kicklist")}

		self.whitelist_filters = {"addbackpackcargo": os.path.join(self.server_settings["Filters Location"], "addbackpackcargo.whitelist"),
								"addmagazinecargo": os.path.join(self.server_settings["Filters Location"], "addmagazinecargo.whitelist"),
								"createvehicle": os.path.join(self.server_settings["Filters Location"], "createvehicle.whitelist"),
								"deletevehicle": os.path.join(self.server_settings["Filters Location"], "deletevehicle.whitelist"),
								"mpeventhandler": os.path.join(self.server_settings["Filters Location"], "mpeventhandler.whitelist"),
								"publicvariable": os.path.join(self.server_settings["Filters Location"], "publicvariable.whitelist"),
								"remoteexec": os.path.join(self.server_settings["Filters Location"], "remoteexec.whitelist"),
								"scripts": os.path.join(self.server_settings["Filters Location"], "scripts.whitelist"),
								"setdamage": os.path.join(self.server_settings["Filters Location"], "setdamage.whitelist"),
								"setpos": os.path.join(self.server_settings["Filters Location"], "setpos.whitelist"),
								"setvariable": os.path.join(self.server_settings["Filters Location"], "setvariable.whitelist")}

		# Create Backup Folder if it doesnt exist
		if not os.path.exists(self.backuplog_dir):
			os.makedirs(self.backuplog_dir)

		if not os.path.exists(os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner")):
			os.mkdir(os.path.join(self.server_settings["BattlEye Directory"], "pyBEscanner"))

		if not os.path.exists(self.server_settings["Filters Location"]):
			os.mkdir(self.server_settings["Filters Location"])

		if not os.path.exists(self.server_settings["Temp Directory"]):
			os.mkdir(self.server_settings["Temp Directory"])

	def scan_battleye_logs(self, x):

		self.log_scanner.scan_log(self.temp_logs[x], self.backup_logs[x], self.whitelist_filters[x], self.banlist_filters[x], self.kicklist_filters[x])
		if self.server_settings[x] == "off":
			print x + " (off)"
		else:
			if self.server_settings[x] == "strict":
				# Strict Scanning
				print x + " (strict)"
				self.update_bans(x, self.log_scanner.banlist)
				self.update_bans(x, self.log_scanner.kicklist)
				self.update_bans(x, self.log_scanner.unknownlist, update=True)

				# Logging
				self.log(x, "bans", self.log_scanner.banlist)
				self.log(x, "kicks", self.log_scanner.kicklist)
				self.log(x, "unknown", self.log_scanner.unknownlist)

			elif self.server_settings[x] == "standard+kick":
				# Standard Scanning + Kicking
				print x + " (standard+kick)"
				self.update_bans(x, self.log_scanner.banlist, update=True)
				self.update_kicks(x, self.log_scanner.kicklist)
				self.update_kicks(x, self.log_scanner.unknownlist)

				# Logging
				self.log(x, "bans", self.log_scanner.banlist)
				self.log(x, "kicks", self.log_scanner.kicklist)
				self.log(x, "unknown", self.log_scanner.unknownlist)

			elif self.server_settings[x] == "standard":
				# Standard Scanning
				print x + " (standard)"
				self.update_bans(x, self.log_scanner.banlist, update=True)
				self.update_kicks(x, self.log_scanner.kicklist)

				# Logging
				self.log(x, "bans", self.log_scanner.banlist)
				self.log(x, "kicks", self.log_scanner.kicklist)
				self.log(x, "unknown", self.log_scanner.unknownlist)

			else:
				print x + " (unknown option)"

	def kick_ban_msg(self, template, player_name, server_name, log_file, date_time):
		tmp = string.replace(template, "PLAYER_NAME", player_name)
		tmp = string.replace(tmp, "SERVER_NAME", server_name)
		tmp = string.replace(tmp, "LOG_FILE", log_file)
		tmp = string.replace(tmp, "DATE_TIME", date_time)
		return tmp

	def update_bans(self, log_file, data, time="-1", update=False):

		for x in range(len(data["guid"])):
			if self.ban_list.count(data["guid"][x]) == 0:
				self.ban_list.append(data["guid"][x])
				ban_message = self.kick_ban_msg(self.server_settings["Ban Message"], str(data["name"][x]), str(self.server_settings["ServerName"]), log_file, str(data["date"][x]))
				self.ban_reason.append(ban_message)
				print ("Banning Player " + str(data["name"][x]))

		if update is True:
			if self.ban_list != []:
				self.bans.openfile()
				for x in range(len(self.ban_list)):
					self.bans.addban(self.ban_list[x], time, self.ban_reason[x])
				self.bans.closefile()
				self.ban_list = []
				self.ban_reason = []

	def update_kicks(self, x, data):
		for x in range(len(data["name"])):
			if self.kick_list.count(data["name"]) == 0:
				self.kick_list.append(data["name"])
				self.kick_reason.append("pyBEscanner: " + str(data["name"][x]) + " detected unknown @ " + str(data["date"][x]))

		for x in range(len(self.kick_list)):
			self.rcon.kickplayer(self.kick_list[x])

	def log(self, x, action, data):
		if data["date"] != []:
			f_log = open((os.path.join(self.backuplog_dir, x + "-" + action + ".txt")), "a")
			for x in range(len(data["date"])):
				f_log.write(str(data["date"][x]) + str(data["name"][x]) + "(" + str(data["ip"][x]) + ") " + str(data["guid"][x]) + " - " + str(data["code"][x]) + "\n")
			f_log.close()

	def scan(self):
		battleye_logs = ["addbackpackcargo", "addmagazinecargo", "createvehicle", "deletevehicle", "mpeventhandler", "publicvariable", "remoteexec", "scripts", "setdamage", "setpos", "setvariable"]

		self.log_scanner = Parser(time.time(), float(self.server_settings["OffSet"]))

		for log in battleye_logs:
			if os.path.isfile(self.battleye_logs[log]) is True:
				shutil.move(self.battleye_logs[log], self.temp_logs[log])

		for log in battleye_logs:
			self.scan_battleye_logs(log)  # Scan Logs incase a .pickle file exists, with previous log entry


class Parser:
	def __init__(self, scan_time, offset):
		logger = logging.getLogger(__name__)

		self.scan_time = scan_time
		self.offset = offset

	def scan_log(self, logfile, backupfile, whitelist_filters, banlist_filters, kicklist_filters):

		# Entries
		entries_date = []
		entries_guid = []
		entries_ip = []
		entries_code = []
		entries_name = []

		# Ban Entries
		ban_entries_date = []
		ban_entries_guid = []
		ban_entries_ip = []
		ban_entries_code = []
		ban_entries_name = []

		# Kick Entries
		kick_entries_date = []
		kick_entries_guid = []
		kick_entries_ip = []
		kick_entries_code = []
		kick_entries_name = []

		# Check for Offset pickle file / Initialize OffSet Data
		offset_data_file = logfile + ".pickle"

		logging.info('')
		logging.info('Parsing ' + str(logfile))
		logging.info('Checking of Offset Data File')
		if os.path.isfile(offset_data_file) is True:
			logging.info('Offset Data File Found')
			f_offset_data_file = open(offset_data_file, 'rb')
			offset_data = pickle.load(f_offset_data_file)
			logging.debug('Loading Offset Data = ' + str(offset_data))
			if offset_data != []:
				entries_date.append(offset_data[0])
				entries_guid.append(offset_data[1])
				entries_ip.append(offset_data[2])
				entries_code.append(offset_data[3])
				entries_name.append(offset_data[4])
			f_offset_data_file.close()
			logging.debug('Entries Data = ' + str(offset_data))
		else:
			logging.debug('No Offset Data File Found')

		# Scan BattlEye Logs
		if os.path.isfile(logfile) is True:
			f_backup = open(backupfile, "a")
			with open(logfile) as f_log:
				for line in f_log:
					## Append Lines to Backup Files
					f_backup.write(line)

					temp = line.strip()
					date = re.match('\A[0-3][0-9]\.[0-1][0-9]\.[0-9][0-9][0-9][0-9][ ][0-2][0-9][:][0-6][0-9][:][0-6][0-9][:]\s', temp)
					temp = re.split('\A[0-3][0-9]\.[0-1][0-9]\.[0-9][0-9][0-9][0-9][ ][0-2][0-9][:][0-6][0-9][:][0-6][0-9][:]\s', temp)
					if date is None:
						x = len(entries_date) - 1
						if x >= 0:
							logging.debug('Detected Multiple lines = ' + str(entries_code[x]))
							entries_code[x] = entries_code[x] + line.strip()
							logging.debug('Updated line = ' + str(entries_code[x]))
					else:
						name = re.split(".\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}[0-9].", temp[1])
						temp = re.split(".\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}[0-9].", line.strip())
						ip = re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}[0-9]", line.strip())
						code = re.split("\s-\s", temp[1])
						entries_date.append(date.group())
						entries_guid.append(code[0].strip(' '))
						entries_ip.append(ip.group())
						entries_code.append(code[1])
						entries_name.append(name[0])
			f_backup.close()

			os.remove(logfile)

		# Check for battleye offset condition
		offset_data = []
		if len(entries_date) > 0:
			x = time.mktime(time.localtime(self.scan_time))
			x2 = time.mktime((time.strptime(entries_date[-1], "%d.%m.%Y %H:%M:%S: ")))
			#print x - x2

			if ((x - x2) < self.offset) is True:
				offset_data.append(entries_date.pop())
				offset_data.append(entries_guid.pop())
				offset_data.append(entries_ip.pop())
				offset_data.append(entries_code.pop())
				offset_data.append(entries_name.pop())
				logging.debug("Saving  " + str(offset_data))

		# Update offset_data_file
		f_offset_data_file = open(offset_data_file, 'wb')
		pickle.dump(offset_data, f_offset_data_file)
		f_offset_data_file.close()

		if (len(entries_code) > 0) is True:

			if os.path.isfile(whitelist_filters) is True:
				# Remove whitelisted entries
				with open(whitelist_filters) as f:
					for line in f:
						temp = line.strip()
						x = 0
						while x != len(entries_code):
							if re.search(temp, entries_code[x]) is not None:
								entries_date.pop(x)
								entries_guid.pop(x)
								entries_ip.pop(x)
								entries_code.pop(x)
								entries_name.pop(x)
							else:
								x = x + 1
			else:
				# If file = missing, create an empty file
				print "Create missing filter " + str(whitelist_filters)
				open(whitelist_filters, 'w').close()

			#print "DEBUG 2: length of entries code " + str(len(entries_code))

			if banlist_filters is not None:
				if os.path.isfile(banlist_filters) is True:
					# Search for BlackListed Entries
					with open(banlist_filters) as f:
						for line in f:
							temp = line.strip()
							x = 0
							while x != len(entries_code):
								if re.search(temp, entries_code[x]) or re.search(temp, string.replace(entries_code[x], "\",\"", "")):
									ban_entries_date.append(entries_date.pop(x))
									ban_entries_guid.append(entries_guid.pop(x))
									ban_entries_ip.append(entries_ip.pop(x))
									ban_entries_code.append(entries_code.pop(x))
									ban_entries_name.append(entries_name.pop(x))
								else:
									x = x + 1
				else:
					# If file = missing, create an empty file
					open(banlist_filters, 'w').close()

			#print "DEBUG 3: length of entries code " + str(len(entries_code))

			if kicklist_filters is not None:
				if os.path.isfile(kicklist_filters) is True:
					# Search for KickList Entries
					with open(kicklist_filters) as f:
						for line in f:
							temp = line.strip()
							x = 0
							while x != len(entries_code):
								if re.search(temp, entries_code[x]) or re.search(temp, string.replace(entries_code[x], "\",\"", "")):
									kick_entries_date.append(entries_date.pop(x))
									kick_entries_guid.append(entries_guid.pop(x))
									kick_entries_ip.append(entries_ip.pop(x))
									kick_entries_code.append(entries_code.pop(x))
									kick_entries_name.append(entries_name.pop(x))
								else:
									x = x + 1
				else:
					# If file = missing, create an empty file
					open(kicklist_filters, 'w').close()

			#print "DEBUG 4: length of entries code " + str(len(entries_code))

		self.banlist = {"date": ban_entries_date,
						"guid": ban_entries_guid,
						"ip": ban_entries_ip,
						"code": ban_entries_code,
						"name": ban_entries_name}

		self.kicklist = {"date": kick_entries_date,
						"guid": kick_entries_guid,
						"ip": kick_entries_ip,
						"code": kick_entries_code,
						"name": kick_entries_name}

		self.unknownlist = {"date": entries_date,
							"guid": entries_guid,
							"ip": entries_ip,
							"code": entries_code,
							"name": entries_name}


class Bans:
	def __init__(self, bans_file):
		self.bans_file = bans_file

	def openfile(self):
		self.f_bans = open(self.bans_file, "a")

	def closefile(self):
		self.f_bans.close()

	def addban(self, guid, time, reason):
		self.f_bans.write(guid + " " + time + " " + reason + "\n")

	def removeban(self, guid, time, reason):
		pass
