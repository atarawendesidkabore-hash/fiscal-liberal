Attribute VB_Name = "FiscalCalculator"
Option Explicit

#If VBA7 Then
    Private Declare PtrSafe Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As LongPtr)
#Else
    Private Declare Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)
#End If

Private Const TAUX_NORMAL As Double = 0.25
Private Const TAUX_REDUIT_PME As Double = 0.15
Private Const SEUIL_REDUIT As Double = 42500#
Private Const PLAFOND_CA_PME As Double = 10000000#
Private Const DEFAULT_REPO_ROOT As String = "C:\Users\eu\OneDrive\Desktop\fiscia-pro\fiscal-liberal"
Private Const LEGACY_REPO_ROOT As String = "C:\Users\eu\OneDrive\Desktop\fiscia-pro"
Private Const MARKETING_URL As String = "http://localhost:3101/"
Private Const LOGIN_URL As String = "http://localhost:3101/login"
Private Const REGISTER_URL As String = "http://localhost:3101/register"
Private Const APP_URL As String = "http://localhost:3100/"
Private Const LIASSE_URL As String = "http://localhost:3100/liasse"
Private Const API_HEALTH_URL As String = "http://localhost:8000/health"

Public Sub CalculerIS()
    Dim ws As Worksheet
    Dim benefice As Double
    Dim perte As Double
    Dim wi As Double
    Dim wg As Double
    Dim wm As Double
    Dim wn As Double
    Dim wv As Double
    Dim l8 As Double
    Dim caHT As Double
    Dim capitalPP As Boolean
    Dim resultatComptable As Double
    Dim totalReintegrations As Double
    Dim totalDeductions As Double
    Dim rfBrut As Double
    Dim rfNet As Double
    Dim tranche15 As Double
    Dim tranche25 As Double
    Dim isTotal As Double
    Dim acompte As Double
    Dim regime As String
    Dim pmeEligible As Boolean

    Set ws = ThisWorkbook.Worksheets("2058A_IS")

    benefice = NzDbl(ws.Range("B6").Value)
    perte = NzDbl(ws.Range("B7").Value)
    wi = NzDbl(ws.Range("B8").Value)
    wg = NzDbl(ws.Range("B9").Value)
    wm = NzDbl(ws.Range("B10").Value)
    wn = NzDbl(ws.Range("B11").Value)
    wv = NzDbl(ws.Range("B12").Value)
    l8 = NzDbl(ws.Range("B13").Value)
    caHT = NzDbl(ws.Range("B14").Value)
    capitalPP = ParseBooleanValue(ws.Range("B15").Value)

    resultatComptable = benefice - perte
    totalReintegrations = wi + wg + wm + wn + l8
    totalDeductions = wv
    rfBrut = resultatComptable + totalReintegrations - totalDeductions

    If rfBrut > 0 Then
        rfNet = rfBrut
    Else
        rfNet = 0
    End If

    If rfNet <= 0 Then
        tranche15 = 0
        tranche25 = 0
        isTotal = 0
        acompte = 0
        regime = "Deficit - pas d'IS du"
    Else
        pmeEligible = (caHT < PLAFOND_CA_PME And capitalPP)

        If pmeEligible Then
            tranche15 = WorksheetFunction.Min(rfNet, SEUIL_REDUIT)
            tranche25 = WorksheetFunction.Max(rfNet - SEUIL_REDUIT, 0)
            isTotal = RoundCurrency(tranche15 * TAUX_REDUIT_PME + tranche25 * TAUX_NORMAL)
            regime = "PME - Taux reduit Art. 219-I-b CGI"
        Else
            tranche15 = 0
            tranche25 = rfNet
            isTotal = RoundCurrency(rfNet * TAUX_NORMAL)
            regime = "Taux normal 25% - Art. 219 CGI"
        End If

        acompte = RoundCurrency(isTotal / 4)
    End If

    WriteCurrencyValue ws.Range("E8"), resultatComptable
    WriteCurrencyValue ws.Range("E9"), totalReintegrations
    WriteCurrencyValue ws.Range("E10"), totalDeductions
    WriteCurrencyValue ws.Range("E11"), rfBrut
    WriteCurrencyValue ws.Range("E12"), rfNet
    ws.Range("E13").Value = regime
    WriteCurrencyValue ws.Range("E14"), tranche15
    WriteCurrencyValue ws.Range("E15"), tranche25
    WriteCurrencyValue ws.Range("E16"), isTotal
    WriteCurrencyValue ws.Range("E17"), acompte
    ws.Range("E18").Value = "Reponse indicative. Toute decision fiscale engageante necessite l'analyse personnalisee d'un professionnel qualifie."
    ws.Range("E18").WrapText = True

