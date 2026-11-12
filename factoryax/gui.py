"""Small offline owner GUI, stdlib Tkinter only. No network/service calls."""
from __future__ import annotations

from pathlib import Path


def launch() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from .delivery import run
    from .verify import IntakeError

    root = tk.Tk()
    root.title('Factory AX VERIFY | 오프라인 검수 후보')
    root.geometry('780x460')
    root.minsize(540, 380)
    root.columnconfigure(1, weight=1)
    spec = tk.StringVar()
    output = tk.StringVar()
    summary = tk.StringVar(value='파일 선택 → 승인된 설정 JSON 선택 → 새 보고 폴더 지정 → 검수 실행')
    ttk.Label(root, text='Factory AX VERIFY | 내부 시험용 · RELEASE HOLD', font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=3, sticky='w', padx=20, pady=16)
    ttk.Label(root, text='검수 설정 JSON').grid(row=1, column=0, sticky='w', padx=20, pady=10)
    ttk.Entry(root, textvariable=spec).grid(row=1, column=1, sticky='ew', padx=6)
    ttk.Button(root, text='선택', command=lambda: spec.set(filedialog.askopenfilename(filetypes=[('JSON', '*.json')]))).grid(row=1, column=2, padx=15)
    ttk.Label(root, text='새 보고 폴더').grid(row=2, column=0, sticky='w', padx=20, pady=10)
    ttk.Entry(root, textvariable=output).grid(row=2, column=1, sticky='ew', padx=6)
    def choose_output_parent():
        chosen = filedialog.askdirectory()
        if chosen:  # Cancel must not silently select '/FactoryAX-New-Report'.
            output.set(str(Path(chosen) / 'FactoryAX-New-Report'))

    ttk.Button(root, text='상위 폴더 선택', command=choose_output_parent).grid(row=2, column=2, padx=15)
    result_box = tk.Text(root, height=9, wrap='word', state='disabled')
    result_box.grid(row=4, column=0, columnspan=3, sticky='nsew', padx=20, pady=12)
    root.rowconfigure(4, weight=1)

    def submit():
        if not spec.get() or not output.get():
            messagebox.showwarning('입력 필요', '승인된 설정과 새 보고 폴더를 선택하세요.')
            return
        try:
            result = run(spec.get(), output.get())
            text = f"검수: {result['status']}\n추가 확인: {result['findings']}\n출력: {result['output']}\n"
            summary.set('검수 기록 생성. 사람 확인·Windows 실기기 검증과 납품 승인은 별도입니다.')
        except (IntakeError, OSError, ValueError, TypeError, KeyError) as exc:
            text = f"BLOCKED: {exc if isinstance(exc, IntakeError) else 'INVALID_LOCAL_INPUT_OR_IO'}\n기존 결과는 덮어쓰지 않습니다.\n"
            summary.set('BLOCKED: 출력 또는 입력을 확인한 뒤 별도의 새 폴더로 재시도하세요.')
        result_box.configure(state='normal')
        result_box.delete('1.0', 'end')
        result_box.insert('end', text)
        result_box.configure(state='disabled')

    ttk.Button(root, text='읽기 전용 검수 실행', command=submit).grid(row=3, column=0, columnspan=3, pady=12)
    ttk.Label(root, textvariable=summary, wraplength=690).grid(row=5, column=0, columnspan=3, sticky='w', padx=20, pady=12)
    root.mainloop()
