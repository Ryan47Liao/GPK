import tkinter as tk

class tkLIST(tk.Frame):
    def __init__(self,master, base_row = 0, base_col = 0, 
                 n = 7, header = None, 
                 show_sub = False,view_frame = None,TEXT = None,
                  **cnf):
        tk.Frame.__init__(self,master)
        self.root = master 
        self.config(cnf)
        self.LISTBOXes = []
        self.show_sub = show_sub 
        self.view_frame = view_frame
        self.base_row = base_row
        self.base_col = base_col
        if TEXT is None:
            self.TEXT_Create = True
        else:
            self.TEXT_Create = False
            self.TEXT = TEXT
        
        self.header = header
        self._draw(n, header)

    def LB_Clear(self):
        for listbox in self.LISTBOXes:
            listbox.delete(0,tk.END)
        
    def SetLists(self,n, header = None):
        if header is None:
            header = [i for i in range(n)]
        assert len(header) == n, 'The length of the header must match n'
        #Construction 
        for i in range(n):
            exec(f"self.listbox{i} = tk.Listbox(self.root) ")
            self.LISTBOXes.append(eval(f"self.listbox{i}"))
        #Positioning 
        col = self.base_col
        for listbox in self.LISTBOXes:
            listbox.config(height = 15, width = 13, font = ('times new roman',14))
            label = tk.Label(self.root,text = header[col])  
            
            #self.INSERT(col, [f"Task {i}" for i in range(15)]) 
            col += 1 
            
            label.grid(row = 0 + self.base_row, column = col)
            listbox.grid(row = 1 + self.base_row, column = col)
            
    def INSERT(self,header,list_of_items):
        'Insert a list of items under the corresponding header'
        list_idx = list(self.header).index(header)
        for item in list_of_items:
            self.LISTBOXes[list_idx].insert( tk.END, item)
            
    def retrieve(self):
        SELECTION = [listbox.curselection() for listbox in self.LISTBOXes]
        day = [ idx+1 for idx in range(len(SELECTION)) if SELECTION[idx] != () ][0]
        print(SELECTION)
        temp = [lb.get(idx) for lb,idx in zip(self.LISTBOXes,SELECTION) if  idx != ()]
        selected_id= f"day {day-1}:{temp[0]}"
        self.selected.set(selected_id)
        return selected_id

        
    def Text_refresh(self,text):
        self.TEXT.delete("1.0","end")
        self.TEXT.insert("1.0", text)
    
    def _draw(self,n, header):
        self.SetLists(n, header)
        #Lower Frame
        if self.view_frame is None:
            self.view_frame = tk.Frame(self.root ,bg = 'pink')
            self.view_frame.grid(row = self.base_row + 2, column = self.base_col+ 5)
        self.selected = tk.StringVar()
        self.selected.set("Select and Submit to update")
        if self.show_sub:
            if self.TEXT_Create:
                self.lab_s = tk.Label(self.view_frame,
                                      textvar = self.selected,
                                      font = ('times new roman',16))
                self.lab_s.pack()
                self.TEXT = tk.Text(self.view_frame,height = 10,
                                    width = 70, bg = "light cyan")
                self.TEXT.configure(font=("Times New Roman", 14, "bold"))
                self.TEXT.pack()
            
            
                
if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("1000x500")
    LIST = tkLIST(root, bg = 'green',show_sub = False , n =4, 
                  header = ['Health','Family','Personal_Dev','Career'])
    
    root.mainloop()