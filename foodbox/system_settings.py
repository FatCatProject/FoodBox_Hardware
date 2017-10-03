from enum import Enum


class SystemSettings(Enum):
	BrainBox_IP = 1  # IP address of BrainBox to communicate with
	FoodBox_ID = 2  # Unique ID for this box
	FoodBox_Name = 3  # Name of box, defaults to HOSTNAME
	Max_Open_Time = 4  # Max time to keep lid open before buzzer turns on
	Scale_Offset = 5  # OFFSET for HX711
	Scale_Scale = 6  # SCALE for HX711
	Sync_Interval = 7  # Interval between pooling BrainBox
	Last_Weight = 8  # The last weight before system went down
	BrainBox_Port = 9  # TCP port number of BrainBox to communicate with
	Last_Purge = 10  # The last time the logs were purged
