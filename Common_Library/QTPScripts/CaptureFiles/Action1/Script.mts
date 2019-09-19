Dim logPath
logPath = "D:\Log\HPDM.log"
If not JavaWindow("HP Device Manager 5.0 Main").Exist(3) Then
	Logon
End If



DataTable.GetSheet("Config")
DataTable.SetCurrentRow(1)
taskName = Split(DataTable.Value("Project Name"),"_", 2)(1)
localPath = DataTable.Value("Local Path")
remotePath = DataTable.Value("Remote Path")
temp = Split(localPath, "/")
project_name = temp(ubound(temp))
For each ostype in Array("HP ThinPro 7","WES7P-64","Win10IoT-64","WES7E")
	If CreateFilter_Local("UUT_"&ostype) Then
		x = CaptureFiles(ostype, project_name, remotePath)
	End If
Next
'x = CaptureFiles("Win10IoT-64", "TaskName","c:\temp")


Function CaptureFiles(os, projectName, remote)
	Set sheet = DataTable.GetSheet("UUT_"&os)
	capture_device_list = sheet.GetRowCount
	DataTable.SetCurrentRow(1)
'	msgbox capture_device_list
	If capture_device_list > 0 Then
		For capture_device = 1 To capture_device_list Step 1
			With JavaWindow("HP Device Manager 5.0 Main")
				.Activate
				.JavaObject("ManagerDevices").Click 10, 10, "LEFT"
				.JavaList("OSSelection").Select os '-----------------------------------------Test data: OS
				If .JavaTree("Group").GetROProperty("items count") <> 0 Then
					.JavaTree("Group").Select "root;Deploy-Node-1 (00:0C:29:94:78:92)"
'					msgbox DataTable.Value("IP","UUT_"&os)
					row_id = IsDeviceExist(DataTable.Value("IP","UUT_"&os)) '-----------------------------Test Data: IP, Mac
					If row_id <> "N" Then
						.JavaTable("Deploy-Node-1 (00:0C:29:94:78").ClickCell row_id,"IP Address","RIGHT"
						
						.JavaMenu("Send Task").Select
'						Else
						
						.JavaDialog("Template Chooser").JavaList("TemplateCategory").Select "File and Registry"
						.JavaDialog("Template Chooser").JavaList("Template").Select "_File and Registry" 
						.JavaDialog("Template Chooser").JavaButton("Next").Click
						With .JavaDialog("Template Chooser").JavaDialog("Task Editor")
							.JavaButton("Add").Click
							.JavaDialog("Sub-Task Chooser").JavaList("DMList").Select "Capture Files"
							.JavaDialog("Sub-Task Chooser").JavaButton("OK").Click
							.JavaDialog("Capture Files").JavaButton("Add").Click
							.JavaDialog("Capture Files").JavaTable("FilePath").SetCellData 0,"File or folder with full path", remote&"\"&projectName&"\"&"test_report" 'Test Data: remote path
							.JavaDialog("Capture Files").JavaEdit("LocalPath").Set projectName&"\"&DataTable.Value("IP","UUT_"&os)
							.JavaDialog("Capture Files").JavaButton("OK").Click
							.JavaButton("OK").Click	
						End With
						GetTaskReport(50)
'					Else 
'						Msgbox "not found in list"
					End If
					
				End If
			End With
			DataTable.SetNextRow
		Next
		
	End If
	
End Function


'result = GetTaskReport(50)
'msgbox result(0)
