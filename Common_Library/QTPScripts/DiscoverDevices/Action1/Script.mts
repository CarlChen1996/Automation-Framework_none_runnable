Dim logPath
logPath = "D:\Log\HPDM.log"
If not JavaWindow("HP Device Manager 5.0 Main").Exist(3) Then
	Logon
End If


For each ostype in Array("HP ThinPro 7","WES7P-64","Win10IoT-64","WES7E")
	DiscoverDevices(ostype)
Next


