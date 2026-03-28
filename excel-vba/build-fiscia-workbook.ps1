param(
    [string]$OutputPath = "C:\Users\eu\OneDrive\Desktop\FiscIA.xlsm"
)

$ErrorActionPreference = "Stop"
$repoRoot = "C:\Users\eu\OneDrive\Desktop\fiscia-pro\fiscal-liberal"
$logPath = Join-Path $repoRoot "excel-vba\build.log"

function Write-BuildLog {
    param([string]$Message)
    Add-Content -Path $logPath -Value ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message)
}

function Set-RangeStyle {
    param(
        [Parameter(Mandatory = $true)]$Range,
        [int]$FontSize = 11,
        [switch]$Bold,
        [string]$HorizontalAlignment = "Left"
    )

    $Range.Font.Size = $FontSize
    $Range.Font.Bold = [bool]$Bold
    switch ($HorizontalAlignment) {
        "Center" { $Range.HorizontalAlignment = -4108 }
        "Right" { $Range.HorizontalAlignment = -4152 }
        default { $Range.HorizontalAlignment = -4131 }
    }
}

function Add-ActionButton {
    param(
        [Parameter(Mandatory = $true)]$Worksheet,
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][double]$Left,
        [Parameter(Mandatory = $true)][double]$Top,
        [Parameter(Mandatory = $true)][double]$Width,
        [Parameter(Mandatory = $true)][double]$Height,
        [Parameter(Mandatory = $true)][string]$MacroName
    )

    $shape = $Worksheet.Shapes.AddShape(1, $Left, $Top, $Width, $Height)
    $shape.TextFrame2.TextRange.Text = $Text
    $shape.TextFrame2.TextRange.Font.Size = 11
    $shape.TextFrame2.TextRange.Font.Bold = $true
    $shape.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = 16777215
    $shape.Fill.ForeColor.RGB = 14061772
    $shape.Line.ForeColor.RGB = 14061772
    $shape.OnAction = $MacroName
}

$excel = $null
$workbook = $null

