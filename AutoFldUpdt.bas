Attribute VB_Name = "Module1"
Option Explicit
' Word macro to automatically update field links to other files
' Created by Paul Edstein (aka macropod). Posted at:
' http://windowssecrets.com/forums/showthread.php/154379-Word-Fields-and-Relative-Paths-to-External-Files
Dim TrkStatus As Boolean      ' Track Changes flag
Dim Pwd As String ' String variable to hold passwords for protected documents
Dim pState As Boolean ' Document protection state flag

Sub AutoOpen()
' This routine runs whenever the document is opened.
' It calls on the others to do the real work.
'
' Prepare the environment.
With ActiveDocument
  ' Insert your document's password between the double quotes on the next line
  Pwd = ""
  ' Initialise the protection state
  pState = False
  ' If the document is protected, unprotect it
  If .ProtectionType <> wdNoProtection Then
    ' Update the protection state
    pState = True
    ' Unprotect the document
    .Unprotect Pwd
  End If
  Call MacroEntry
  ' Most of the work is done by this routine.
  Call UpdateFields
  ' Go to the start of the document
  Selection.HomeKey Unit:=wdStory
  ' Clean up and exit.
  Call MacroExit
  ' If the document was protected, reprotect it, preserving any formfield contents
  If pState = True Then .Protect wdAllowOnlyFormFields, Noreset:=True, Password:=Pwd
  ' Set the saved status of the document to true, so that changes via
  ' this code are ignored. Since the same changes will be made the
  ' next time the document is opened, saving them doesn't matter.
  .Saved = True
End With
End Sub

Private Sub MacroEntry()
' Store current Track Changes status, then switch off temporarily.
With ActiveDocument
    TrkStatus = .TrackRevisions
    .TrackRevisions = False
End With
' Turn Off Screen Updating temporarily.
Application.ScreenUpdating = False
End Sub

Private Sub MacroExit()
' Restore original Track Changes status
ActiveDocument.TrackRevisions = TrkStatus
' Restore Screen Updating
Application.ScreenUpdating = True
End Sub

Private Sub UpdateFields()
' This routine sets the new path for external links, pointing them to the current folder.
Dim Rng As Range, Fld As Field, Shp As Shape, iShp As InlineShape, i As Long
Dim OldPath As String, NewPath As String, Parent As String, Child As String, StrTmp As String
' Set the new path.
' If your files are always in a folder whose path bracnhes off, one or more levels above the current
' folder, replace the second '0' on the next line with the number of levels above the current folder.
For i = 0 To UBound(Split(ActiveDocument.Path, "\")) - 0
  Parent = Parent & Split(ActiveDocument.Path, "\")(i) & "\"
Next i
' If your files are in a Child folder below the (new) parent folder, add the Child folder's
' path from the parent (minus the leading & trailing "\" path separators) on the next line.
Child = ""
NewPath = Parent & Child
' Strip off any trailing path separators.
While Right(NewPath, 1) = "\"
  NewPath = Left(NewPath, Len(NewPath) - 1)
Wend
NewPath = NewPath & "\"
' Go through all story ranges in the document.
With ThisDocument
  For Each Rng In .StoryRanges
    ' Go through the shapes in the story range.
    For Each Shp In Rng.ShapeRange
      With Shp
        ' Skip over shapes that don't have links to external files.
        If Not .LinkFormat Is Nothing Then
          With .LinkFormat
            OldPath = Left(.SourceFullName, InStrRev(.SourceFullName, "\"))
            ' Replace the link to the external file if it differs.
            If OldPath <> NewPath Then
              .SourceFullName = Replace(.SourceFullName, OldPath, NewPath)
              On Error Resume Next
              .AutoUpdate = False
              On Error GoTo 0
            End If
          End With
        End If
      End With
    Next Shp
    ' Go through the inlineshapes in the story range.
    For Each iShp In Rng.InlineShapes
      With iShp
        ' Skip over inlineshapes that don't have links to external files.
        If Not .LinkFormat Is Nothing Then
          With .LinkFormat
            OldPath = Left(.SourceFullName, InStrRev(.SourceFullName, "\"))
            ' Replace the link to the external file if it differs.
            If OldPath <> NewPath Then
              .SourceFullName = Replace(.SourceFullName, OldPath, NewPath)
              On Error Resume Next
              .AutoUpdate = False
              On Error GoTo 0
            End If
          End With
        End If
      End With
    Next iShp
    ' Go through the fields in the story range.
    For Each Fld In Rng.Fields
      With Fld
        ' Skip over fields that don't have links to external files.
        If Not .LinkFormat Is Nothing Then
          With .LinkFormat
            OldPath = Left(.SourceFullName, InStrRev(.SourceFullName, "\"))
            ' Replace the link to the external file if it differs.
            If OldPath <> NewPath Then
              .SourceFullName = Replace(.SourceFullName, OldPath, NewPath)
              On Error Resume Next
              .AutoUpdate = False
              On Error GoTo 0
            End If
          End With
        End If
      End With
    Next Fld
  Next Rng
  .Save
End With
End Sub

