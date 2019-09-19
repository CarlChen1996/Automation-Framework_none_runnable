Dim logPath
logPath = "D:\Log\HPDM.log"
If not JavaWindow("HP Device Manager 5.0 Main").Exist(3) Then
	Logon
End If


DataTable.GetSheet("Config")
DataTable.SetCurrentRow(1)
cycles = DataTable.Value("Cycle", "Config")
localPath = DataTable.Value("Local Path", "Config")
remotePath = DataTable.Value("Remote Path", "Config")
temp = Split(localPath, "/")
project_name = temp(ubound(temp))

For each command_os in ostype_list
	If Instr(command_os, "ThinPro") Then
	' ------------ Linux OS ------------------------------
		cmd = "chmod 777 "&remotePath&"/"&project_name&"/run"&vbCr&remotePath&"/"&project_name&"/run"
		If CreateFilter_Local("UUT_"&command_os) Then
			If SendCommand(command_os, cmd) Then
				GetTaskReport(40)
			End If
			Wait 5
		End If
	Else 
	' ---------------WES OS ----------------------------
		If Instr(Ucase(command_os), "WES7") Then
			user="Administrator"
		ElseIf Instr(Ucase(command_os), "WIN10IOT") Then
			user="Admin"
		End If
		cmd = "schtasks /delete /tn taskName /F"&vbCr&"schtasks /create  /sc WEEKLY /tn taskName /tr "&remotePath&"/"&project_name&"/run.exe"&" /ru "&user&vbCr&"schtasks /run /tn taskName"
		If CreateFilter_Local("UUT_"&command_os) Then
			If SendCommand(command_os, cmd) Then
				GetTaskReport(40)
			End If
			Wait 5
		End If
	End If
Next
Wait 20
' --------Keep sending sripts --------------------------------------------------------------
' --------Send command checking remote scripts flag.txt, if test finished exist ------------
' --------Until all the uut test finished, exit qtp scripts --------------------------------
' -------QTP datatable set value only support runtime data, so set status must included with sendcommand
DataTable.GetSheet("Config")
DataTable.SetCurrentRow(1)
For cycle = 0 To cycles Step 1
	If DataTable.Value("Status")<>"Finished" Then
		If SetStatus = "Finished" Then
			DataTable.Value("Status")="Finished"
		End If
	Else 
		Exit For
	End If
Next


Function SetStatus()
	all_status="Finished"
	For Each setstatus_ostype in ostype_list
		Set SetStatus_sheet = DataTable.GetSheet("UUT_"&setstatus_ostype)
		SetStatus_sheet.SetCurrentRow(1)
		SetStatus_sheet_rows = SetStatus_sheet.GetRowCount
		If SetStatus_sheet_rows>0 Then ' check uut count under each ostype
			For SetStatus_sheet_row = 1 To SetStatus_sheet_rows Step 1 ' Loop all the uut under ostype
				If DataTable.Value("Status","UUT_"&setstatus_ostype)=""  or DataTable.Value("Status","UUT_"&setstatus_ostype)="None" or DataTable.Value("Status","UUT_"&setstatus_ostype)="Running"  Then ' check status, if running reload status, if finished skip
					If SendCommandByIP(DataTable.Value("IP","UUT_"&setstatus_ostype), setstatus_ostype, "more """&remotePath&"/"&project_name&"/flag.txt""")<> "N" Then
						' This If is to check if UUT online for HPDM, if exist, send command, else skip
						task_status = GetStatus(600) ' load status for first task report
						DataTable.Value("Status", "UUT_"&setstatus_ostype)=task_status ' Set latest status for UUT
						If task_status<>"Finished" Then
						' Flag the summary result, only all the uut finished, task set finished, if one not finished, the total task status still No Finished
							all_status="No Finished"
						End If
					End If	
				End If
				SetStatus_sheet.SetNextRow
			Next
		End If
	Next
	SetStatus = all_status
End Function



