VICKY ALBUM STUDIO CLASSIC
==========================
Naya classic-look wedding album designer starter project for Windows 10/11.

FEATURES INCLUDED IN THIS STARTER:
- Classic maroon + antique-gold interface
- Multiple album pages and sizes (12x36, 12x18, 18x24, 24x36)
- Import common photo formats: JPG/JPEG, PNG, BMP, TIFF, WEBP (availability depends on Pillow decoder)
- Drag photos/text on the page
- Five basic wedding title/background templates
- Auto-layout photos
- Add/edit text, reorder/delete selected objects
- Save/open project (.vkas)
- Export current page as JPG and all pages as PDF
- Photoshop CS3 launch button: exports current page as flattened JPG and opens it with the chosen Photoshop.exe

IMPORTANT HONEST LIMITS:
- This is a new starter project, not a complete HStock Album replacement yet.
- It is not yet a fully tested commercial-grade album editor.
- Photoshop CS3 integration currently opens a flattened JPG page. It does not yet create a fully layered PSD project.
- For PSD files, best compatibility is to open them in Photoshop CS3 and save/export a JPG or TIFF, then import that image here. The app's main supported input formats are JPG, PNG, BMP, TIFF and WEBP.
- Exported pixel dimensions are design-canvas dimensions; verify actual print size and DPI in your print workflow before production.
- Test on the target Windows 10/11 machine before using for paid client work.

RUN ON WINDOWS 10/11:
1. Install Python 3.11 or 3.12.
2. Open Command Prompt in this folder.
3. Run: py -m pip install -r requirements.txt
4. Run: py app.py

BUILD EXE:
1. Run build_windows.bat, or use:
   py -m pip install pyinstaller
   py -m PyInstaller --noconfirm --onefile --windowed --name VickyAlbumStudioClassic app.py
2. EXE will be created in the dist folder.

PHOTOSHOP CS3:
1. In the right panel, click Browse Photoshop EXE.
2. Select Photoshop.exe (commonly in Adobe Photoshop CS3 folder).
3. Click Edit in Photoshop CS3. The current album page is exported as JPG and opened in CS3.