End Sub

Public Sub EffacerSaisie()
    Dim ws As Worksheet

    Set ws = ThisWorkbook.Worksheets("2058A_IS")
    ws.Range("B4:B15").ClearContents
    ws.Range("E8:E18").ClearContents
    ws.Range("B5").Value = Format(DateSerial(Year(Date), 12, 31), "yyyy-mm-dd")
    ws.Range("B15").Value = "Oui"
End Sub

Public Sub Calculer2065()
    Dim ws As Worksheet
    Dim resultatComptable As Double
    Dim reintegrations As Double
    Dim deductions As Double
    Dim deficitsAnterieurs As Double
    Dim rfAvantDeficits As Double
    Dim rfApresDeficits As Double
    Dim regime As String
    Dim annexes As String
    Dim statut As String

    Set ws = ThisWorkbook.Worksheets("2065_2033")

    resultatComptable = NzDbl(ws.Range("B15").Value)
    reintegrations = NzDbl(ws.Range("B23").Value)
    deductions = NzDbl(ws.Range("B24").Value)
    deficitsAnterieurs = NzDbl(ws.Range("B25").Value)
    regime = LCase$(Trim$(CStr(ws.Range("B8").Value)))

    rfAvantDeficits = resultatComptable + reintegrations - deductions
    rfApresDeficits = rfAvantDeficits - deficitsAnterieurs

    If regime = "reel normal" Or regime = "reel_normal" Then
        annexes = "2065-SD, 2050 a 2057, 2058-A a C, 2059-A a G"
    Else
        annexes = "2065-SD, 2033-A a G, 2058-A a C, 2059-A/B"
    End If

    If Len(Trim$(CStr(ws.Range("B4").Value))) <> 9 Then
        statut = "Verifier le SIREN"
    ElseIf NzDbl(ws.Range("B9").Value) <= 0 Then
        statut = "Verifier le CA HT"
    Else
        statut = "Dossier pret pour transfert vers 2058-A"
    End If

    WriteCurrencyValue ws.Range("E8"), resultatComptable
    WriteCurrencyValue ws.Range("E9"), reintegrations
    WriteCurrencyValue ws.Range("E10"), deductions
    WriteCurrencyValue ws.Range("E11"), rfAvantDeficits
    WriteCurrencyValue ws.Range("E12"), rfApresDeficits
    ws.Range("E13").Value = annexes
    ws.Range("E14").Value = statut
    ws.Range("E15").Value = "Flux actif : 2065 + 2033 -> 2058-A -> IS"
    ws.Range("E16").Value = "Imports recommandes : Excel, CSV, JSON"
    ws.Range("E17").Value = "Controle capital PP : " & CStr(ws.Range("B12").Value)
End Sub

Public Sub Transferer2065Vers2058A()
    Dim ws2065 As Worksheet
    Dim ws2058 As Worksheet
    Dim resultatComptable As Double

    Set ws2065 = ThisWorkbook.Worksheets("2065_2033")
    Set ws2058 = ThisWorkbook.Worksheets("2058A_IS")

    resultatComptable = NzDbl(ws2065.Range("B15").Value)

    ws2058.Range("B4").Value = ws2065.Range("B4").Value
    ws2058.Range("B5").Value = ws2065.Range("B7").Value
    ws2058.Range("B14").Value = ws2065.Range("B9").Value
    ws2058.Range("B15").Value = ws2065.Range("B12").Value

    If resultatComptable >= 0 Then
        ws2058.Range("B6").Value = RoundCurrency(resultatComptable)
        ws2058.Range("B7").Value = 0
    Else
        ws2058.Range("B6").Value = 0
        ws2058.Range("B7").Value = RoundCurrency(Abs(resultatComptable))
    End If

    ws2058.Range("B11").Value = NzDbl(ws2065.Range("B23").Value)
    ws2058.Range("B12").Value = NzDbl(ws2065.Range("B24").Value)

    ws2058.Activate
