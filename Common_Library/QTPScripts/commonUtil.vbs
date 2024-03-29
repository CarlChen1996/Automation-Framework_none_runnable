test_data = "C:\inetpub\ftproot\test_data.xlsx"
ostype_list=Array("HP ThinPro 7","WES7P-64","Win10IoT-64","WES7E")
' DataTable first Line: row=1
' JavaTable first line: row=0
' ----os type---------------------
' HP ThinPro 7
' WES7P-64
' Win10IoT-64
' WES7E
' ---------------------------------
' Set excel = new ExcelUtil
Sub Logon
	SystemUtil.Run "C:\Program Files\HP\HP Device Manager\Console\JVM\bin\javaw.exe", "-Xms256m -Xmx2048m -Dfile.encoding=UTF-8 -Dsun.java2d.uiScale=1.0 -classpath hpdm-console.jar com.hp.hpdm.console.main.Console", "C:\Program Files\HP\HP Device Manager\Console\lib\", "", 1
	With JavaWindow("HP Device Manager 5.0 Login")
		.JavaEdit("Username").Set "root"
		.JavaEdit("Password").Set " "
		.JavaButton("OK").Click
	End With
	' --------Wait logon successfully------------------
	For tests = 1 To 60 Step 1
		If JavaWindow("HP Device Manager 5.0 Main").Exist(3) Then
			Exit For
		Else 
			Wait 1
		End If
	Next
End Sub

Sub LogInfo(msg, fileName)
	Dim fs,fso
	Set fs = CreateObject("Scripting.FileSystemObject")
	Set fso = fs.OpenTextFile(fileName, 8, True) ' 8:ForAppending, 2:ForWriting, True: If File not Exist, create File
	fso.WriteLine "[" & Date & "-" & Time & "]:" & msg & Chr(10)
	fso.Close
End Sub

Function GetTaskReport(waitTime)
	Dim result()
	JavaWindow("HP Device Manager 5.0 Main").JavaObject("TasksReports").Click 5, 5,"LEFT"
	JavaWindow("HP Device Manager 5.0 Main").JavaList("TaskTypes").Select "Device Tasks"
	JavaWindow("HP Device Manager 5.0 Main").JavaTable("DeviceTasksReport").DoubleClickCell 0, 1 'Select the first task
	rows = JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Device Task View").JavaTable("TaskStatus").GetROProperty("rows")
	For row = 0 To rows -1 Step 1
		Dim tastTimeOut
		taskTimeOut=True
		hostName = JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Device Task View").JavaTable("TaskStatus").GetCellData(row, "Device Name")
		For t = 0 To waitTime Step 1
			status = JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Device Task View").JavaTable("TaskStatus").GetCellData(row, "Status")
			endTime = JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Device Task View").JavaTable("TaskStatus").GetCellData(row, "End Time")
			If endTime <> "" Then
			'  dynamic append array: Redim preserve--- preserve: do not clear previous array
				ReDim Preserve result(row)
				result(row)=hostName & ":" & status
				taskTimeOut = False
'				msgbox Cstr(endTime) & Cstr(row)
				Exit For
			End If
			Wait(1)
		Next
'		If taskTimeOut Then
'			result(row) = hostName & ":timeout"
'		End If
	Next
	JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Device Task View").Close
	GetTaskReport=result
End Function

Function GetTaskReportID
	JavaWindow("HP Device Manager 5.0 Main").JavaObject("TasksReports").Click 5, 5,"LEFT"
	JavaWindow("HP Device Manager 5.0 Main").JavaList("TaskTypes").Select "Device Tasks"
	id = JavaWindow("HP Device Manager 5.0 Main").JavaTable("DeviceTasksReport").GetCellData(0,0) '.DoubleClickCell 0, 1 'Select the first task
	GetTaskReportID=id
End Function

Function IsDeviceExist(ip)
' Reture device index in javatable object, if not found return "N"
	flag = "N"
	With JavaWindow("HP Device Manager 5.0 Main").JavaTable("Deploy-Node-1 (00:0C:29:94:78")
		rows = .GetROProperty("rows")
		For row = 0 To rows-1 Step 1
			If .GetCellData(row,"IP Address")=ip Then
				flag = row
				Exit For
			End If
		Next
		IsDeviceExist=flag
	End With
End Function

Function IsTemplateExist(name)
	flag = "N"
	With JavaWindow("HP Device Manager 5.0 Main").JavaTable("DeviceTasksReport")
		rows = .GetROProperty("rows")
		For row = 0 To rows-1 Step 1
			If .GetCellData(row, "Template")=name Then
				flag=row
				Exit For
			End If
		Next
		IsTemplateExist=flag
	End With
End Function

