import json, os, sys, subprocess, shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont

APP_NAME = 'Vicky Album Studio'
BASE = Path(__file__).resolve().parent
PROJECT_EXT = '.vkas'

class AlbumStudio:
    def __init__(self, root):
        self.root = root
        root.title('Vicky Album Studio Classic — Wedding Album Designer')
        root.geometry('1360x860')
        root.minsize(980, 650)
        self.pages = [{'size':'12x36', 'background':'#f6efe2', 'items':[]}]
        self.page_index = 0
        self.selected = None
        self.drag_state = None
        self.preview_scale = 1.0
        self.canvas_w, self.canvas_h = 1080, 360
        self.project_path = None
        self.photo_refs = []
        self._style()
        self._build_ui()
        self.draw_page()

    @property
    def page(self): return self.pages[self.page_index]

    def _style(self):
        s=ttk.Style()
        try: s.theme_use('clam')
        except: pass
        s.configure('TFrame', background='#eee6d8')
        s.configure('TLabel', background='#eee6d8', foreground='#33231d', font=('Segoe UI', 9))
        s.configure('Header.TLabel', background='#3b1e25', foreground='#f4d99a', font=('Georgia', 16, 'bold'))
        s.configure('TButton', padding=6, background='#e0d1b8', foreground='#33231d', font=('Segoe UI', 9, 'bold'))
        s.map('TButton', background=[('active','#c5a15a')])
        s.configure('TCombobox', padding=4)

    def _build_ui(self):
        top=ttk.Frame(self.root, padding=10); top.pack(fill='x'); top.configure(style='TFrame')
        banner=tk.Label(top, text='  VICKY ALBUM STUDIO CLASSIC  ', bg='#3b1e25', fg='#f4d99a', font=('Georgia',16,'bold'), padx=10, pady=8); banner.pack(side='left', padx=(0,14))
        for label, cmd in [('New',self.new_project),('Open Project',self.open_project),('Save Project',self.save_project),('Add Photo',self.add_photo),('Add Text',self.add_text),('Template',self.apply_template),('Export JPG',self.export_jpg),('Export PDF',self.export_pdf),('Edit in Photoshop CS3',self.open_photoshop)]:
            ttk.Button(top,text=label,command=cmd).pack(side='left', padx=2)
        body=ttk.Frame(self.root, padding=6); body.pack(fill='both',expand=True,padx=8,pady=(0,8))
        left=ttk.Frame(body,width=190,padding=8); left.pack(side='left',fill='y')
        ttk.Label(left,text='ALBUM PAGES',font=('Segoe UI',11,'bold')).pack(anchor='w')
        self.page_list=tk.Listbox(left,height=15,exportselection=False); self.page_list.pack(fill='x',pady=6)
        self.page_list.bind('<<ListboxSelect>>',self.on_page_select)
        row=ttk.Frame(left); row.pack(fill='x')
        ttk.Button(row,text='+ Page',command=self.add_page).pack(side='left',fill='x',expand=True)
        ttk.Button(row,text='− Page',command=self.remove_page).pack(side='left',fill='x',expand=True,padx=(4,0))
        ttk.Separator(left).pack(fill='x',pady=10)
        ttk.Label(left,text='PAGE SIZE',font=('Segoe UI',10,'bold')).pack(anchor='w')
        self.size_var=tk.StringVar(value='12x36')
        ttk.Combobox(left,textvariable=self.size_var,values=['12x36','12x18','18x24','24x36','Custom'],state='readonly').pack(fill='x',pady=5)
        ttk.Button(left,text='Apply Size',command=self.apply_size).pack(fill='x')
        ttk.Label(left,text='SELECTED OBJECT',font=('Segoe UI',10,'bold')).pack(anchor='w',pady=(14,4))
        ttk.Button(left,text='Bring Forward',command=lambda:self.reorder(1)).pack(fill='x',pady=2)
        ttk.Button(left,text='Send Backward',command=lambda:self.reorder(-1)).pack(fill='x',pady=2)
        ttk.Button(left,text='Delete Object',command=self.delete_selected).pack(fill='x',pady=2)
        ttk.Button(left,text='Change Background',command=self.change_background).pack(fill='x',pady=2)
        center=ttk.Frame(body); center.pack(side='left',fill='both',expand=True,padx=8)
        ttk.Label(center,text='CLASSIC STUDIO  •  Click an object, then drag to reposition',foreground='#6b4d3e').pack(anchor='w',pady=(2,8))
        self.canvas=tk.Canvas(center,bg='#4a4140',highlightthickness=2,highlightbackground='#c5a15a')
        self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<Button-1>',self.mouse_down); self.canvas.bind('<B1-Motion>',self.mouse_move); self.canvas.bind('<ButtonRelease-1>',self.mouse_up)
        right=ttk.Frame(body,width=220,padding=8); right.pack(side='right',fill='y')
        ttk.Label(right,text='QUICK TOOLS',font=('Segoe UI',11,'bold')).pack(anchor='w')
        ttk.Button(right,text='Auto Layout Photos',command=self.auto_layout).pack(fill='x',pady=(8,3))
        ttk.Button(right,text='Wedding Template 1',command=lambda:self.template(1)).pack(fill='x',pady=3)
        ttk.Button(right,text='Wedding Template 2',command=lambda:self.template(2)).pack(fill='x',pady=3)
        ttk.Button(right,text='Wedding Template 3',command=lambda:self.template(3)).pack(fill='x',pady=3)
        ttk.Button(right,text='Royal Gold Template',command=lambda:self.template(4)).pack(fill='x',pady=3)
        ttk.Button(right,text='Classic Maroon Template',command=lambda:self.template(5)).pack(fill='x',pady=3)
        ttk.Separator(right).pack(fill='x',pady=10)
        ttk.Label(right,text='Object settings',font=('Segoe UI',10,'bold')).pack(anchor='w')
        ttk.Label(right,text='Text content:').pack(anchor='w',pady=(8,0))
        self.text_var=tk.StringVar()
        ttk.Entry(right,textvariable=self.text_var).pack(fill='x',pady=3)
        ttk.Button(right,text='Update Selected Text',command=self.update_text).pack(fill='x')
        ttk.Label(right,text='Photo / text size:').pack(anchor='w',pady=(10,0))
        self.scale_var=tk.IntVar(value=100)
        ttk.Scale(right,from_=30,to=220,variable=self.scale_var,command=self.scale_selected).pack(fill='x',pady=3)
        ttk.Label(right,text='Photoshop CS3 path (optional):').pack(anchor='w',pady=(12,0))
        self.ps_path_var=tk.StringVar(value='')
        ttk.Entry(right,textvariable=self.ps_path_var).pack(fill='x',pady=3)
        ttk.Button(right,text='Browse Photoshop EXE',command=self.browse_ps).pack(fill='x')
        self.status=tk.StringVar(value='Classic Studio ready — add photos, choose a wedding layout, then save your project.')
        ttk.Label(self.root,textvariable=self.status,relief='sunken',anchor='w',padding=5).pack(fill='x',side='bottom')
        self.refresh_page_list()

    def _dims(self, size=None):
        size=size or self.page.get('size','12x36')
        if size=='12x36': return (1080,360)
        if size=='12x18': return (540,360)
        if size=='18x24': return (480,360)
        if size=='24x36': return (540,360)
        return (1080,360)

    def refresh_page_list(self):
        self.page_list.delete(0,'end')
        for i,p in enumerate(self.pages): self.page_list.insert('end',f'Page {i+1}  •  {p.get("size","12x36")}')
        self.page_list.selection_clear(0,'end'); self.page_list.selection_set(self.page_index)

    def draw_page(self):
        self.canvas.delete('all'); self.photo_refs=[]
        self.root.update_idletasks()
        cw=max(self.canvas.winfo_width(),400); ch=max(self.canvas.winfo_height(),250)
        aw,ah=self._dims(); scale=min((cw-30)/aw,(ch-30)/ah)
        self.preview_scale=scale; w=int(aw*scale); h=int(ah*scale)
        self.origin=((cw-w)//2,(ch-h)//2)
        x0,y0=self.origin
        bg=self.page.get('background','#f7f1e8')
        self.canvas.create_rectangle(x0,y0,x0+w,y0+h,fill=bg,outline='#9b8d7a',width=2,tags=('page',))
        for i,item in enumerate(self.page['items']):
            x=x0+item.get('x',0)*scale; y=y0+item.get('y',0)*scale
            if item['type']=='photo':
                try:
                    im=Image.open(item['path']).convert('RGB')
                    iw=max(10,int(item.get('w',240)*scale)); ih=max(10,int(item.get('h',180)*scale))
                    im.thumbnail((iw,ih),Image.Resampling.LANCZOS)
                    photo=ImageTk.PhotoImage(im); self.photo_refs.append(photo)
                    self.canvas.create_image(x,y,image=photo,anchor='nw',tags=(f'obj{i}','object'))
                    self.canvas.create_rectangle(x,y,x+im.width,y+im.height,outline='#c5a15a' if self.selected==i else '#777',width=3 if self.selected==i else 1,tags=(f'obj{i}','object'))
                except Exception: pass
            elif item['type']=='text':
                size=max(8,int(item.get('font_size',40)*scale))
                self.canvas.create_text(x,y,text=item.get('text','Text'),anchor='nw',fill=item.get('color','#4b1724'),font=('Georgia',size,'bold'),tags=(f'obj{i}','object'))
                if self.selected==i: self.canvas.create_rectangle(x-3,y-3,x+240*scale,y+55*scale,outline='#c5a15a',width=2,tags=(f'obj{i}','object'))
        self.refresh_page_list()

    def mouse_down(self,e):
        found=self.canvas.find_overlapping(e.x,e.y,e.x,e.y)
        idx=None
        for item_id in reversed(found):
            tags=self.canvas.gettags(item_id)
            for tag in tags:
                if tag.startswith('obj'):
                    try: idx=int(tag[3:]); break
                    except: pass
            if idx is not None: break
        self.selected=idx
        if idx is not None: self.drag_state=(e.x,e.y,self.page['items'][idx].get('x',0),self.page['items'][idx].get('y',0))
        else: self.drag_state=None
        self.draw_page()

    def mouse_move(self,e):
        if self.drag_state is None or self.selected is None:return
        sx,sy,ox,oy=self.drag_state; sc=max(self.preview_scale,0.01)
        item=self.page['items'][self.selected]; item['x']=max(0,ox+(e.x-sx)/sc); item['y']=max(0,oy+(e.y-sy)/sc)
        self.draw_page()

    def mouse_up(self,e): self.drag_state=None
    def on_page_select(self,e):
        s=self.page_list.curselection()
        if s: self.page_index=s[0]; self.selected=None; self.size_var.set(self.page.get('size','12x36')); self.draw_page()

    def add_photo(self):
        paths=filedialog.askopenfilenames(title='Choose photos',filetypes=[('Photo files','*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.webp'),('JPEG','*.jpg *.jpeg'),('PNG','*.png'),('TIFF','*.tif *.tiff'),('All files','*.*')])
        if not paths:return
        for p in paths:
            self.page['items'].append({'type':'photo','path':p,'x':40+(len(self.page['items'])%4)*210,'y':35+(len(self.page['items'])//4)*100,'w':220,'h':160})
        self.selected=len(self.page['items'])-1; self.status.set(f'{len(paths)} photo(s) added. Drag them to position.'); self.draw_page()

    def add_text(self):
        txt=simpledialog.askstring('Add text','Enter name, date, or title:')
        if txt:
            self.page['items'].append({'type':'text','text':txt,'x':50,'y':50,'font_size':42,'color':'#6b2036'})
            self.selected=len(self.page['items'])-1; self.text_var.set(txt); self.draw_page()

    def add_page(self):
        self.pages.append({'size':self.page.get('size','12x36'),'background':'#f6efe2','items':[]}); self.page_index=len(self.pages)-1; self.selected=None; self.draw_page(); self.status.set('New page added.')
    def remove_page(self):
        if len(self.pages)==1: messagebox.showinfo('Page','Project mein kam se kam ek page rehna chahiye.'); return
        del self.pages[self.page_index]; self.page_index=max(0,self.page_index-1); self.selected=None; self.draw_page()
    def apply_size(self): self.page['size']=self.size_var.get(); self.draw_page()
    def change_background(self):
        c=tk.colorchooser.askcolor(title='Choose page background') if hasattr(tk,'colorchooser') else None
        if c and c[1]: self.page['background']=c[1]; self.draw_page()
        else:
            from tkinter import colorchooser
            c=colorchooser.askcolor(title='Choose page background')
            if c and c[1]: self.page['background']=c[1]; self.draw_page()
    def delete_selected(self):
        if self.selected is not None:
            del self.page['items'][self.selected]; self.selected=None; self.draw_page()
    def reorder(self,d):
        i=self.selected
        if i is None:return
        j=max(0,min(len(self.page['items'])-1,i+d))
        self.page['items'][i],self.page['items'][j]=self.page['items'][j],self.page['items'][i]; self.selected=j; self.draw_page()
    def update_text(self):
        if self.selected is not None and self.page['items'][self.selected]['type']=='text': self.page['items'][self.selected]['text']=self.text_var.get(); self.draw_page()
    def scale_selected(self,v=None):
        if self.selected is None:return
        item=self.page['items'][self.selected]; factor=float(self.scale_var.get())/100
        if item['type']=='photo': item['w']=max(30,240*factor); item['h']=max(25,180*factor)
        else: item['font_size']=max(8,42*factor)
        self.draw_page()
    def template(self,n):
        bg=['#f6efe2','#fff8ef','#f1e3e5'][n-1]; self.page['background']=bg
        if n==1: self.page['items'].append({'type':'text','text':'Wedding Memories','x':40,'y':20,'font_size':40,'color':'#7c263c'})
        elif n==2:
            self.page['items'].append({'type':'text','text':'Forever Together','x':35,'y':20,'font_size':38,'color':'#8a5a24'})
            self.page['items'].append({'type':'text','text':'The Wedding Day','x':35,'y':75,'font_size':20,'color':'#5b3a2b'})
        elif n==3: self.page['items'].append({'type':'text','text':'Our Love Story','x':35,'y':25,'font_size':42,'color':'#6b2036'})
        elif n==4:
            self.page['background']='#f5ead2'; self.page['items'].append({'type':'text','text':'ROYAL WEDDING','x':35,'y':22,'font_size':42,'color':'#8a6428'})
        else:
            self.page['background']='#f0e0df'; self.page['items'].append({'type':'text','text':'Wedding Memories','x':35,'y':22,'font_size':42,'color':'#702638'})
        self.selected=len(self.page['items'])-1; self.draw_page(); self.status.set(f'Classic wedding template {n} applied. Add your photos.')
    def apply_template(self):
        n=simpledialog.askinteger('Template','Choose template number: 1 to 5',minvalue=1,maxvalue=5)
        if n:self.template(n)
    def auto_layout(self):
        photos=[it for it in self.page['items'] if it['type']=='photo']
        if not photos: messagebox.showinfo('Auto Layout','Pehle Add Photo se photos add karein.'); return
        count=len(photos); cols=2 if count<=4 else 3; rows=(count+cols-1)//cols
        cellw= (self._dims()[0]-40)/cols; cellh=(self._dims()[1]-70)/rows
        for k,it in enumerate(photos):
            it['x']=20+(k%cols)*cellw; it['y']=45+(k//cols)*cellh; it['w']=cellw-15; it['h']=cellh-15
        self.draw_page(); self.status.set('Auto layout applied. You can still drag each photo.')

    def render_page(self, page):
        w,h=self._dims(page.get('size','12x36')); im=Image.new('RGB',(w,h),page.get('background','#f7f1e8'))
        d=ImageDraw.Draw(im)
        for item in page.get('items',[]):
            x=int(item.get('x',0)); y=int(item.get('y',0))
            if item['type']=='photo':
                try:
                    p=Image.open(item['path']).convert('RGB'); p.thumbnail((int(item.get('w',220)),int(item.get('h',160))),Image.Resampling.LANCZOS); im.paste(p,(x,y)); d.rectangle([x,y,x+p.width,y+p.height],outline='#c5a15a',width=3)
                except Exception: pass
            elif item['type']=='text':
                try: font=ImageFont.truetype('arial.ttf',int(item.get('font_size',40)))
                except: font=ImageFont.load_default()
                d.text((x,y),item.get('text','Text'),fill=item.get('color','#4b1724'),font=font)
        return im
    def export_jpg(self):
        path=filedialog.asksaveasfilename(defaultextension='.jpg',filetypes=[('JPEG image','*.jpg')],initialfile=f'Album_Page_{self.page_index+1}.jpg')
        if path:
            self.render_page(self.page).save(path,'JPEG',quality=95,dpi=(300,300)); self.status.set('JPG exported at 300 DPI metadata.')
    def export_pdf(self):
        path=filedialog.asksaveasfilename(defaultextension='.pdf',filetypes=[('PDF document','*.pdf')],initialfile='Wedding_Album.pdf')
        if path:
            imgs=[self.render_page(p).convert('RGB') for p in self.pages]
            if imgs: imgs[0].save(path,save_all=True,append_images=imgs[1:],resolution=300.0); self.status.set(f'PDF exported: {len(imgs)} page(s).')
    def save_project(self):
        path=self.project_path or filedialog.asksaveasfilename(defaultextension=PROJECT_EXT,filetypes=[('Vicky Album project','*.vkas')])
        if not path:return
        try:
            with open(path,'w',encoding='utf-8') as f: json.dump({'app':'Vicky Album Studio','version':1,'pages':self.pages,'ps_path':self.ps_path_var.get()},f,ensure_ascii=False,indent=2)
            self.project_path=path; self.status.set(f'Project saved: {path}')
        except Exception as e: messagebox.showerror('Save failed',str(e))
    def open_project(self):
        path=filedialog.askopenfilename(filetypes=[('Vicky Album project','*.vkas'),('JSON','*.json')])
        if not path:return
        try:
            data=json.load(open(path,encoding='utf-8')); self.pages=data.get('pages') or self.pages; self.page_index=0; self.project_path=path; self.ps_path_var.set(data.get('ps_path','')); self.selected=None; self.draw_page(); self.status.set('Project opened.')
        except Exception as e: messagebox.showerror('Open failed',str(e))
    def new_project(self):
        if messagebox.askyesno('New project','Start a new album? Unsaved changes will be lost.'):
            self.pages=[{'size':'12x36','background':'#f6efe2','items':[]}]; self.page_index=0; self.selected=None; self.project_path=None; self.draw_page()
    def browse_ps(self):
        p=filedialog.askopenfilename(title='Select Photoshop CS3 executable',filetypes=[('Photoshop executable','Photoshop.exe'),('Executable','*.exe')])
        if p:self.ps_path_var.set(p)
    def open_photoshop(self):
        tmp=Path.home()/'VickyAlbumStudio_CurrentPage.jpg'
        try:
            self.render_page(self.page).save(tmp,'JPEG',quality=95,dpi=(300,300))
            ps=self.ps_path_var.get().strip()
            if ps and os.path.isfile(ps): subprocess.Popen([ps,str(tmp)])
            else:
                # Ask Windows to open the exported page with the system's default image app / Photoshop association.
                if sys.platform=='win32': os.startfile(str(tmp))
                else: subprocess.Popen(['xdg-open',str(tmp)])
                messagebox.showinfo('Photoshop CS3','Page JPG export ho gaya. Agar Photoshop CS3 default app nahi hai, Browse Photoshop EXE se Photoshop.exe select karein. JPG Photoshop mein ek flattened image ki tarah khulega.')
            self.status.set(f'Page exported for Photoshop: {tmp}')
        except Exception as e: messagebox.showerror('Photoshop launch failed',str(e))

if __name__=='__main__':
    root=tk.Tk(); app=AlbumStudio(root); root.mainloop()