End Sub

Public Sub Effacer2065()
    Dim ws As Worksheet

    Set ws = ThisWorkbook.Worksheets("2065_2033")
    ws.Range("B4:B25").ClearContents
    ws.Range("E8:E17").ClearContents
    ws.Range("B6").Value = Format(DateSerial(Year(Date), 1, 1), "yyyy-mm-dd")
    ws.Range("B7").Value = Format(DateSerial(Year(Date), 12, 31), "yyyy-mm-dd")
    ws.Range("B8").Value = "reel simplifie"
    ws.Range("B12").Value = "Oui"
    ws.Range("B13").Value = "Oui"
End Sub

Public Sub DemarrerPlateformeLocale()
    StartPlatformIfNeeded True
End Sub

Public Sub OuvrirSiteExact()
    EnsurePlatformAndOpen MARKETING_URL
End Sub

Public Sub OuvrirLoginExact()
    EnsurePlatformAndOpen LOGIN_URL
End Sub

Public Sub OuvrirRegisterExact()
    EnsurePlatformAndOpen REGISTER_URL
End Sub

Public Sub OuvrirAppExact()
    EnsurePlatformAndOpen APP_URL
End Sub

Public Sub OuvrirLiasseExact()
    EnsurePlatformAndOpen LIASSE_URL
End Sub

Public Sub AllerAccueil()
    ThisWorkbook.Worksheets("Accueil").Activate
End Sub

Public Sub AllerDashboard()
    ThisWorkbook.Worksheets("Dashboard").Activate
End Sub

Public Sub AllerCalculateur()
    ThisWorkbook.Worksheets("2058A_IS").Activate
End Sub

Public Sub Aller2065()
    ThisWorkbook.Worksheets("2065_2033").Activate
End Sub

Public Sub ActualiserDashboard()
    Dim wsDash As Worksheet
    Dim ws2058 As Worksheet
    Dim ws2065 As Worksheet
    Dim status2058 As String
    Dim status2065 As String

    Set wsDash = ThisWorkbook.Worksheets("Dashboard")
    Set ws2058 = ThisWorkbook.Worksheets("2058A_IS")
    Set ws2065 = ThisWorkbook.Worksheets("2065_2033")

    status2058 = "Pret a calculer"
    If Len(Trim$(CStr(ws2058.Range("E16").Value))) > 0 Then
        status2058 = "Dernier IS : " & CStr(ws2058.Range("E16").Text)
    End If

    status2065 = "Nouveau dossier"
    If Len(Trim$(CStr(ws2065.Range("E14").Value))) > 0 Then
        status2065 = CStr(ws2065.Range("E14").Value)
    End If

    wsDash.Range("B6").Value = "Modules actifs"
    wsDash.Range("B7").Value = "2058-A / IS"
    wsDash.Range("B8").Value = "2065 + 2033"
    wsDash.Range("E6").Value = "Etat"
    wsDash.Range("E7").Value = status2058
    wsDash.Range("E8").Value = status2065
    wsDash.Range("B11").Value = "Workflow"
    wsDash.Range("B12").Value = "Accueil -> Dashboard -> 2065 + 2033 -> 2058-A -> IS"
    wsDash.Range("B14").Value = "Promesse produit"
    wsDash.Range("B15").Value = "Import Excel/PDF, preparation 2065 + 2033, liasse 2058-A et calcul IS dans un meme fichier VBA."
    wsDash.Range("B15").WrapText = True
End Sub

