# convert-pdf-to-word

Web server chạy trong mạng LAN để upload PDF và convert sang Word ngay trên máy nội bộ.

## Cách chạy

1. Mở PowerShell tại thư mục project.
2. Chạy:

```powershell
.\run_server.ps1
```

Mặc định server sẽ:

- lắng nghe trên `0.0.0.0:8080`
- dùng engine `pdf2docx`
- in ra các URL LAN để máy khác trong cùng mạng truy cập

Ví dụ đổi port:

```powershell
.\run_server.ps1 -Port 8090
```

## Truy cập từ máy khác trong LAN

- Mở URL mà script in ra, ví dụ `http://192.168.1.10:8080`
- Nếu máy khác không vào được, chạy PowerShell `Run as Administrator` rồi mở firewall:

```powershell
.\open_firewall.ps1 -Port 8080
```

## Engine convert

- `pdf2docx`: mặc định, chạy ổn định trên máy này
- `word`: tùy chọn, dùng Microsoft Word automation; chất lượng có thể tốt hơn với một số PDF nhưng có thể phụ thuộc môi trường Office

Ví dụ chạy bằng Word engine:

```powershell
.\run_server.ps1 -ConverterEngine word
```