Function SendCommand(os, command) ' By filter
	' -----Send command by Filter group under each ostype ----------------------------
	' -----If there is IP under filter return True, No IP under Filter return False---
	With JavaWindow("HP Device Manager 5.0 Main")
		.Activate
		Wait 3 ' Wait object shown before click by position
		.JavaObject("ManagerDevices").Click 10, 10, "LEFT"
		.JavaList("OSSelection").Select os 'OS type data
		''Select Filter send task
		.JavaList("Filter By").Select "deploy-node-1-filter"
		If .JavaTree("Group").GetROProperty("items count") <> 0 Then
			.JavaTree("Group").Click 50, 10, "RIGHT"
			.JavaMenu("Send Task").Select
			.JavaDialog("Template Chooser").JavaList("TemplateCategory").Select "File and Registry"
			.JavaDialog("Template Chooser").JavaList("Template").Select "_File and Registry"
			.JavaDialog("Template Chooser").JavaButton("Next").Click
			With .JavaDialog("Template Chooser").JavaDialog("Task Editor")
				.JavaButton("Add").Click
				.JavaDialog("Sub-Task Chooser").JavaList("DMList").Select "Script"
				.JavaDialog("Sub-Task Chooser").JavaButton("OK").Click
				.JavaDialog("Script Sub-task").JavaEdit("ScriptsContent").Set command
				.JavaDialog("Script Sub-task").JavaButton("OK").Click
				.JavaButton("OK").Click
			End  With
			'-----------------------get report----------------------------------
			GetTaskReport(600)
			SendCommand=True
		Else 
			SendCommand=False
		End If
	End With
End Function

Function SendCommandByIP(ip, os, command)
	' THis function only support send command by uut ip, and is related with set uut status, so if only send command, need replace getstatus(600) with GetTaskReport(600)
	' If IP exist return command status (more c:\temp\taskname\flag.txt checking if test finished)
	' If IP do not exist return N
	With JavaWindow("HP Device Manager 5.0 Main")
		.Activate
		Wait 3 ' Wait object shown before click by position
		.JavaObject("ManagerDevices").Click 10, 10, "LEFT"
		.JavaList("OSSelection").Select os 'OS type data
		''clear Filter send task
		.JavaList("Filter By").Select "[NONE]"
		Wait 3
		device_id = IsDeviceExist(ip)
		If device_id<>"N" Then
			.JavaTable("Deploy-Node-1 (00:0C:29:94:78").ClickCell device_id,"IP Address","RIGHT"
			.JavaMenu("Send Task").Select
			.JavaDialog("Template Chooser").JavaList("TemplateCategory").Select "File and Registry"
			.JavaDialog("Template Chooser").JavaList("Template").Select "_File and Registry"
			.JavaDialog("Template Chooser").JavaButton("Next").Click
			With .JavaDialog("Template Chooser").JavaDialog("Task Editor")
				.JavaButton("Add").Click
				.JavaDialog("Sub-Task Chooser").JavaList("DMList").Select "Script"
				.JavaDialog("Sub-Task Chooser").JavaButton("OK").Click
				.JavaDialog("Script Sub-task").JavaEdit("ScriptsContent").Set command
				.JavaDialog("Script Sub-task").JavaButton("OK").Click
				.JavaButton("OK").Click
			End  With
			SendCommandByIP = GetStatus(600)
		Else 
			SendCommandByIP = "N"
		End If
	End With
End Function


Function GetStatus(waitTime)
	status="N"
	JavaWindow("HP Device Manager 5.0 Main").JavaObject("TasksReports").Click 5, 5,"LEFT"
	JavaWindow("HP Device Manager 5.0 Main").JavaList("TaskTypes").Select "Device Tasks"
	JavaWindow("HP Device Manager 5.0 Main").JavaTable("DeviceTasksReport").DoubleClickCell 0, 1 'Select the first task
	For t = 0 To waitTime Step 1
		status = JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Device Task View").JavaTable("TaskStatus").GetCellData(0, "Status")
		endTime = JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Device Task View").JavaTable("TaskStatus").GetCellData(0, "End Time")
		If endTime <> "" Then
			JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Device Task View").JavaTable("TaskStatus").DoubleClickCell 0,"Status","LEFT"
			row = JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Device Task View - _File").JavaTable("TaskLog").GetROProperty("rows")
			For Iterator = 0 To row-1 Step 1
				If Instr(Ucase(JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Device Task View - _File").JavaTable("TaskLog").GetCellData(Iterator,"Log")),"TEST FINISHED") Then
					status = "Finished"
					Exit For
				ElseIf Instr(Ucase(JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Device Task View - _File").JavaTable("TaskLog").GetCellData(Iterator,"Log")),"TEST RUNNING") Then
					status = "Running"
					Exit For
				Else 
					status = "None"
				End If
			Next
			Exit For
		End If
			Wait(1)
	Next
	JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Device Task View").Close
	GetStatus = status
End Function

