# logs_server.py
#	 This file is part of pyBEscanner.
#
#	 pyBEscanner is free software: you can redistribute it and/or modify
#	 it under the terms of the GNU General Public License as published by
#	 the Free Software Foundation, either version 3 of the License, or
#	 (at your option) any later version.
#
#	 pyBEscanner is distributed in the hope that it will be useful,
#	 but WITHOUT ANY WARRANTY; without even the implied warranty of
#	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	 GNU General Public License for more details.
#
#	 You should have received a copy of the GNU General Public License
#	 along with pyBEscanner.  If not, see <http://www.gnu.org/licenses/>.


import datetime
import os
import locale
import pickle
import re

pickleVersion = 2


def scan(logfile, log_offset):
	if os.path.isfile(logfile) is True:
		with open(logfile, 'r') as f_log:
			f_log.seek(0,2)
			if f_log.tell() == log_offset:
				f_log_entries = []
				f_offset = log_offset
			else:
				f_log.seek(log_offset)
				f_log_entries = f_log.readlines()
				f_offset = f_log.tell()
	return f_log_entries, f_offset


def load_datafile(logfile, datafile):
	timestamp = os.path.getctime(logfile)
	if os.path.isfile(datafile) is True:
		with open(datafile, 'rb') as f_data_file:
			data = pickle.load(f_data_file)
		if (data["Version"] != pickleVersion) or (data["Timestamp"] != timestamp):
			data = {"Version": pickleVersion, "Offset":0, "Lastline":"", "Timestamp": timestamp}
	else:
		data = {"Version": pickleVersion, "Offset":0, "Lastline":"", "Timestamp": timestamp}
	return data
		
def save_datafile(data, datafile):
	# Update offset_data_file
	with open(datafile, 'wb') as f_datafile:
		pickle.dump(data, f_datafile)



class PlayerTracker:
	def __init__(self, server_settings, player_tracker_data_file, server_ban_deamon):
		self.player_tracker_data_file = player_tracker_data_file
		self.server_ban_deamon = server_ban_deamon
		self.resetData()
		
	def resetData(self):
		self.players = {}
		self.save()
	
	def addPlayer(self, playername, ip):
		if self.players.has_key(playername):
			print("Player Tracker has already got a record for " + playername)
		self.players[playername] = {"IP": ip}
	
	def updatePlayerGUID(self, playername, guid):
		if self.players.has_key(playername):
			self.players[playername]["GUID"] = guid
		else:
			print
			print("Player Tracker has no record of " + playername)
		
	def removePlayer(self, playername):
		if self.players.has_key(playername):
			del self.players[playername]
		else:
			print
			print("Player Tracker has no record of " + playername)
			
	def banPlayer(self, playername, guid=None, ip=None):
		pass
		
	def load(self):
		if os.path.isfile(self.player_tracker_data_file) is True:
			with open(self.player_tracker_data_file, 'rb') as f_data_file:
				data = pickle.load(f_data_file)
			if (data["Version"] != pickleVersion):
				data = {"Version": pickleVersion, "Players": {}}
		else:
			data = {"Version": pickleVersion, "Players": {}}
		self.players = data["Players"]
		
	def save(self):
		with open(self.player_tracker_data_file, 'wb') as f_datafile:
			pickle.dump({"Version": pickleVersion, "Players": self.players}, f_datafile)


class RPTScanner:
	def __init__(self, server_settings, player_tracker):
		self.player_tracker = player_tracker
		self.logfile = server_settings["Server RPT Log"]
		self.offset_data_file = os.path.join(server_settings["Temp Directory"], "server_rpt.offset")

		backup_dir = os.path.join(server_settings["Logs Directory"], datetime.datetime.now().strftime("%Y-%m-%d"))
		self.backup_rptlog = os.path.join(backup_dir, "server_rpt.log")

	def scan_log(self, lastline=1):
		if os.path.isfile(self.logfile) is False:
			print
			print("Warning -- Could Not Find " + self.logfile)
		else:
			self.offset_data = load_datafile(self.logfile, self.offset_data_file)
			self.entries, f_offset = scan(self.logfile, self.offset_data["Offset"])
			self.offset_data["Offset"] = f_offset
			if self.entries != []:
				with open(self.backup_rptlog, "a") as rptlog_backup:
					self.entries[0] = self.offset_data["Lastline"] + self.entries[0]
					x = 0
					while x < (len(self.entries) - lastline):
						rptlog_backup.write(self.entries[x])
						x = x + 1
				self.offset_data["Lastline"] = self.entries[x-1]
				self.entries = []
				save_datafile(self.offset_data, self.offset_data_file)

				