Private Function NzDbl(ByVal sourceValue As Variant) As Double
    If IsError(sourceValue) Then
        NzDbl = 0
        Exit Function
    End If

    If IsNumeric(sourceValue) Then
        NzDbl = CDbl(sourceValue)
        Exit Function
    End If

    If Len(Trim$(CStr(sourceValue))) = 0 Then
        NzDbl = 0
        Exit Function
    End If

    NzDbl = CDbl(Replace(CStr(sourceValue), ",", "."))
End Function

Private Function ParseBooleanValue(ByVal sourceValue As Variant) As Boolean
    Dim normalized As String

    normalized = LCase$(Trim$(CStr(sourceValue)))
    ParseBooleanValue = (normalized = "oui" Or normalized = "true" Or normalized = "1" Or normalized = "yes")
End Function

Private Function RoundCurrency(ByVal sourceValue As Double) As Double
    RoundCurrency = WorksheetFunction.Round(sourceValue, 2)
End Function

Private Sub WriteCurrencyValue(ByVal target As Range, ByVal sourceValue As Double)
    target.Value = RoundCurrency(sourceValue)
    target.NumberFormat = "#,##0.00 [$EUR]"
End Sub

Private Sub EnsurePlatformAndOpen(ByVal targetUrl As String)
    StartPlatformIfNeeded False

    If Not WaitForUrl(targetUrl, 45) Then
        MsgBox "La plateforme locale demarre encore. Reessaie dans quelques secondes.", vbInformation, "FiscIA Pro"
        Exit Sub
    End If

    OpenUrlInChromiumApp targetUrl
End Sub

Private Sub StartPlatformIfNeeded(ByVal showMessage As Boolean)
    Dim repoRoot As String
    Dim logsFolder As String

    repoRoot = GetRepoRoot()
    logsFolder = GetLogsFolder(repoRoot)
    EnsureDirectory logsFolder

    If Not UrlResponds(MARKETING_URL) Then
        StartHiddenCommand repoRoot & "\marketing", "npm run dev", logsFolder & "\marketing-vba.log"
    End If

    If Not UrlResponds(APP_URL) Then
        StartHiddenCommand repoRoot & "\frontend", "npm run dev", logsFolder & "\frontend-vba.log"
    End If

    If Not UrlResponds(API_HEALTH_URL) Then
        StartHiddenCommand repoRoot, "python -m uvicorn fiscia.app:app --host 127.0.0.1 --port 8000", logsFolder & "\api-vba.log"
    End If

    If showMessage Then
        MsgBox "Demarrage de la plateforme FiscIA Pro lance. Le site exact sera disponible dans quelques secondes.", vbInformation, "FiscIA Pro"
    End If
End Sub

Private Function WaitForUrl(ByVal targetUrl As String, ByVal timeoutSeconds As Long) As Boolean
    Dim startedAt As Single

    startedAt = Timer

    Do
        If UrlResponds(targetUrl) Then
            WaitForUrl = True
            Exit Function
        End If

        DoEvents
        Sleep 1000

        If Timer < startedAt Then
            startedAt = Timer
        End If
    Loop While (Timer - startedAt) < timeoutSeconds

    WaitForUrl = False
End Function

Private Function UrlResponds(ByVal targetUrl As String) As Boolean
    Dim http As Object

    On Error GoTo CleanFail

    Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
    http.SetTimeouts 1000, 1000, 1000, 3000
    http.Open "GET", targetUrl, False
    http.Send

    UrlResponds = (http.Status >= 200 And http.Status < 500)
    Exit Function

CleanFail:
    UrlResponds = False
End Function

Private Sub OpenUrlInChromiumApp(ByVal targetUrl As String)
    Dim browserPath As String
    Dim shellObject As Object
    Dim commandText As String

    browserPath = GetChromiumPath()

    If Len(browserPath) = 0 Then
        ThisWorkbook.FollowHyperlink targetUrl
        Exit Sub
    End If

    commandText = Quote(browserPath) & " --app=" & Quote(targetUrl) & " --window-size=1440,960"
    Set shellObject = CreateObject("WScript.Shell")
    shellObject.Run commandText, 1, False
End Sub