Class ExcelUtil
	Dim oExcel,workBook,workSheet
	
	Public Sub OpenWorkbook()
		Set oExcel = CreateObject("Excel.Application")
		Set workBook = oExcel.Workbooks.Open(test_data)
		Set workSheet = oExcel.Worksheets(1)
	End Sub
	
	Public Sub ActiveSheet(sheetname)
		Set workSheet = oExcel.Worksheets.Item(sheetname)
		workSheet.Activate
	End  Sub
	
	Public Function GetUsedRows()
		GetUsedRows = workSheet.UsedRange.Rows.count
	End Function
	
	Public Function GetCellValue(row, col)
		GetCellValue = workSheet.Cells(row,col)
	End Function
	
	Public Sub SetCellValue(row,col,data)
		workSheet.Cells(row,col).value=data
		workBook.Saved=False
		workBook.Save
	End Sub
	
	Public Sub DeleteRow(row)
		workSheet.Rows(row).Delete
		workBook.Saved=False
		workBook.Save
	End Sub
	Public Sub CloseWorkBook()
		workBook.Close
		oExcel.Quit
	End Sub
End Class
 
Sub CreateFilter(excel, sheetName)
	excel.ActiveSheet(sheetName)
	rows = excel.GetUsedRows
	logPath = "D:\Log\HPDM.log"
	If not JavaWindow("HP Device Manager 5.0 Main").Exist(3) Then
		Logon
	End If
	
	With JavaWindow("HP Device Manager 5.0 Main")
		.Activate
		.JavaObject("ManagerDevices").Click 10, 10, "LEFT"
		.JavaButton("Device Filter").Click
		.JavaDialog("Device Filter Management").JavaList("FilterList").Select "deploy-node-1-filter"
		.JavaDialog("Device Filter Management").JavaButton("Edit").Click
		.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaTree("JTree").Activate "#0"
		.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaButton("delete").Click
		
		.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaTree("JTree").Activate "#0"
		.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaCheckBox("OR").Set "ON"
		For index = 2 To rows Step 1
			.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaTree("JTree").Activate "#0"
			.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaButton("add").Click
			.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaDialog("Choose Criteria Key").JavaList("CriteriaKeyList").Select "MAC Address"
			.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaDialog("Choose Criteria Key").JavaButton("OK").Click
			.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaDialog("Criteria Editor").JavaEdit("Criteria").Set excel.GetCellValue(index, 2) '--------Test Data Mac
			.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaDialog("Criteria Editor").JavaButton("OK").Click
		Next
	
		.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaButton("OK").Click
		.JavaDialog("Device Filter Management").JavaButton("Close").Click
	End With

End Sub

Function CreateFilter_Local(sheetName)
	Set sheet = DataTable.GetSheet(sheetName)
	DataTable.SetCurrentRow(1)
	rows = sheet.GetRowCount
'	msgbox DataTable.Value("Mac", sheetName)

	If rows>0 Then
		logPath = "D:\Log\HPDM.log"
'		If not JavaWindow("HP Device Manager 5.0 Main").Exist(3) Then
'			Logon
'		End If
		
		With JavaWindow("HP Device Manager 5.0 Main")
			.Activate
			.JavaObject("ManagerDevices").Click 10, 10, "LEFT"
			.JavaButton("Device Filter").Click
			.JavaDialog("Device Filter Management").JavaList("FilterList").Select "deploy-node-1-filter"
			.JavaDialog("Device Filter Management").JavaButton("Edit").Click
			.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaTree("JTree").Activate "#0"
			.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaButton("delete").Click
			.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaTree("JTree").Activate "#0"
			.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaCheckBox("OR").Set "ON"
			For index = 0 To rows-1 Step 1
				.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaTree("JTree").Activate "#0"
				.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaButton("add").Click
				.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaDialog("Choose Criteria Key").JavaList("CriteriaKeyList").Select "MAC Address"
				.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaDialog("Choose Criteria Key").JavaButton("OK").Click
				If DataTable.Value("Mac", sheetName) <> "" Then
					.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaDialog("Criteria Editor").JavaEdit("Criteria").Set DataTable.Value("Mac", sheetName) '--------Test Data Mac
					.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaDialog("Criteria Editor").JavaButton("OK").Click
'					.Close
'					Exit Function
				End If
				DataTable.SetNextRow
			Next

			.JavaDialog("Device Filter Management").JavaDialog("Edit Device Filter").JavaButton("OK").Click
			.JavaDialog("Device Filter Management").JavaButton("Close").Click
		End With
		CreateFilter_Local=True
	Else
		CreateFilter_Local=False
	End If

End Function

Sub DeleteTemplete(os, name)
	With JavaWindow("HP Device Manager 5.0 Main")
		.JavaObject("Templates Rules").Click 10,10,"LEFT"
		.JavaList("OSSelection").Select os
		.JavaTree("TemplateFolderTree").Click 50, 10, "LEFT"
		templateCount = .JavaTable("Gateway Tasks").GetROProperty("rows")
		For template = 0 To templateCount-1 Step 1
			If .JavaTable("Gateway Tasks").GetCellData(template,"Template")=name Then
				.JavaTable("Gateway Tasks").ClickCell template,"Template","RIGHT"
				.JavaMenu("Delete").Select
				.JavaDialog("Confirm Delete Action").JavaButton("Yes").Click
				Exit For
			End If
		Next