try {
    Set-Content -Path $logPath -Value ""
    Write-BuildLog "build start"
    $modulePath = Join-Path $repoRoot "excel-vba\modules\FiscalCalculator.bas"
    $resolvedOutput = [System.IO.Path]::GetFullPath($OutputPath)
    $outputFolder = Split-Path -Path $resolvedOutput -Parent
    $currentYear = (Get-Date).Year

    if (-not (Test-Path $outputFolder)) {
        New-Item -ItemType Directory -Path $outputFolder | Out-Null
    }

    Write-BuildLog "excel create start"
    $excel = New-Object -ComObject Excel.Application
    Write-BuildLog "excel object created"
    $excel.DisplayAlerts = $false
    Write-BuildLog "excel alerts configured"

    $workbook = $excel.Workbooks.Add()
    Write-BuildLog "workbook added"

    Write-BuildLog "worksheet normalization start"
    while ($workbook.Worksheets.Count -lt 5) {
        $null = $workbook.Worksheets.Add()
    }
    while ($workbook.Worksheets.Count -gt 5) {
        $workbook.Worksheets.Item($workbook.Worksheets.Count).Delete()
    }
    Write-BuildLog "worksheet normalization complete"

    $wsHome = $workbook.Worksheets.Item(1)
    $wsDashboard = $workbook.Worksheets.Item(2)
    $ws2065 = $workbook.Worksheets.Item(3)
    $wsCalc = $workbook.Worksheets.Item(4)
    $wsInfo = $workbook.Worksheets.Item(5)

    $wsHome.Name = "Accueil"
    $wsDashboard.Name = "Dashboard"
    $ws2065.Name = "2065_2033"
    $wsCalc.Name = "2058A_IS"
    $wsInfo.Name = "Instructions"
    Write-BuildLog "worksheets prepared"

    $workbook.VBProject.VBComponents.Import($modulePath) | Out-Null
    Write-BuildLog "vba module imported"

    $thisWorkbookModule = $workbook.VBProject.VBComponents.Item("ThisWorkbook").CodeModule
    if ($thisWorkbookModule.CountOfLines -gt 0) {
        $thisWorkbookModule.DeleteLines(1, $thisWorkbookModule.CountOfLines)
    }
    $thisWorkbookModule.AddFromString(@"
Option Explicit

Private Sub Workbook_Open()
    On Error Resume Next
    OuvrirSiteExact
End Sub
"@)
    Write-BuildLog "workbook event injected"

    # Accueil
    $wsHome.Cells.Clear()
    $wsHome.Range("A1:J2").Merge()
    $wsHome.Range("A1").Value = "FiscIA Pro"
    Set-RangeStyle -Range $wsHome.Range("A1") -FontSize 26 -Bold -HorizontalAlignment Center
    $wsHome.Range("A3:J3").Merge()
    $wsHome.Range("A3").Value = "Le site exact dans Chrome ou Edge, plus les modules fiscaux dans le meme fichier Excel VBA"
    Set-RangeStyle -Range $wsHome.Range("A3") -FontSize 14 -Bold -HorizontalAlignment Center
    $wsHome.Range("A5:J5").Merge()
    $wsHome.Range("A5").Value = "Le rendu exactement identique au website est ouvert en mode application Chrome/Edge depuis ce classeur. Les modules 2065 + 2033 et 2058-A restent disponibles aussi en VBA."
    $wsHome.Range("A5").WrapText = $true
    Set-RangeStyle -Range $wsHome.Range("A5") -FontSize 12 -HorizontalAlignment Center

    $wsHome.Range("A7:C9").Merge()
    $wsHome.Range("A7").Value = "22 000+ experts-comptables"
    Set-RangeStyle -Range $wsHome.Range("A7") -FontSize 16 -Bold -HorizontalAlignment Center
    $wsHome.Range("D7:F9").Merge()
    $wsHome.Range("D7").Value = "3,5 M structures accompagnees"
    Set-RangeStyle -Range $wsHome.Range("D7") -FontSize 16 -Bold -HorizontalAlignment Center
    $wsHome.Range("G7:J9").Merge()
    $wsHome.Range("G7").Value = "1,16 M creations d'entreprises (2025)"
    Set-RangeStyle -Range $wsHome.Range("G7") -FontSize 16 -Bold -HorizontalAlignment Center

    $wsHome.Range("A11:J11").Merge()
    $wsHome.Range("A11").Value = "Experience web exacte + modules VBA"
    Set-RangeStyle -Range $wsHome.Range("A11") -FontSize 14 -Bold -HorizontalAlignment Center
    $wsHome.Range("A13:C15").Merge()
    $wsHome.Range("A13").Value = "Site exact"
    Set-RangeStyle -Range $wsHome.Range("A13") -FontSize 12 -Bold -HorizontalAlignment Center
    $wsHome.Range("D13:F15").Merge()
    $wsHome.Range("D13").Value = "Connexion / inscription exactes"
    Set-RangeStyle -Range $wsHome.Range("D13") -FontSize 12 -Bold -HorizontalAlignment Center
    $wsHome.Range("G13:H15").Merge()
    $wsHome.Range("G13").Value = "App web exacte"
    Set-RangeStyle -Range $wsHome.Range("G13") -FontSize 12 -Bold -HorizontalAlignment Center
    $wsHome.Range("I13:J15").Merge()
    $wsHome.Range("I13").Value = "Modules VBA"
    Set-RangeStyle -Range $wsHome.Range("I13") -FontSize 12 -Bold -HorizontalAlignment Center

    Add-ActionButton -Worksheet $wsHome -Text "Demarrer plateforme" -Left 35 -Top 330 -Width 170 -Height 34 -MacroName "DemarrerPlateformeLocale"
    Add-ActionButton -Worksheet $wsHome -Text "Ouvrir site exact" -Left 220 -Top 330 -Width 155 -Height 34 -MacroName "OuvrirSiteExact"
    Add-ActionButton -Worksheet $wsHome -Text "Login exact" -Left 390 -Top 330 -Width 120 -Height 34 -MacroName "OuvrirLoginExact"
    Add-ActionButton -Worksheet $wsHome -Text "Register exact" -Left 525 -Top 330 -Width 130 -Height 34 -MacroName "OuvrirRegisterExact"
    Add-ActionButton -Worksheet $wsHome -Text "App exacte" -Left 670 -Top 330 -Width 115 -Height 34 -MacroName "OuvrirAppExact"

    Add-ActionButton -Worksheet $wsHome -Text "Liasse web" -Left 35 -Top 372 -Width 115 -Height 32 -MacroName "OuvrirLiasseExact"
    Add-ActionButton -Worksheet $wsHome -Text "Dashboard VBA" -Left 165 -Top 372 -Width 135 -Height 32 -MacroName "AllerDashboard"
    Add-ActionButton -Worksheet $wsHome -Text "2065 + 2033 VBA" -Left 315 -Top 372 -Width 145 -Height 32 -MacroName "Aller2065"
    Add-ActionButton -Worksheet $wsHome -Text "2058-A / IS VBA" -Left 475 -Top 372 -Width 145 -Height 32 -MacroName "AllerCalculateur"

    $wsHome.Columns("A:J").ColumnWidth = 14
    $wsHome.Range("A1:J20").Interior.Color = 15925247
    $wsHome.Range("A7:J15").Borders.Weight = 2

    # Dashboard
    $wsDashboard.Cells.Clear()
    $wsDashboard.Range("A1:H2").Merge()
    $wsDashboard.Range("A1").Value = "Dashboard FiscIA Pro"
    Set-RangeStyle -Range $wsDashboard.Range("A1") -FontSize 22 -Bold -HorizontalAlignment Center
    $wsDashboard.Range("A4:H4").Merge()
    $wsDashboard.Range("A4").Value = "Vue d'ensemble du classeur VBA : modules, workflow et etat du dossier"
    Set-RangeStyle -Range $wsDashboard.Range("A4") -FontSize 12 -HorizontalAlignment Center
    $wsDashboard.Range("B6:E8").Interior.Color = 15794160
    $wsDashboard.Range("B10:G16").Interior.Color = 15925247
    $wsDashboard.Columns("A:H").ColumnWidth = 18
    $wsDashboard.Range("B6:G16").Borders.Weight = 2
    $wsDashboard.Range("B6").Value = "Modules actifs"
    $wsDashboard.Range("B7").Value = "2058-A / IS"
    $wsDashboard.Range("B8").Value = "2065 + 2033"
    $wsDashboard.Range("E6").Value = "Etat"
    $wsDashboard.Range("E7").Value = "Pret a calculer"
    $wsDashboard.Range("E8").Value = "Pret a preparer"
    $wsDashboard.Range("B11").Value = "Workflow"
    $wsDashboard.Range("B12").Value = "Accueil -> Dashboard -> 2065 + 2033 -> 2058-A -> IS"
    $wsDashboard.Range("B14").Value = "Promesse produit"
    $wsDashboard.Range("B15").Value = "Import Excel/PDF, preparation 2065 + 2033, liasse 2058-A et calcul IS dans un meme fichier VBA."
    $wsDashboard.Range("B15").WrapText = $true
    Add-ActionButton -Worksheet $wsDashboard -Text "Actualiser" -Left 40 -Top 70 -Width 120 -Height 30 -MacroName "ActualiserDashboard"
    Add-ActionButton -Worksheet $wsDashboard -Text "Vers 2065 + 2033" -Left 180 -Top 70 -Width 150 -Height 30 -MacroName "Aller2065"
    Add-ActionButton -Worksheet $wsDashboard -Text "Vers 2058-A / IS" -Left 350 -Top 70 -Width 150 -Height 30 -MacroName "AllerCalculateur"
    Add-ActionButton -Worksheet $wsDashboard -Text "Accueil" -Left 520 -Top 70 -Width 110 -Height 30 -MacroName "AllerAccueil"

    # 2065 + 2033
    $ws2065.Cells.Clear()
    $ws2065.Range("A1:H1").Merge()
    $ws2065.Range("A1").Value = "Preparation 2065 + 2033"
    Set-RangeStyle -Range $ws2065.Range("A1") -FontSize 20 -Bold -HorizontalAlignment Center
    $ws2065.Range("A3:B3").Merge()
    $ws2065.Range("A3").Value = "Bloc 2065"
    Set-RangeStyle -Range $ws2065.Range("A3") -FontSize 13 -Bold
    $ws2065.Range("D3:E3").Merge()
    $ws2065.Range("D3").Value = "Lecture fiscale"
    Set-RangeStyle -Range $ws2065.Range("D3") -FontSize 13 -Bold

    $labels2065 = @(
        "SIREN",
        "Denomination",
        "Exercice ouvert le",
        "Exercice clos le",
        "Regime d'imposition",
        "CA HT",
        "Capital social",
        "Effectif moyen",
        "Capital >= 75% PP (Oui/Non)",
        "Capital entierement libere (Oui/Non)",
        "Resultat comptable",
        "Achats marchandises",
        "Charges externes",
        "Impots et taxes",
        "Salaires",
        "Charges sociales",
        "Dotations amortissements",
        "Reintegrations fiscales",
        "Deductions fiscales",
        "Deficits anterieurs"
    )

    for ($i = 0; $i -lt $labels2065.Count; $i++) {
        $row = 4 + $i
        $ws2065.Cells.Item($row, 1).Value = $labels2065[$i]
        $ws2065.Cells.Item($row, 1).Font.Bold = $true
        $ws2065.Cells.Item($row, 2).Interior.Color = 16777215
        $ws2065.Cells.Item($row, 2).Borders.Weight = 2
    }

    $ws2065.Range("B6").Value = (Get-Date -Year $currentYear -Month 1 -Day 1 -Format "yyyy-MM-dd")
    $ws2065.Range("B7").Value = (Get-Date -Year $currentYear -Month 12 -Day 31 -Format "yyyy-MM-dd")
    $ws2065.Range("B8").Value = "reel simplifie"
    $ws2065.Range("B12").Value = "Oui"
    $ws2065.Range("B13").Value = "Oui"

    $resultLabels2065 = @(
        "Resultat comptable",
        "Reintegrations",
        "Deductions",
        "RF avant deficits",
        "RF apres deficits",
        "Annexes attendues",
        "Statut dossier",
        "Flux",
        "Imports"
    )

    for ($i = 0; $i -lt $resultLabels2065.Count; $i++) {
        $row = 8 + $i
        $ws2065.Cells.Item($row, 4).Value = $resultLabels2065[$i]
        $ws2065.Cells.Item($row, 4).Font.Bold = $true
        $ws2065.Cells.Item($row, 5).Interior.Color = 16053492
        $ws2065.Cells.Item($row, 5).Borders.Weight = 2
    }

    $ws2065.Columns("A").ColumnWidth = 30
    $ws2065.Columns("B").ColumnWidth = 18
    $ws2065.Columns("D").ColumnWidth = 22
    $ws2065.Columns("E:H").ColumnWidth = 18
    $ws2065.Range("A4:B25").Interior.Color = 15925247
    $ws2065.Range("D8:E17").Interior.Color = 15794160
    Add-ActionButton -Worksheet $ws2065 -Text "Calculer 2065" -Left 360 -Top 50 -Width 120 -Height 30 -MacroName "Calculer2065"
    Add-ActionButton -Worksheet $ws2065 -Text "Vers 2058-A" -Left 495 -Top 50 -Width 120 -Height 30 -MacroName "Transferer2065Vers2058A"
    Add-ActionButton -Worksheet $ws2065 -Text "Effacer" -Left 630 -Top 50 -Width 90 -Height 30 -MacroName "Effacer2065"
    Add-ActionButton -Worksheet $ws2065 -Text "Dashboard" -Left 735 -Top 50 -Width 100 -Height 30 -MacroName "AllerDashboard"

    # Calculateur
    $wsCalc.Cells.Clear()
    $wsCalc.Range("A1:G1").Merge()
    $wsCalc.Range("A1").Value = "Liasse 2058-A / Calcul IS"
    Set-RangeStyle -Range $wsCalc.Range("A1") -FontSize 20 -Bold -HorizontalAlignment Center
    $wsCalc.Range("A2:G2").Merge()
    $wsCalc.Range("A2").Value = "Workflow continu : Accueil -> Dashboard -> 2065 + 2033 -> 2058-A / IS"
    Set-RangeStyle -Range $wsCalc.Range("A2") -FontSize 11 -HorizontalAlignment Center

    $wsCalc.Range("A3:B3").Merge()
    $wsCalc.Range("A3").Value = "Saisie"
    Set-RangeStyle -Range $wsCalc.Range("A3") -FontSize 13 -Bold

    $labels = @(
        "SIREN",
        "Exercice clos le",
        "Benefice comptable",
        "Perte comptable",
        "WI - IS comptabilise",
        "WG - Amendes et penalites",
        "WM - Interets excedentaires",
        "WN - Reintegrations diverses",
        "WV - Regime mere-filiale",
        "L8 - QP 12%",
        "CA HT",
        "Capital >= 75% PP (Oui/Non)"
    )

    for ($i = 0; $i -lt $labels.Count; $i++) {
        $row = 4 + $i
        $wsCalc.Cells.Item($row, 1).Value = $labels[$i]
        $wsCalc.Cells.Item($row, 1).Font.Bold = $true
        $wsCalc.Cells.Item($row, 2).Interior.Color = 16777215
        $wsCalc.Cells.Item($row, 2).Borders.Weight = 2
    }

    $wsCalc.Range("B5").Value = "2025-12-31"
    $wsCalc.Range("B15").Value = "Oui"

    $wsCalc.Range("D3:E3").Merge()
    $wsCalc.Range("D3").Value = "Resultats"
    Set-RangeStyle -Range $wsCalc.Range("D3") -FontSize 13 -Bold

    $resultLabels = @(
        "Resultat comptable",
        "Total reintegrations",
        "Total deductions",
        "RF brut",
        "RF net",
        "Regime",
        "Tranche 15%",
        "Tranche 25%",
        "IS total",
        "Acompte trimestriel",
        "Disclaimer"
    )

    for ($i = 0; $i -lt $resultLabels.Count; $i++) {
        $row = 8 + $i
        $wsCalc.Cells.Item($row, 4).Value = $resultLabels[$i]
        $wsCalc.Cells.Item($row, 4).Font.Bold = $true
        $wsCalc.Cells.Item($row, 5).Interior.Color = 16053492
        $wsCalc.Cells.Item($row, 5).Borders.Weight = 2
    }

    $wsCalc.Range("E18:G19").Merge()
    $wsCalc.Range("E18:G19").WrapText = $true
    $wsCalc.Range("E18:G19").VerticalAlignment = -4160
    $wsCalc.Range("E18:G19").HorizontalAlignment = -4131

    $wsCalc.Columns("A").ColumnWidth = 28
    $wsCalc.Columns("B").ColumnWidth = 18
    $wsCalc.Columns("D").ColumnWidth = 24
    $wsCalc.Columns("E:G").ColumnWidth = 18

    Add-ActionButton -Worksheet $wsCalc -Text "Calculer IS" -Left 360 -Top 55 -Width 120 -Height 30 -MacroName "CalculerIS"
    Add-ActionButton -Worksheet $wsCalc -Text "Effacer" -Left 490 -Top 55 -Width 100 -Height 30 -MacroName "EffacerSaisie"
    Add-ActionButton -Worksheet $wsCalc -Text "Dashboard" -Left 600 -Top 55 -Width 100 -Height 30 -MacroName "AllerDashboard"
    Add-ActionButton -Worksheet $wsCalc -Text "2065 + 2033" -Left 710 -Top 55 -Width 110 -Height 30 -MacroName "Aller2065"

    $validation = $wsCalc.Range("B15").Validation
    $validation.Delete()
    $validation.Add(3, 1, 1, "Oui,Non") | Out-Null

    $validation2065Capital = $ws2065.Range("B12").Validation
    $validation2065Capital.Delete()
    $validation2065Capital.Add(3, 1, 1, "Oui,Non") | Out-Null

    $validation2065Libere = $ws2065.Range("B13").Validation
    $validation2065Libere.Delete()
    $validation2065Libere.Add(3, 1, 1, "Oui,Non") | Out-Null

    $validation2065Regime = $ws2065.Range("B8").Validation
    $validation2065Regime.Delete()
    $validation2065Regime.Add(3, 1, 1, "reel simplifie,reel normal") | Out-Null

    $wsCalc.Range("A4:B15").Interior.Color = 15925247
    $wsCalc.Range("D8:E19").Interior.Color = 15794160

    # Instructions
    $wsInfo.Cells.Clear()
    $wsInfo.Range("A1:H1").Merge()
    $wsInfo.Range("A1").Value = "Instructions d'utilisation"
    Set-RangeStyle -Range $wsInfo.Range("A1") -FontSize 18 -Bold -HorizontalAlignment Center
    $wsInfo.Range("A3").Value = "1. Commencez sur Accueil ou Dashboard."
    $wsInfo.Range("A4").Value = "2. Pour le rendu exact du website, cliquez sur Demarrer plateforme puis sur Ouvrir site exact, Login exact, Register exact ou App exacte."
    $wsInfo.Range("A5").Value = "3. Pour le workflow full VBA, preparez le dossier dans la feuille 2065_2033."
    $wsInfo.Range("A6").Value = "4. Cliquez sur Calculer 2065 puis sur Vers 2058-A."
    $wsInfo.Range("A7").Value = "5. Finalisez les retraitements dans 2058A_IS et cliquez sur Calculer IS."
    $wsInfo.Range("A8").Value = "6. Le taux reduit PME 15% est applique sur les premiers 42 500 EUR si le CA HT est inferieur a 10 000 000 EUR et si le capital est detenu a 75% par des personnes physiques."
    $wsInfo.Range("A9").Value = "7. Cette version est indicative et doit etre revue par un professionnel qualifie."
    $wsInfo.Range("A10").Value = "Feuilles disponibles"
    $wsInfo.Range("A10").Font.Bold = $true
    $wsInfo.Range("A11").Value = "- Accueil : lanceur du site exact et des modules VBA"
    $wsInfo.Range("A12").Value = "- Dashboard : vue d'ensemble"
    $wsInfo.Range("A13").Value = "- 2065_2033 : preparation dossier IS"
    $wsInfo.Range("A14").Value = "- 2058A_IS : calcul fiscal final"
    $wsInfo.Columns("A:H").ColumnWidth = 24
    $wsInfo.Range("A3:A14").WrapText = $true

    if (Test-Path $resolvedOutput) {
        Remove-Item $resolvedOutput -Force
        Write-BuildLog "existing output removed"
    }

    $fileFormatXlsm = 52
    Write-BuildLog "save start"
    $workbook.SaveAs($resolvedOutput, $fileFormatXlsm)
    Write-BuildLog "save complete"
    $null = $workbook.Close($true)
    Write-BuildLog "workbook closed"
    $null = $excel.Quit()
    Write-BuildLog "excel quit"
    $workbook = $null
    $excel = $null

    Write-Output "Workbook generated: $resolvedOutput"
}
finally {
    if ($workbook -ne $null) {
        try { $workbook.Close($false) } catch {}
    }
    if ($excel -ne $null) {
        try { $excel.Quit() } catch {}
    }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
