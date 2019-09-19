Dim logPath
logPath = "D:\Log\HPDM.log"

If not JavaWindow("HP Device Manager 5.0 Main").Exist(5) Then
	Logon
End If

'--------------------
DataTable.GetSheet("Config")
DataTable.SetCurrentRow(1)
localPath = DataTable.Value("Local Path", "Config")
remotePath = DataTable.Value("Remote Path", "Config")

For each os_package in ostype_list
	If CreateFilter_Local("UUT_"&os_package) Then
		DeleteTemplete os_package, "deploy-node-1-test" 
		If SendPackages(os_package, localPath, remotePath) Then
			result = GetTaskReport(40)
		End If
		Wait 3
		DeleteTemplete os_package, "deploy-node-1-test" 
		'Delete template here is to avoid template with the same name cannot be delete  in other os
	End If
Next
' x = SendPackages("WES7E", "C:\inetpub\ftproot\jenkins\windows\task_2","c:\temp")
'----------------------

Function SendPackages(os, local, remote)
	With JavaWindow("HP Device Manager 5.0 Main")
		.Activate
		.JavaObject("ManagerDevices").Click 10, 10, "LEFT"
		.JavaList("OSSelection").Select os 'OS type data
		''
		''Select Filter send task
		''
		.JavaList("Filter By").Select "deploy-node-1-filter"
		If .JavaTree("Group").GetROProperty("items count") <> 0 Then
			.JavaTree("Group").Click 50, 10, "RIGHT"
			.JavaMenu("Send Task").Select
			.JavaDialog("Template Chooser").JavaList("TemplateCategory").Select "File and Registry"
			.JavaDialog("Template Chooser").JavaList("Template").Select "_File and Registry" 'Data prepared
			.JavaDialog("Template Chooser").JavaButton("Next").Click
			With .JavaDialog("Template Chooser").JavaDialog("Task Editor")
				.JavaButton("Add").Click
				.JavaDialog("Sub-Task Chooser").JavaList("DMList").Select "Deploy Files"
				.JavaDialog("Sub-Task Chooser").JavaButton("OK").Click
				.JavaDialog("Deploy Files").JavaButton("Add from local").Click
				.JavaDialog("Deploy Files").JavaDialog("Add from local").JavaEdit("File Name").Set local 'Data packages
				.JavaDialog("Deploy Files").JavaDialog("Add from local").JavaButton("Add from local").Click
				Wait 3
				.JavaDialog("Deploy Files").JavaTable("Sub-task to deploy files").SetCellData 0,"Path On Device",remote 'Data Deploy dist path
				.JavaDialog("Deploy Files").JavaButton("OK").Click
				.JavaButton("OK").Click
				.JavaDialog("Enter New Template Name").JavaEdit("NewTemplateName").Set "deploy-node-1-test"
				.JavaDialog("Enter New Template Name").JavaButton("OK").Click
				
			End With
			.JavaDialog("Package Description Editor").JavaButton("Generate").Click
			SendPackages = True
		Else 
			SendPackages = False
		End If
	End With
End Function


'msgbox result(0)