class ConsoleScanner:
	def __init__(self, server_settings, player_tracker):
		self.player_tracker = player_tracker
		self.logfile = server_settings["Server Console Log"]
		self.offset_data_file = os.path.join(server_settings["Temp Directory"], "server_console.offset")

		player_tracker_data_file = os.path.join(server_settings["Temp Directory"], "server_player_tracker.offset")
				
		backup_dir = os.path.join(server_settings["Logs Directory"], datetime.datetime.now().strftime("%Y-%m-%d"))
		self.backup_chatlog = os.path.join(backup_dir, "chat-logs.txt")
		self.backup_consolelog = os.path.join(backup_dir, "server_console.log")

	def scan_log(self, lastline=1):
		if os.path.isfile(self.logfile) is False:
			print
			print("Warning -- Could Not Find " + self.logfile)
		else:
			self.offset_data = load_datafile(self.logfile, self.offset_data_file)
			self.entries, self.offset_data["Offset"] = scan(self.logfile, self.offset_data["Offset"])
			if self.offset_data["Offset"] != 0:
				self.player_tracker.load()
			else:
				self.player_tracker.resetData()
			if self.entries != []:
				with open(self.backup_chatlog, "a") as chatlog_backup, open(self.backup_consolelog, "a") as consolelog_backup:
					self.entries[0] = self.offset_data["Lastline"] + self.entries[0]
					x = 0
					while x < (len(self.entries) - lastline):
						consolelog_backup.write(self.entries[x])
						#time = self.entries[x][0:8]
						data = self.entries[x][9:]
						if len(data) > 2:
							if re.match("BattlEye Server: ", data):
								if re.match("BattlEye Server: \(.*\)", data):
									chatlog_backup.write(self.entries[x])
								elif re.match("BattlEye Server: Player #", data):
									if re.search("connected$", data):
										playername, ip = self.get_player_ip(data)
										self.player_tracker.addPlayer(player_name, ip)
									else:
										pass
								elif re.match("BattlEye Server: Verified GUID", data):
									print data
									playername, guid = self.get_player_guid(data)
									self.player_tracker.updatePlayerGUID(playername, guid)
							elif re.match("Player ", data):
								if re.search("disconnected\.$", data):
									self.player_tracker.removePlayer(data[7:-14])
								elif re.search("kicked off by BattlEye: Global Ban \#.*$", data):
									playername = self.get_player_be_kick(data)
									self.player_tracker.banPlayer(playername)
								elif re.search("kicked off by BattleEye: BattlEye Hack", data):
									playername = self.get_player_be_kick(data)
									self.player_tracker.banPlayer(playername)
								else:
									pass
							else:
								pass
						x = x + 1
				self.offset_data["Lastline"] = self.entries[x-1]
				self.entries = []
				save_datafile(self.offset_data, self.offset_data_file)
				self.player_tracker.save()
				
	def get_player_ip(self, line):
		# Just Incase Player Name Tries to Confuse pyBEscanner
		line = re.split("#\d{1,3}\s", line, 1)[1]
		temp = re.search("\(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}[0-9]\) connected$", line).group()
		playername = line[: (-1 * (len(temp)+1))]
		ip = temp.split(":")[0][1:]
		
		return playername, ip
		 
	
	def get_player_guid(self, line):
		line = re.split("GUID \(", line, 1)[1]
		temp = re.split("\)", line, 1)

		guid = temp[0]
		playername = re.split("\s", temp[1][11:], 1)[1]
		
		return playername, guid
	
	
	def get_player_be_kick(self, line):
		# Just Incase Player Name Tries to Confuse pyBEscanner
		temp = re.split("kicked off by Battleye")
		playername = ""
		for x in range (0, len(temp) - 1):
			playername = playername + temp[x]
		return playername