Private Function GetChromiumPath() As String
    Dim candidates As Variant
    Dim item As Variant

    candidates = Array( _
        Environ$("ProgramFiles") & "\Google\Chrome\Application\chrome.exe", _
        Environ$("ProgramFiles(x86)") & "\Google\Chrome\Application\chrome.exe", _
        Environ$("LocalAppData") & "\Google\Chrome\Application\chrome.exe", _
        Environ$("ProgramFiles") & "\Microsoft\Edge\Application\msedge.exe", _
        Environ$("ProgramFiles(x86)") & "\Microsoft\Edge\Application\msedge.exe", _
        Environ$("LocalAppData") & "\Microsoft\Edge\Application\msedge.exe" _
    )

    For Each item In candidates
        If FileExists(CStr(item)) Then
            GetChromiumPath = CStr(item)
            Exit Function
        End If
    Next item

    GetChromiumPath = ""
End Function

Private Function GetRepoRoot() As String
    Dim workbookRoot As String

    workbookRoot = ThisWorkbook.Path

    If IsValidRepoRoot(workbookRoot) Then
        GetRepoRoot = workbookRoot
        Exit Function
    End If

    If IsValidRepoRoot(DEFAULT_REPO_ROOT) Then
        GetRepoRoot = DEFAULT_REPO_ROOT
        Exit Function
    End If

    If IsValidRepoRoot(LEGACY_REPO_ROOT) Then
        GetRepoRoot = LEGACY_REPO_ROOT
        Exit Function
    End If

    GetRepoRoot = workbookRoot
End Function

Private Function IsValidRepoRoot(ByVal candidatePath As String) As Boolean
    If Len(candidatePath) = 0 Then
        IsValidRepoRoot = False
        Exit Function
    End If

    IsValidRepoRoot = DirectoryExists(candidatePath & "\marketing") _
        And DirectoryExists(candidatePath & "\frontend") _
        And DirectoryExists(candidatePath & "\fiscia")
End Function

Private Function GetLogsFolder(ByVal repoRoot As String) As String
    If IsValidRepoRoot(repoRoot) Then
        GetLogsFolder = repoRoot & "\excel-vba\logs"
    Else
        GetLogsFolder = Environ$("USERPROFILE") & "\OneDrive\Desktop\fiscia-pro\excel-vba\logs"
    End If
End Function

Private Sub StartHiddenCommand(ByVal workingDirectory As String, ByVal commandText As String, ByVal logPath As String)
    Dim shellObject As Object
    Dim wrappedCommand As String

    EnsureDirectory GetParentFolder(logPath)
    wrappedCommand = "cmd /c cd /d " & Quote(workingDirectory) & " && " & commandText & " > " & Quote(logPath) & " 2>&1"

    Set shellObject = CreateObject("WScript.Shell")
    shellObject.Run wrappedCommand, 0, False
End Sub

Private Function GetParentFolder(ByVal targetPath As String) As String
    Dim separatorPosition As Long

    separatorPosition = InStrRev(targetPath, "\")
    If separatorPosition > 0 Then
        GetParentFolder = Left$(targetPath, separatorPosition - 1)
    Else
        GetParentFolder = targetPath
    End If
End Function

Private Sub EnsureDirectory(ByVal folderPath As String)
    Dim fileSystem As Object

    If Len(folderPath) = 0 Then
        Exit Sub
    End If

    Set fileSystem = CreateObject("Scripting.FileSystemObject")
    If Not fileSystem.FolderExists(folderPath) Then
        fileSystem.CreateFolder folderPath
    End If
End Sub

Private Function FileExists(ByVal filePath As String) As Boolean
    FileExists = (Len(Dir$(filePath)) > 0)
End Function

Private Function DirectoryExists(ByVal folderPath As String) As Boolean
    On Error Resume Next
    DirectoryExists = ((GetAttr(folderPath) And vbDirectory) = vbDirectory)
    If Err.Number <> 0 Then
        DirectoryExists = False
        Err.Clear
    End If
End Function

Private Function Quote(ByVal rawValue As String) As String
    Quote = Chr$(34) & rawValue & Chr$(34)
End Function
