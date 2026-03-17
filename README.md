# convert-pdf-to-word

Web server chạy trong mạng LAN để upload PDF và convert sang Word ngay trên máy nội bộ.

Repo này chỉ giữ phần runtime chính. File DOCX sinh ra trong lúc test/convert sẽ không được lưu lại trong source tree.

## Cách chạy

1. Mở PowerShell tại thư mục project.
2. Chạy:

```powershell
.\run_server.ps1
```

Mặc định server sẽ:

- lắng nghe trên `0.0.0.0:8080`
- dùng engine `auto` để ưu tiên Microsoft Word rồi fallback sang `pdf2docx`
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

- `auto`: mặc định, ưu tiên `word` để giữ header/footer và bố cục tốt hơn, sau đó fallback sang `pdf2docx`
- `pdf2docx`: phù hợp khi không muốn phụ thuộc Microsoft Word, nhưng với PDF phức tạp thì header/footer có thể lệch hơn
- `word`: dùng Microsoft Word automation; thường giữ layout tốt hơn với PDF có header/footer, nhưng phụ thuộc môi trường Office

Ví dụ chạy bằng Word engine:

```powershell
.\run_server.ps1 -ConverterEngine word
```
