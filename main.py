# main.py
import sys
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from lexer import Lexer
from parser import Parser, Assign, Print, Block
from interpreter import Interpreter


class EditorWindow:
    """独立的编辑窗口"""
    def __init__(self, parent, file_path=None):
        self.parent = parent
        self.file_path = file_path

        self.window = tk.Toplevel(parent.root)
        self.window.title("happyfriskyo Editor")
        self.window.geometry("600x400")

        self.editor = scrolledtext.ScrolledText(
            self.window,
            wrap=tk.WORD,
            font=('Consolas', 12),
            bg='white',
            fg='black'
        )
        self.editor.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        if file_path and file_path.endswith('.hp'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.insert(1.0, content)
                self.window.title(f"happyfriskyo Editor - {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot load file:\n{e}")

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=5)

        save_btn = tk.Button(btn_frame, text="💾 Save", command=self.save_file,
                             bg='#4CAF50', fg='white', padx=10)
        save_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(btn_frame, text="✖ Close", command=self.close_window,
                              bg='#f44336', fg='white', padx=10)
        close_btn.pack(side=tk.LEFT, padx=5)

        self.editor.bind('<Control-s>', lambda e: self.save_file())
        self.parent.set_current_editor(self)

    def save_file(self):
        content = self.editor.get(1.0, tk.END).strip()
        if not self.file_path:
            file_path = filedialog.asksaveasfilename(
                title="Save happyfriskyo file",
                defaultextension=".hp",
                filetypes=[("happyfriskyo files", "*.hp"), ("All files", "*.*")]
            )
            if not file_path:
                return
            self.file_path = file_path
            self.window.title(f"happyfriskyo Editor - {file_path}")
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.parent.set_current_file(self.file_path)
            messagebox.showinfo("Saved", f"File saved:\n{self.file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def close_window(self):
        self.parent.clear_current_editor()
        self.window.destroy()


class HappyFriskyoMain:
    def __init__(self, root, file_to_open=None):
        self.root = root
        self.root.title("happyfriskyo REPL")
        self.root.geometry("750x600")
        self.root.configure(bg='#f0f0f0')

        self.current_file = None
        self.current_editor = None
        self.interpreter = Interpreter()

        self.output = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            state='disabled',
            font=('微软雅黑', 11),
            bg='white',
            fg='black'
        )
        self.output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.output.tag_configure("prompt", foreground="#2E8B57")
        self.output.tag_configure("result", foreground="#1E90FF")
        self.output.tag_configure("error", foreground="#FF0000")
        self.output.tag_configure("info", foreground="#888888")

        toolbar = tk.Frame(root, bg='#e0e0e0', height=35)
        toolbar.pack(fill=tk.X, padx=2, pady=2)

        btn_kw = {
            'font': ('微软雅黑', 10),
            'fg': 'white',
            'padx': 10,
            'pady': 2,
            'relief': tk.RAISED,
            'bd': 1
        }

        btn_new = tk.Button(toolbar, text="📄 New File", command=self.new_file,
                            bg='#4CAF50', **btn_kw)
        btn_new.pack(side=tk.LEFT, padx=2)

        btn_open = tk.Button(toolbar, text="📂 Open", command=self.open_file,
                             bg='#2196F3', **btn_kw)
        btn_open.pack(side=tk.LEFT, padx=2)

        btn_save = tk.Button(toolbar, text="💾 Save", command=self.save_current_file,
                             bg='#FF9800', **btn_kw)
        btn_save.pack(side=tk.LEFT, padx=2)

        btn_run = tk.Button(toolbar, text="▶ Run File", command=self.run_file,
                            bg='#4CAF50', **btn_kw)
        btn_run.pack(side=tk.LEFT, padx=2)

        self.status_label = tk.Label(toolbar, text="No file", bg='#e0e0e0',
                                     font=('微软雅黑', 9), anchor='w')
        self.status_label.pack(side=tk.RIGHT, padx=10)

        input_frame = tk.Frame(root, bg='#f0f0f0')
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.prompt_label = tk.Label(
            input_frame,
            text=">>> ",
            font=('微软雅黑', 12, 'bold'),
            bg='#f0f0f0',
            fg='#2E8B57'
        )
        self.prompt_label.pack(side=tk.LEFT, anchor='nw', padx=(0, 5), pady=(5, 0))

        self.input_area = tk.Text(
            input_frame,
            font=('微软雅黑', 12),
            bg='white',
            fg='black',
            height=4,
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            bd=2
        )
        self.input_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(5, 0))
        self.input_area.bind('<Control-Return>', self.execute_repl)
        self.input_area.focus_set()

        self.run_button = tk.Button(
            input_frame,
            text="Run (Ctrl+Enter)",
            font=('微软雅黑', 10),
            bg='#4CAF50',
            fg='white',
            command=self.execute_repl
        )
        self.run_button.pack(side=tk.RIGHT, padx=(5, 0), pady=(5, 0))

        self.display_output("happyfriskyo REPL + File Editor\n", "info")
        self.display_output("Use New File to open an editor, write code, then Save.\n", "info")
        self.display_output("You can also type code directly in the input box (Ctrl+Enter).\n", "info")
        self.display_output("-" * 50 + "\n", "info")

        if file_to_open and file_to_open.endswith('.hp'):
            self.current_file = file_to_open
            self.status_label.config(text=file_to_open.split('/')[-1])
            self.open_editor(file_to_open)
            self.display_output(f"Loaded file: {file_to_open}\n", "info")

    # ---------- 编辑器管理 ----------
    def set_current_editor(self, editor):
        self.current_editor = editor

    def clear_current_editor(self):
        self.current_editor = None

    def open_editor(self, file_path=None):
        editor = EditorWindow(self, file_path)
        if file_path:
            self.set_current_file(file_path)
        return editor

    # ---------- 显示输出 ----------
    def display_output(self, text, tag=None):
        self.output.config(state='normal')
        if tag:
            self.output.insert(tk.END, text, tag)
        else:
            self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state='disabled')

    # 移除了 clear_output()，不再清空输出

    def set_current_file(self, file_path):
        self.current_file = file_path
        if file_path:
            self.status_label.config(text=file_path.split('/')[-1])
        else:
            self.status_label.config(text="No file")

    # ---------- 按钮功能 ----------
    def new_file(self):
        self.open_editor()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open happyfriskyo file",
            filetypes=[("happyfriskyo files", "*.hp"), ("All files", "*.*")]
        )
        if not file_path:
            return
        self.open_editor(file_path)

    def save_current_file(self):
        if self.current_editor:
            self.current_editor.save_file()
        else:
            self.open_editor(self.current_file)

    def run_file(self):
        """运行当前文件（保留历史输出，每次运行添加分隔线）"""
        if not self.current_file:
            messagebox.showwarning("No file", "Please create or open a file first, and save it.")
            return

        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read file:\n{e}")
            return

        # 添加分隔线，标识新一次运行
        self.display_output("\n" + "=" * 50 + "\n", "info")
        self.display_output(f"Running: {self.current_file}\n", "info")
        self.display_output("-" * 40 + "\n", "info")

        interpreter = Interpreter()
        try:
            lexer = Lexer(content)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse_program()
            result = interpreter.eval(ast)

            # 输出结果（根据AST类型判断）
            if isinstance(ast, Block):
                if ast.statements:
                    last_stmt = ast.statements[-1]
                    if isinstance(last_stmt, Print):
                        if result is not None:
                            self.display_output(f"{result}\n", "result")
                    elif not isinstance(last_stmt, Assign):
                        if result is not None:
                            self.display_output(f"{result}\n", "result")
            else:
                if isinstance(ast, Print):
                    if result is not None:
                        self.display_output(f"{result}\n", "result")
                elif not isinstance(ast, Assign):
                    if result is not None:
                        self.display_output(f"{result}\n", "result")

            self.display_output("--- Execution finished ---\n", "info")
        except Exception as e:
            self.display_output(f"Error: {e}\n", "error")

    def execute_repl(self, event=None):
        code = self.input_area.get("1.0", tk.END).strip()
        if not code:
            return
        self.input_area.delete("1.0", tk.END)

        lines = code.split('\n')
        self.display_output(">>> " + lines[0] + "\n", "prompt")
        for line in lines[1:]:
            self.display_output("... " + line + "\n", "prompt")

        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse_program()
            result = self.interpreter.eval(ast)

            if isinstance(ast, Block) and ast.statements:
                last_stmt = ast.statements[-1]
                if isinstance(last_stmt, Print):
                    if result is not None:
                        self.display_output(f"{result}\n", "result")
                elif not isinstance(last_stmt, Assign):
                    if result is not None:
                        self.display_output(f"{result}\n", "result")
            elif isinstance(ast, Print):
                if result is not None:
                    self.display_output(f"{result}\n", "result")
            elif not isinstance(ast, Assign):
                if result is not None:
                    self.display_output(f"{result}\n", "result")
        except Exception as e:
            self.display_output(f"Error: {e}\n", "error")


def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if filename.endswith('.hp'):
            root = tk.Tk()
            app = HappyFriskyoMain(root, file_to_open=filename)
            root.mainloop()
        else:
            print("Please specify a .hp file", file=sys.stderr)
            sys.exit(1)
    else:
        root = tk.Tk()
        app = HappyFriskyoMain(root)
        root.mainloop()

if __name__ == "__main__":
    main()