'
	End With
End Sub

Function DiscoverDevices(os)
	Set discover_sheet = DataTable.GetSheet("UUT_"&os)
	ip_rows = discover_sheet.GetRowCount
	DataTable.SetCurrentRow(1)
	For temp_row = 1 To ip_rows Step 1
		ip = DataTable.Value("IP", "UUT_"&os)
'		msgbox DataTable.GetCurrentRow&os&ip
		If ip="" Then
			Exit Function
		End If
		discover_sheet.SetNextRow
		ip_split = split(ip, ".")
		With JavaWindow("HP Device Manager 5.0 Main")
			.Activate
			.JavaObject("ManagerDevices").Click 10, 10, "LEFT"
			'------------------------------
			'Delete Exist device by IP
			'------------------------------
			existDeviceRow = IsDeviceExists(ip,os)
			If existDeviceRow <> "N" Then
				JavaWindow("HP Device Manager 5.0 Main").JavaTable("Deploy-Node-1 (00:0C:29:94:78").ClickCell existDeviceRow, "IP Address", "RIGHT"
				JavaWindow("HP Device Manager 5.0 Main").JavaMenu("Delete").Select
'				msgbox "delete"&os&ip
				JavaWindow("HP Device Manager 5.0 Main").JavaDialog("Confirm Delete Action").JavaButton("Yes").Click
			End If
			'---------------------------------
			.JavaButton("Discover Devices").Click
			.JavaDialog("Discover Device").JavaRadioButton("Scan using IP range").Set "ON"
			.JavaDialog("Discover Device").JavaButton("Next >").Click
		End  With
		JavaDialog("Discover by Range").JavaEdit("StartingIP1").Set ip_split(0)
		JavaDialog("Discover by Range").JavaEdit("StartingIP2").Set ip_split(1)
		JavaDialog("Discover by Range").JavaEdit("StartingIP3").Set ip_split(2)
		JavaDialog("Discover by Range").JavaEdit("StartingIP4").Set ip_split(3)
		JavaDialog("Discover by Range").JavaEdit("EndingIP1").Set ip_split(0)
		JavaDialog("Discover by Range").JavaEdit("EndingIP2").Set ip_split(1)
		JavaDialog("Discover by Range").JavaEdit("EndingIP3").Set ip_split(2)
		JavaDialog("Discover by Range").JavaEdit("EndingIP4").Set ip_split(3)
		JavaDialog("Discover by Range").JavaButton("OK").Click
	'	------Wait Result-----------------------------------------------------
		JavaWindow("HP Device Manager 5.0 Main").JavaObject("TasksReports").Click 5, 5, "LEFT"
		JavaWindow("HP Device Manager 5.0 Main").JavaList("Temp&TaskList").Select "#1"
		Wait 15 'wait discover task show under gateway task table
		For wait_time = 1 To 20 Step 1
			status = JavaWindow("HP Device Manager 5.0 Main").JavaTable("Gateway Tasks").GetCellData(0,"Task Status")
			If status="Finished" Then
				Exit For
			Else
				Wait 1
			End If
		Next
	Next
End Function

Function GetDevices()
	Dim devices
	devices = Array()
	index = 0
	For each getdevice_ostype in ostype_list
		Set getdevice_sheet = DataTable.GetSheet("UUT_"&getdevice_ostype)
		getdevice_sheet.SetCurrentRow(1)
		getdevice_sheet_rows = getdevice_sheet.GetRowCount
		If getdevice_sheet_rows>0 Then
			For getdevice_sheet_row = 1 To getdevice_sheet_rows Step 1
				ReDim Preserve devices(index)
				devices(index) = DataTable.Value("IP","UUT_"&getdevice_ostype)&"_"&getdevice_ostype
				index = index + 1
				getdevice_sheet.SetNextRow
			Next
		End If
	Next
	GetDevices = devices
End Function

Function IsDeviceExists(ip, os)
' Reture device index in javatable object, if not found return "N"
	flag = "N"
	With JavaWindow("HP Device Manager 5.0 Main") '.JavaTable("Deploy-Node-1 (00:0C:29:94:78")
		.JavaObject("ManagerDevices").Click 10, 10, "LEFT"
		.JavaList("OSSelection").Select os 'OS type data
		.JavaList("Filter By").Select "[NONE]"
		If .JavaTree("Group").GetROProperty("items count") <> 0 Then
			.JavaTree("Group").Click 50, 10, "LEFT"
			exist_rows = .JavaTable("Deploy-Node-1 (00:0C:29:94:78").GetROProperty("rows")
			For exist_row = 0 To exist_rows-1 Step 1
				If .JavaTable("Deploy-Node-1 (00:0C:29:94:78").GetCellData(exist_row,"IP Address")=ip Then
					flag = exist_row
					Exit For
				End If
			Next
		End If
	End With
	IsDeviceExists=flag
End Function
