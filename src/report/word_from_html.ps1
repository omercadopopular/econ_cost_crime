param(
    [Parameter(Mandatory = $true)][string]$HtmlPath,
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [Parameter(Mandatory = $true)][string]$MetadataPath,
    [Parameter(Mandatory = $true)][string]$PreviewPdfPath
)

$ErrorActionPreference = "Stop"
$word = $null
$document = $null
$missing = [System.Type]::Missing

try {
    $htmlResolved = (Resolve-Path -LiteralPath $HtmlPath).Path
    $outputResolved = [System.IO.Path]::GetFullPath($OutputPath)
    $previewResolved = [System.IO.Path]::GetFullPath($PreviewPdfPath)
    $metadata = Get-Content -LiteralPath $MetadataPath -Raw -Encoding UTF8 | ConvertFrom-Json

    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($htmlResolved, $false, $false)
    Write-Output "Opened HTML source"

    $linkedPictures = 0
    for ($index = $document.InlineShapes.Count; $index -ge 1; $index--) {
        $shape = $document.InlineShapes.Item($index)
        if ($shape.Type -eq 4) {
            $shape.LinkFormat.SavePictureWithDocument = $true
            $shape.LinkFormat.BreakLink()
            $linkedPictures++
        }
    }
    Write-Output "Embedded linked pictures: $linkedPictures"

    foreach ($footnote in $metadata.footnotes) {
        $range = $document.Content.Duplicate
        $find = $range.Find
        $find.ClearFormatting()
        $find.Text = [string]$footnote.marker
        $find.Forward = $true
        $find.Wrap = 0
        if (-not $find.Execute()) {
            throw "Footnote marker not found: $($footnote.marker)"
        }
        $range.Text = ""
        $range.Collapse(1)
        $null = $document.Footnotes.Add($range, $missing, [string]$footnote.text)
    }
    Write-Output "Inserted footnotes: $($metadata.footnotes.Count)"

    $tocRange = $document.Content.Duplicate
    $tocFind = $tocRange.Find
    $tocFind.ClearFormatting()
    $tocFind.Text = "[[TOC]]"
    $tocFind.Forward = $true
    $tocFind.Wrap = 0
    if (-not $tocFind.Execute()) {
        throw "TOC marker not found"
    }
    $tocRange.Text = ""
    $tocRange.Collapse(1)
    $null = $document.TablesOfContents.Add($tocRange, $true, 1, 4)
    Write-Output "Inserted table of contents"

    $marginPoints = $word.CentimetersToPoints(2.35)
    foreach ($section in $document.Sections) {
        $section.PageSetup.PaperSize = 7
        $section.PageSetup.TopMargin = $marginPoints
        $section.PageSetup.BottomMargin = $marginPoints
        $section.PageSetup.LeftMargin = $marginPoints
        $section.PageSetup.RightMargin = $marginPoints
        $footer = $section.Footers.Item(1)
        $footer.Range.ParagraphFormat.Alignment = 1
        $footer.Range.Text = ""
        $null = $footer.Range.Fields.Add($footer.Range, -1, "PAGE")
    }
    Write-Output "Formatted sections: $($document.Sections.Count)"

    $firstSection = $document.Sections.Item(1)
    $contentWidth = $firstSection.PageSetup.PageWidth - $firstSection.PageSetup.LeftMargin - $firstSection.PageSetup.RightMargin
    $contentHeight = $firstSection.PageSetup.PageHeight - $firstSection.PageSetup.TopMargin - $firstSection.PageSetup.BottomMargin
    $resizedPictures = 0
    foreach ($shape in $document.InlineShapes) {
        $shape.LockAspectRatio = -1
        if ($shape.Width -gt $contentWidth) {
            $shape.Width = $contentWidth
            $resizedPictures++
        }
        if ($shape.Height -gt $contentHeight) {
            $shape.Height = $contentHeight
            $resizedPictures++
        }
    }
    Write-Output "Resized oversized pictures: $resizedPictures"

    $document.Fields.Update() | Out-Null
    foreach ($toc in $document.TablesOfContents) {
        $toc.Update() | Out-Null
    }
    Write-Output "Updated fields"
    $document.SaveAs2($outputResolved, 16)
    Write-Output "Saved DOCX"
    $document.ExportAsFixedFormat($previewResolved, 17)
    Write-Output "Exported preview PDF"
    $document.Close($false)
    $document = $null
    $word.Quit()
    $word = $null
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
    }
    if ($null -ne $word) {
        $word.Quit()
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
