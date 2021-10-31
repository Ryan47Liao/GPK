import tkinter as tk
import random
from tkinter import messagebox

class Faller:
    def __init__(self):
        self.Types = {"O":{"Shape":[(-1, -1),(0, -1), (-1,0), (0,0)],"Color":"pink"},
                 "S":{"Shape":[(-1, 0), (0, 0), (0, -1), (1, -1)],"Color":"red"},
                 "T":{"Shape":[(-1, 0), (0, 0), (0, -1), (1, 0)],"Color":"yellow"},
                 "I":{"Shape":[(0, 1), (0, 0), (0, -1), (0, -2)],"Color":"green"},
                 "L":{"Shape":[(-1, 0), (0, 0), (-1, -1), (-1, -2)],"Color":"blue"},
                 "J":{"Shape":[(-1, 0), (0, 0), (0, -1), (0, -2)],"Color":"purple"},
                 "Z":{"Shape": [(-1, -1), (0, -1), (0, 0), (1, 0)],"Color":"Tan"}}
    
class Tetris:
    def __init__(self,master = None):
        if master is None:
            master = tk.Tk()
        self.size = 30
        self.Columns = 10
        self.Rows= 18
        self.Height = self.Rows * self.size
        self.Width = self.Columns * self.size
        self.score = tk.IntVar(master)
        self.score.set(0)
        self.frequency= 250
        self.current_faller = None
        self.blocks = []
        self.Fallers = Faller()
        self.Window = master
        self.canvas = tk.Canvas(self.Window, width = self.Width, height = self.Height)
        
    def draw_empty_blocks(self):
        for n in range(self.Rows):
            r = ["" for m in range(self.Columns)]
            self.blocks.append(r)
            
    def draw_blocks(self,canvas, column, row, color):
        x0 = column * self.size
        x1 = column * self.size + self.size
        y0 = row * self.size
        y1 = row * self.size + self.size
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline = "grey", width = 2)
        
    def draw_window(self,canvas):
        for x in range(self.Rows):
            for y in range(self.Columns):
                self.draw_blocks(self.canvas, y, x, "#000000")
            
    def fallers_generator(self) -> dict:
        faller_types = [i for i in self.Fallers.Types.keys()]
        Type = random.choice(faller_types)
        position = [self.Columns//2, 0]
        faller = {"Type": Type,
          "Position":position,
          "Shape":self.Fallers.Types[Type]["Shape"],
          "Color":self.Fallers.Types[Type]["Color"]}
        return faller
    
    def draw_clean_row(self, canvas, blocks):
        for x in range(self.Rows):
            for y in range(self.Columns):
                block = self.blocks[x][y]
                if block: self.draw_blocks(canvas, y, x, self.Fallers.Types[block]["Color"])
                else: self.draw_blocks(canvas, y, x, "#000000")
                
    def draw_fallers(self, canvas, column, row, faller, color):
        for i in faller:
            x,y = i
            n = x + column
            m = y + row
            if 0 <= column < self.Columns and 0 <= row < self.Rows: self.draw_blocks(canvas,n,m,color)
    
    def horizontal_move_faller(self,event):
        if current_faller is None: return
        direction = [0,0]
        if event.keysym == "Left": direction = [-1, 0]
        elif event.keysym == 'Right': direction = [1, 0]
        else: return
        if check_availablity(current_faller, direction):
            draw_fallers_move(self.canvas, current_faller, direction)
            
    def draw_fallers_move(self, canvas, faller, direction):
        faller_type = faller["Type"]
        column,row = faller["Position"]
        Shape = faller["Shape"]
        self.draw_fallers(self.canvas, column, row, Shape,"#000000")
        mc, mr = direction
        c_after, r_after = column + mc, row + mr
        faller["Position"] = [c_after, r_after]
        self.draw_fallers(self.canvas, c_after, r_after,Shape,faller["Color"])

    def check_availablity(self, faller, direction) -> bool:
        column,row = faller["Position"]
        Shape = faller["Shape"]
        i = 0
        while (i < len(Shape)):
            block = Shape[i]
            new_x = block[0] + column + direction[0]
            new_y = block[1] + row + direction[1]
            i += 1
            if new_x < 0 or new_x >= self.Columns or new_y >= self.Rows: return False
            if new_y >= 0 and self.blocks[new_y][new_x]: return False

        return True

    def save_faller(self, faller):
        Type = faller["Type"]
        x, y = faller["Position"]
        Shape = faller["Shape"]
        for item in Shape:
            new_x = x + item[0]
            new_y = y + item[1]
            self.blocks[new_y][new_x] = Type
            
    def horizontal_move_faller(self, event):
        direction = [0,0]
        if event.keysym == "Left": direction = [-1, 0]
        elif event.keysym == 'Right': direction = [1, 0]
        else: return
        if self.current_faller is not None and self.check_availablity(self.current_faller, direction):
            self.draw_fallers_move(self.canvas, self.current_faller, direction)

    def quick_fall(self, event):  
        if self.current_faller is None: return
        Shape = self.current_faller["Shape"]
        x, y = self.current_faller["Position"]
        limitation = self.Rows
        i = 0
        while (i < len(Shape)):
            item = Shape[i]
            new_x = x + item[0]
            new_y = y + item[1]
            i += 1
            if self.blocks[new_y][new_x]:
                return
            temp = 0
            for j in range(new_y+1, self.Rows):
                if self.blocks[j][new_x]: break
                else: temp += 1
            if temp < limitation: limitation = temp
        move = [0, limitation]
        if self.check_availablity(self.current_faller, move):
            self.draw_fallers_move(self.canvas, self.current_faller, move)
        
    def Rotate_faller(self, event):
        if self.current_faller is None:
            return
        Shape = self.current_faller["Shape"]
        After_rotated = []
        i = 0
        while (i < len(Shape)):
            item = Shape[i]
            item_x, item_y = item
            i += 1
            rotate = [item_y, -item_x]
            After_rotated.append(rotate)
        
        new_faller = {"Type": self.current_faller["Type"],
                      "Position":self.current_faller["Position"],
                      "Shape":After_rotated,
                      "Color":self.current_faller["Color"]}
    
        if self.check_availablity(new_faller,[0,0]):
            x,y = self.current_faller["Position"]
            self.draw_fallers(self.canvas, x, y, self.current_faller["Shape"], "#000000")
            self.draw_fallers(self.canvas, x, y, After_rotated, self.current_faller["Color"])
            self.current_faller = new_faller

    def check_row(self, row) -> bool:
        for i in row:
            if i == "":
                return False
        return True


    def update_score(self):
        self.score.forget()
    
    def clear_check(self):
        full = False
        for x in range(len(self.blocks)):
            if self.check_row(self.blocks[x]):
                full = True
                if x > 0:
                    for y in range(x, 0, -1):
                        self.blocks[y] = self.blocks[y-1][:]
                    self.blocks[0] = ["" for n in range(self.Columns)]
                else:
                    self.blocks[x] = ["" for n in range(self.Columns)]
                self.score.set(self.score.get()+1)
        if full:
            self.draw_clean_row(self.canvas, self.blocks)
            #self.Window.title("Score: %s" % self.score)
            
            
    def Game_update(self):
        self.Window.update()
        if self.current_faller is None:
            new = self.fallers_generator()
            self.current_faller = new
            self.draw_fallers_move(self.canvas, new, [0,0])
            if self.check_availablity(self.current_faller, [0, 0]) == False:
                messagebox.showinfo("Game Over!", "Your Score is %s" % self.score.get())
                self.Window.destroy()
                return
        else:
            if self.check_availablity(self.current_faller, [0, 1]):
                self.draw_fallers_move(self.canvas, self.current_faller, [0, 1])
            else:
                self.save_faller(self.current_faller)
                self.current_faller = None
                self.clear_check()
    
        self.Window.after(self.frequency, self.Game_update)

    def start_game(self):
        self.canvas.pack()
        self.draw_empty_blocks()
        self.draw_clean_row(self.canvas, self.blocks)
        self.canvas.focus_set() 
        self.canvas.bind("<KeyPress-Left>", self.horizontal_move_faller)
        self.canvas.bind("<KeyPress-Right>", self.horizontal_move_faller)
        self.canvas.bind("<KeyPress-Up>", self.Rotate_faller)
        self.canvas.bind("<KeyPress-Down>", self.quick_fall)
        #self.Window.title("Score: %s" % self.score)
        self.score_board = tk.Label(master = self.Window,  textvariable = self.score )
        self.score_board.pack()
        #________EXE________#
        self.Window.update()
        self.Window.after(self.frequency, self.Game_update)
        self.Window.mainloop()

if __name__=="__main__":
    Game = Tetris()
    Game.start_game()
